from typing import Dict, Any
from abc import ABC, abstractmethod
from GeneralAgent import Agent
from config2llmworkflow.configs.agents.base import BaseAgentProxyConfig


class BaseAgentProxy(ABC):

    def __init__(self, config: BaseAgentProxyConfig):
        self.config = config

    @abstractmethod
    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def __call__(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        return self.run(input_vars)


class AgentProxy(BaseAgentProxy):

    def __init__(self, config: BaseAgentProxyConfig):
        super().__init__(config)

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        role = self.config.role.format(**input_vars)
        # print(f"Role: {role}")
        prompt = self.config.prompt.format(**input_vars)
        # print(f"Prompt: {prompt}")

        # 运行智能体
        agent = Agent(
            role=role,
            model=self.config.model,
            token_limit=self.config.token_limit,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            workspace=self.config.workspace,
            continue_run=self.config.continue_run,
        )

        output_vars = agent.run(prompt)

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

        return output_vars  # 修复：添加返回语句
