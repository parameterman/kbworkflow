from typing import Dict, Any, List
from abc import ABC, abstractmethod
from GeneralAgent import Agent
import sys
import re
from config2llmworkflow.configs.agents.base import BaseAgentProxyConfig

import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


class BaseAgentProxy(ABC):

    answer: Dict[str, Any] = {}
    full_role: str = ""
    full_prompt: str = ""
    messages: List[Dict[str, str]] = []

    def __init__(self, config: BaseAgentProxyConfig):
        self.config = config

    @abstractmethod
    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def __call__(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        return self.run(input_vars)

    def to_dict(self):
        return {
            "config": self.config.model_dump(),
            "full_role": self.full_role,
            "full_prompt": self.full_prompt,
            "answer": self.answer,
        }


class GenralAgentProxy(BaseAgentProxy):

    def __init__(self, config: BaseAgentProxyConfig):
        super().__init__(config)

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        logger.info(f"Setting input variables: {input_vars}")
        self.full_role = self.config.role.format(**input_vars)
        logger.info(f"Setting role: {self.full_role}")
        self.full_prompt = self.config.prompt.format(**input_vars)
        logger.info(f"Setting prompt: {self.full_prompt}")

        # 运行智能体
        agent = Agent(
            role=self.full_role,
            model=self.config.model,
            token_limit=self.config.token_limit,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            frequency_penalty=self.config.frequency_penalty,
            temperature=self.config.temperature,
            workspace=self.config.workspace,
            continue_run=self.config.continue_run,
            disable_python_run=self.config.disable_python_run,
        )

        output_vars = agent.run(self.full_prompt)

        # reflect
        for i in range(self.config.reflect_times):
            output_vars = agent.run("请你再仔细反思一下结果，重新给出更优的回答")

        if isinstance(output_vars, str) and len(self.config.output_vars) == 1:
            output_vars = {self.config.output_vars[0]["name"]: output_vars}
        elif isinstance(output_vars, dict):
            output_vars = {
                var["name"]: output_vars.get(var["name"], "")
                for var in self.config.output_vars
            }
        else:
            raise ValueError("Invalid output variables")

        if self.config.clean_memory:
            agent.clear()

        self.answer = output_vars
        logger.info(f"Setting answer: {self.answer}")

        return output_vars  # 修复：添加返回语句


class TogetherAgentProxy(BaseAgentProxy):

    def __init__(self, config: BaseAgentProxyConfig):
        super().__init__(config)

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        logger.info(f"Setting input variables: {input_vars}")
        self.full_role = self.config.role.format(**input_vars)
        logger.info(f"Setting role: {self.full_role}")
        self.full_prompt = self.config.prompt.format(**input_vars)
        logger.info(f"Setting prompt: {self.full_prompt}")

        from together import Together

        client = Together(api_key=self.config.api_key)

        response = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.full_role},
                {"role": "user", "content": self.full_prompt},
            ],
            max_tokens=self.config.token_limit,
            temperature=self.config.temperature,
            top_p=0.7,
            top_k=50,
            repetition_penalty=self.config.frequency_penalty,
            stop=["<|eot_id|>"],
            stream=False,
        )

        output_vars = response.choices[0].message.content

        if isinstance(output_vars, str) and len(self.config.output_vars) == 1:
            output_vars = {self.config.output_vars[0]["name"]: output_vars}
        elif isinstance(output_vars, dict):
            output_vars = {
                var["name"]: output_vars.get(var["name"], "")
                for var in self.config.output_vars
            }

        self.answer = output_vars

        return output_vars


"""
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)
"""


class OpenaiAgentProxy(BaseAgentProxy):

    def __init__(self, config: BaseAgentProxyConfig):
        super().__init__(config)

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        logger.info(f"Setting input variables: {input_vars}")
        self.full_role = self.config.role.format(**input_vars)
        logger.info(f"Setting role: {self.full_role}")
        self.full_prompt = self.config.prompt.format(**input_vars)
        logger.info(f"Setting prompt: {self.full_prompt}")

        from openai import OpenAI

        client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

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

        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            frequency_penalty=self.config.frequency_penalty,
            max_tokens=self.config.token_limit,
            temperature=self.config.temperature,
            top_p=0.7,
        )

        tmp = response.choices[0].message.content

        if not self.config.disable_python_run:
            interpreter = _PythonInterpreter(tmp)
            while interpreter.include_python_code():
                interpreter.run_python_code()
                new_prompt = f"计算结果是：{interpreter.result}"
                messages.extend(
                    [
                        {"role": "assistant", "content": new_prompt},
                        {"role": "user", "content": "请你根据代码运行结果继续回答"},
                    ]
                )

                response = client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    frequency_penalty=self.config.frequency_penalty,
                    max_tokens=self.config.token_limit,
                    temperature=self.config.temperature,
                    top_p=0.7,
                )

                tmp = response.choices[0].message.content
                interpreter = _PythonInterpreter(tmp)

        self.messages = messages

        output_vars = tmp

        if isinstance(output_vars, str) and len(self.config.output_vars) == 1:
            output_vars = {self.config.output_vars[0]["name"]: output_vars}
        elif isinstance(output_vars, dict):
            output_vars = {
                var["name"]: output_vars.get(var["name"], "")
                for var in self.config.output_vars
            }

        self.answer = output_vars

        return output_vars


class _PythonInterpreter:
    code_pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
    code: str = None
    result: str = None

    def __init__(self, text: str):
        self.text = text

    def include_python_code(self):
        # 找到python代码，如果有则返回代码，没有则返回None
        match = self.code_pattern.search(self.text)
        if match:
            self.code = match.group(1)
            return self.code
        return None

    def run_python_code(self):
        if self.code is None:
            logger.error("No code to run")
            return None

        logger.info(f"Running Python code: {self.code}")

        try:
            # 开启进程，使用python运行代码
            result = subprocess.run(
                [sys.executable, "-c", self.code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            # 获取输出
            self.result = result.stdout
            logger.info(f"Python code output: {self.result}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running Python code: {e.stderr}")
            self.result = e.stderr

        return self.result
