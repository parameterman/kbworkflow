from typing import List, Dict, Any
from abc import ABC, abstractmethod
import concurrent.futures
import os

from config2llmworkflow.configs.workflows.base import BaseWorkflowConfig
from config2llmworkflow.agents.base import (
    GenralAgentProxy,
    BaseAgentProxy,
    TogetherAgentProxy,
    OpenaiAgentProxy,
)

import logging

logger = logging.getLogger(__name__)


# 定义一个全局函数以供多线程使用
def run_agent(agent: GenralAgentProxy, variables: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug(f"Running agent: {agent.config.name}")
    logger.debug(f"variables: {variables}")
    return agent(variables)


class BaseWorkflow(ABC):

    def __init__(self, config: BaseWorkflowConfig = None):
        self.config = config
        self.variables: Dict[str, Any] = {}

        self.agents = self._init_agents()

    @abstractmethod
    def _init_agents(self) -> List[BaseAgentProxy]:
        pass

    @abstractmethod
    def run(self, input_vars: Dict[str, Any]) -> Any:
        pass


class Workflow(BaseWorkflow):

    def __init__(self, config: BaseWorkflowConfig = None):
        super().__init__(config)

    def _init_agents(self) -> List[BaseAgentProxy]:
        framework_cls_map = {
            "general": GenralAgentProxy,
            "together": TogetherAgentProxy,
            "openai": OpenaiAgentProxy,
        }

        framework = self.config.model_framework

        # get the class of the framework
        framework_cls = framework_cls_map.get(framework, None)
        if framework_cls is None:
            raise ValueError(f"Invalid framework: {framework}")

        agents: List[BaseAgentProxy] = []
        for agent_config in self.config.agents:
            print(f"Initializing agent: {agent_config.name}")
            agent_config.model = self.config.model
            agent_config.token_limit = self.config.token_limit
            agent_config.api_key = self.config.api_key
            agent_config.base_url = self.config.base_url
            agent_config.clean_memory = self.config.clean_memory
            agent_config.workspace = os.path.join(
                self.config.base_workspace, agent_config.workspace
            )

            agent = framework_cls(agent_config)

            agents.append(agent)

            print(f"Agent {agent_config.name} initialized")

        return agents

    def run(self, input_vars: Dict[str, Any]):
        # 验证输入变量
        for var in self.config.input_vars:
            if var.name not in input_vars:
                raise ValueError(f"Missing input variable: {var.name}")

        # 合并输入变量和已有变量
        self.variables.update(input_vars)

        # 对智能体进行优先级排序
        agent_priority_dict = {}
        for agent in self.agents:
            if agent.config.priority not in agent_priority_dict:
                agent_priority_dict[agent.config.priority] = []
            agent_priority_dict[agent.config.priority].append(agent)

        # 获取所有优先级，从 1 到 n 排序
        priorities = sorted(agent_priority_dict.keys())
        logger.debug(f"Priorities: {priorities}")

        # 逐个优先级运行智能体, 必须按照优先级顺序运行
        for priority in priorities:
            logger.info(f"Running agents at priority {priority}")
            agents = agent_priority_dict[priority]

            # 多线程并行运行智能体
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(run_agent, agent, self.variables)
                    for agent in agents
                ]
                results = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                ]

            # 更新变量
            for result in results:
                self.variables.update(result)

        # 返回 output 变量
        output = self.config.output.format(**self.variables)
        return output

    def to_dict(self):
        return {
            "config": self.config.model_dump(),
            "agents": [agent.to_dict() for agent in self.agents],
        }
