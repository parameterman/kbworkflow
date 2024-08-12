from typing import Dict, Any
from config2llmworkflow.agents.base import BaseAgentProxy

import logging

logger = logging.getLogger(__name__)


class GeneralAgentProxy(BaseAgentProxy):

    def _init_client(self):
        from GeneralAgent import Agent

        self.agent = Agent(
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

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        logger.info(f"Setting input variables: {input_vars}")
        self.full_role = self.config.role.format(**input_vars)
        logger.info(f"Setting role: {self.full_role}")
        self.full_prompt = self.config.prompt.format(**input_vars)
        logger.info(f"Setting prompt: {self.full_prompt}")

        # 运行智能体
        self.agent.role = self.full_role

        output_vars = self.agent.run(self.full_prompt)

        # reflect
        for i in range(self.config.reflect_times):
            output_vars = self.agent.run("请你再仔细反思一下结果，重新给出更优的回答")

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
            self.agent.clear()

        self.answer = output_vars
        logger.info(f"Setting answer: {self.answer}")

        return output_vars  # 修复：添加返回语句
