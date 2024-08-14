import re
import json
import time
from typing import Dict, Any, Optional
from config2llmworkflow.agents.base import BaseAgentProxy

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
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            frequency_penalty=self.config.frequency_penalty,
            max_tokens=self.config.token_limit,
            temperature=self.config.temperature,
            response_format={"type": "json_object"},
            top_p=0.7,
        )

        messages.append(
            {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
        )

        return response.choices[0].message.content

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
如果你认为需要先通过生成python代码进行计算，你可以先输出python代码,格式如下:
```python
# main python code
```
"""
        messages[-1][
            "content"
        ] += f"""
请你生成确定的正式结果时，生成json格式，使用```json\n```包裹，产生的变量信息如下；
{self.config.output_vars}
"""

        tmp = self._query(messages)
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
                            "content": "请你结合python计算结果继续给出回答",
                        },
                    ]
                )

                tmp = self._query(messages)
                self.node_log["messages"] = messages

                interpreter = PythonInterpreter(tmp)

        output_vars = tmp.strip()

        logger.debug(f"OpenaiAgentProxy {self.config.output_vars=}")
        logger.debug(f"OpenaiAgentProxy {output_vars=}")

        try:
            # 获取 ```json ```里的内容
            json_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)

            match = json_pattern.search(output_vars)
            if match:
                output_vars = match.group(1)
                output_vars = json.loads(output_vars)
            # 如果没有match，则直接使用 json.loads
            else:
                output_vars = json.loads(output_vars)
        except Exception as e:
            logger.error(f"Error parsing json: {e}")

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

        logger.debug(f"type of output_vars: {type(output_vars)}")
        logger.debug(f"output_vars: {output_vars}")

        return output_vars
