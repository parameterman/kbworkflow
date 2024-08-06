from config2llmworkflow.configs.app.base import BaseAppConfig
from config2llmworkflow.configs.workflows.base import BaseWorkflowConfig
from config2llmworkflow.configs.agents.base import BaseAgentProxyConfig
from config2llmworkflow.workflows.base import Workflow
from config2llmworkflow.agents.base import AgentProxy


class AgentProxyFactory:

    def __init__(self):
        pass

    def create_agent_proxy(self, config: BaseAgentProxyConfig):
        return AgentProxy(config)

    @staticmethod
    def from_config(config: dict):
        return AgentProxy(BaseAgentProxyConfig(**config))


class WorkflowFactory:

    def __init__(self):
        pass

    def create_workflow(self, config: BaseWorkflowConfig):
        return Workflow(config)

    @staticmethod
    def from_config(config: dict):
        return Workflow(BaseWorkflowConfig(**config))


class AppFactory:

    def __init__(self):
        pass

    def create_app(self, config: BaseAppConfig):
        from config2llmworkflow.main import App

        return App(config)

    @staticmethod
    def from_config(config: dict):
        from config2llmworkflow.main import App

        return App(BaseAppConfig(**config))
