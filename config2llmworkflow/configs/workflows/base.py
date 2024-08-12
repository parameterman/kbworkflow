# config2llmworkflow/configs/workflows/base.py


from pydantic import Field
from typing import List, Optional

from config2llmworkflow.configs.nodes.base import BaseNodeConfig
from config2llmworkflow.configs.agents.base import (
    BaseAgentProxyConfig,
    GlobalAgentConfig,
)


class BaseWorkflowConfig(BaseNodeConfig):
    provider: str = Field(..., title="Provider, including default, loop")
    nodes: List[BaseNodeConfig] = Field(..., title="Nodes")
    global_agent: Optional[GlobalAgentConfig] = Field(None, title="Global agent")


class BaseLoopWorkflowConfig(BaseWorkflowConfig):
    """
    Loop 是用来循环执行的节点，直到满足用户的判断条件才可以离开
    """

    end_condition: str = Field(..., title="End condition expression in python")
    max_loops: int = Field(3, title="Max loops")
    watchdog_agent: BaseAgentProxyConfig = Field(..., title="Agent")
