from typing import Dict, Any, List
from GeneralAgent import Agent
from abc import ABC, abstractmethod
from enum import Enum
import sys
import re
import json
from config2llmworkflow.nodes.base import Node
from config2llmworkflow.configs.agents.base import BaseAgentProxyConfig
from config2llmworkflow.configs.nodes.base import BaseNodeConfig, NodeType

import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


class AgentProvider(Enum):
    OPENAI = "openai"
    TOGETHER = "together"
    GENERAL = "general"


class BaseAgentProxy(Node):
    type = NodeType.AGENT

    answer: Dict[str, Any] = {}
    full_role: str = ""
    full_prompt: str = ""
    messages: List[Dict[str, str]] = []

    def __init__(self, config: BaseAgentProxyConfig):
        self.config = config
        self._init_client()

    @abstractmethod
    def _init_client(self):
        pass

    def to_dict(self):
        return {
            "config": self.config.model_dump(),
            "full_role": self.full_role,
            "full_prompt": self.full_prompt,
            "answer": self.answer,
        }
