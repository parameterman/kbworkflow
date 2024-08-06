from typing import List, Dict, Any
from abc import ABC, abstractmethod
import multiprocessing
import os

from config2llmworkflow.configs.workflows.base import BaseWorkflowConfig
from config2llmworkflow.agents.base import AgentProxy


# 定义一个全局函数以供多进程使用
def run_agent(agent: AgentProxy, variables: Dict[str, Any]) -> Dict[str, Any]:
    return agent(variables)


class BaseWorkflow(ABC):

    def __init__(self, config: BaseWorkflowConfig = None):
        self.config = config
        self.variables: Dict[str, Any] = {}

        self.agents = self._init_agents()

    @abstractmethod
    def _init_agents(self):
        pass

    @abstractmethod
    def run(self, input_vars: Dict[str, Any]) -> Any:
        pass


class Workflow(BaseWorkflow):

    def __init__(self, config: BaseWorkflowConfig = None):
        super().__init__(config)

    def _init_agents(self):
        agents: Dict[int, List[AgentProxy]] = {}
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

            agent = AgentProxy(config=agent_config)

            if agent_config.priority not in agents:
                agents[agent_config.priority] = []

            agents[agent_config.priority].append(agent)
            print(f"Agent {agent_config.name} initialized")

        return agents

    def run(self, input_vars: Dict[str, Any]):
        # 验证输入变量
        for var in self.config.input_vars:
            if var.name not in input_vars:
                raise ValueError(f"Missing input variable: {var.name}")

        # 合并输入变量和已有变量
        self.variables.update(input_vars)

        # 获取所有优先级，从 1 到 n 排序
        priorities = sorted(self.agents.keys())
        print(f"Priorities: {priorities}")

        # 逐个优先级运行智能体, 必须按照优先级顺序运行
        for priority in priorities:
            print(f"Running agents at priority {priority}")
            agents = self.agents[priority]

            # 多进程并行运行智能体
            with multiprocessing.Pool() as pool:
                results = pool.starmap(
                    run_agent, [(agent, self.variables) for agent in agents]
                )

            # 更新变量
            for result in results:
                self.variables.update(result)

        # 返回 output 变量
        output = self.config.output.format(**self.variables)
        return output
