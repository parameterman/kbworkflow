from abc import ABC, abstractmethod
from typing import Any, Dict

from config2llmworkflow.configs.nodes.base import BaseNodeConfig


class Node(ABC):
    type = "node"
    # 记录流程

    def __init__(self, config: BaseNodeConfig = None):
        self.config = config
        self.node_log = {
            "name": self.config.name,
            "priority": self.config.priority,
            "description": self.config.description,
        }

    @abstractmethod
    def run(self, input_vars: Dict[str, Any]) -> Any:
        pass

    def __call__(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        return self.run(input_vars)

    @abstractmethod
    def to_dict(self):
        pass

    @property
    def logs(self):
        return self.node_log
