import re
import json
import time
from functools import lru_cache
from typing import Dict, Any, Optional
from config2llmworkflow.agents.base import BaseAgentProxy
from config2llmworkflow.agents.agent_tools import (
    tool_name_to_func_map,
    tool_name_to_schema_map,
)

import logging

logger = logging.getLogger(__name__)

from config2llmworkflow.utils.python_interpreter import PythonInterpreter


class OpenaiAgentProxy(BaseAgentProxy):

    def _init_client(self):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

    def _query(self, messages):
        from openai import NotGiven

        # 从 tool_name_to_schema_map 中获取工具的 schema
        tools = [tool_name_to_schema_map[tool_name] for tool_name in self.config.tools]

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            frequency_penalty=self.config.frequency_penalty,
            max_tokens=self.config.token_limit,
            temperature=self.config.temperature,
            # response_format={"type": "json_object"},
            top_p=0.7,
            tools=tools if tools else NotGiven(),
        )

        if tools:
            try:
                tool_call = response.choices[0].message.tool_calls[0]
            except Exception as e:
                logger.error(f"Error parsing tool call: {e}")
                tool_call = None
        else:
            tool_call = None

        if response.choices[0].message.content:

            messages.append(
                {
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                }
            )

        return response.choices[0].message.content, tool_call

    def run(
        self, input_vars: Dict[str, Any], watchdog_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        logger.info(f"Setting input variables for {self.config.name}: {input_vars}")
        self.full_role = self.config.role.format(**input_vars)
        logger.info(f"Setting role for {self.config.name}: {self.full_role}")
        self.full_prompt = self.config.prompt.format(**input_vars)
        logger.info(f"Setting prompt for {self.config.name}: {self.full_prompt}")

        self._init_client()

        messages = [
            {"role": "system", "content": self.full_role},
            {"role": "user", "content": self.full_prompt},
        ]

        if not self.config.disable_python_run:
            messages[-1][
                "content"
            ] += """
如果你认为需要先通过生成python代码进行计算，那么你可以扮演一个Python计算专家，你可以先输出python代码,格式如下:
```python
# main python code
```
其中的变量名请使用英文，并且符合python变量命名规范。
python代码的最终终端输出结果将被用于后续的回答。
在最后一定要用print()输出结果。
"""
        #         messages[-1][
        #             "content"
        #         ] += f"""
        # 请你生成确定的正式结果时，生成json格式，使用```json\n```包裹，产生的变量信息如下；
        # {self.config.output_vars}
        # """

        tmp, tool_call = self._query(messages)

        if tool_call:
            name = tool_call.function.name
            arguments = tool_call.function.arguments

            # log 当前 agent 选择的函数和参数
            if "tool_call" not in self.node_log:
                self.node_log["tool_call"] = []
            self.node_log["tool_call"].append(
                {
                    "name": name,
                    "arguments": arguments,
                }
            )

            logger.info(
                f"[{self.config.name}] 调用了工具 {name}，参数是 {arguments}, 参数类型是 {type(arguments)}"
            )

            if name in tool_name_to_func_map:
                func = tool_name_to_func_map[name]
                # try json
                try:
                    arguments = json.loads(arguments)
                except:
                    logger.warning(
                        f"[{self.config.name}] 参数 {arguments} 不是json格式，无法解析"
                    )
                    pass
                tmp = func(**arguments)
                logger.info(f"[{self.config.name}] 调用工具 {name} 的结果是 {tmp}")
                messages.extend(
                    [
                        {
                            "role": "assistant",
                            "content": f"我调用了工具{name}, 参数是{arguments}, 结果是{tmp}",
                        },
                    ]
                )

                # logger.info(f"messages: {messages}")

                # # send messages to chatgpt
                # tmp, tool_call = self._query(messages)

        # log
        self.node_log["messages"] = messages

        if not self.config.disable_python_run:
            interpreter = PythonInterpreter(tmp)
            while interpreter.include_python_code():
                interpreter.run_python_code()
                new_prompt = f"我调用Python的运行结果是：{interpreter.result}"
                messages.extend(
                    [
                        {"role": "assistant", "content": new_prompt},
                        {
                            "role": "user",
                            "content": "请你结合python计算结果继续给出回答。如果运行结果报错，那么请修复代码。如果运行成功，那么请你最好直接给出答案，不要啰嗦",
                        },
                    ]
                )

                tmp, tool_call = self._query(messages)
                self.node_log["messages"] = messages

                interpreter = PythonInterpreter(tmp)

        output_vars = messages[-1]["content"]

        logger.debug(
            f"[{self.config.name}] OpenaiAgentProxy {self.config.output_vars=}"
        )
        logger.debug(f"[{self.config.name}] OpenaiAgentProxy {output_vars=}")

        # try:
        #     # 获取 ```json ```里的内容
        #     json_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

        #     match = json_pattern.search(output_vars)
        #     if match:
        #         output_vars = match.group(1)
        #         output_vars = json.loads(output_vars)
        #     # 如果没有match，则直接使用 json.loads
        #     else:
        #         output_vars = json.loads(output_vars)
        # except Exception as e:
        #     logger.warning(f"Error parsing json: {e}")

        if isinstance(output_vars, str) and len(self.config.output_vars) == 1:
            output_vars = {self.config.output_vars[0].name: output_vars}

        elif isinstance(output_vars, dict):
            output_vars = {
                var.name: output_vars.get(var.name, "")
                for var in self.config.output_vars
            }
        else:
            raise ValueError(
                f"Invalid output variables: {output_vars}, expected output_vars: {self.config.output_vars}"
            )

        self.answer = output_vars

        logger.info(f"Running exec")
        exec(f"{self.config.name}_messages = self.node_log['messages']")
        # 添加到 output_vars
        exec(
            f"output_vars['{self.config.name}_messages'] = {self.config.name}_messages"
        )

        logger.debug(f"[{self.config.name}] type of output_vars: {type(output_vars)}")
        logger.info(f"[{self.config.name}] output_vars: {output_vars}")

        return output_vars
