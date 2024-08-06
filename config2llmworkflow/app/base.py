from abc import ABC, abstractmethod
from config2llmworkflow.configs.app.base import BaseAppConfig
from config2llmworkflow.utils.factory import WorkflowFactory


class BaseApp(ABC):

    def __init__(self, config: BaseAppConfig = None):
        self.config = config
        self.name = self.config.name
        self.description = self.config.description
        self.footer = self.config.footer

        if self.config is None:
            raise ValueError("App configuration is required")

        self.workflow = WorkflowFactory().create_workflow(self.config.workflow)

    @abstractmethod
    def create_input_container(self):
        pass

    @abstractmethod
    def run(self) -> None:
        """Start the app."""
        pass
