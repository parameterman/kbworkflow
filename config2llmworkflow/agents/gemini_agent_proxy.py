import re
import json
import time
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from config2llmworkflow.agents.base import BaseAgentProxy

import logging

logger = logging.getLogger(__name__)

from config2llmworkflow.utils.python_interpreter import PythonInterpreter


class GeminiAgentProxy(BaseAgentProxy):

    def _init_client(self):

        import google.generativeai as genai

        genai.configure(api_key=self.config.api_key)

        self.client = genai.GenerativeModel(
            model_name=self.config.model,
            tools="code_execution" if not self.config.disable_python_run else None,
        )

    def _query(self, messages: List[Dict[str, str]]) -> str:

        new_query = messages[-1]["content"]
        chat_his = messages[:-1]

        print(f"{new_query=}")
        print(f"{chat_his=}")

        chat = self.client.start_chat(history=chat_his)

        response = chat.send_message(new_query)

        logger.info(f"Response: {response.text}")

        messages.append(
            {
                "role": "model",
                "content": response.text,
            }
        )

        return response.text

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
            {"role": "model", "content": self.full_role + "\n" + self.full_prompt},
        ]

        if not self.config.disable_python_run:
            messages[-1][
                "content"
            ] += """
如果你觉得有必要计算，那么你可以通过生成python代码来计算
"""
        #         messages[-1][
        #             "content"
        #         ] += f"""
        # 请你生成确定的正式结果时，生成json格式，使用```json\n```包裹，产生的变量信息如下；
        # {self.config.output_vars}
        # """

        tmp = self._query(messages)
        # log
        self.node_log["messages"] = messages

        # if not self.config.disable_python_run:
        #     interpreter = PythonInterpreter(tmp)
        #     while interpreter.include_python_code():
        #         interpreter.run_python_code()
        #         new_prompt = f"我调用Python的运行结果是：{interpreter.result}"
        #         messages.extend(
        #             [
        #                 {"role": "model", "content": new_prompt},
        #                 {
        #                     "role": "user",
        #                     "content": "请你结合python计算结果继续给出回答。如果运行结果报错，那么请修复代码。如果运行成功，那么请你最好直接给出答案，不要啰嗦",
        #                 },
        #             ]
        #         )

        #         tmp = self._query(messages).strip()
        #         self.node_log["messages"] = messages

        #         interpreter = PythonInterpreter(tmp)

        output_vars = tmp

        logger.debug(f"GeminiAgentProxy {self.config.output_vars=}")
        logger.debug(f"GeminiAgentProxy {output_vars=}")

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
            logger.warning(f"Error parsing json: {e}")

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
