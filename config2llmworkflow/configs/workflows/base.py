from pydantic import BaseModel, Field
from typing import List, Optional


from config2llmworkflow.configs.agents.base import (
    BaseAgentProxyConfig,
    BaseVariableConfig,  # noqa
    InputVariableConfig,
)


class BaseWorkflowConfig(BaseModel):
    name: Optional[str] = Field(None, title="Workflow name")
    description: Optional[str] = Field(None, title="Workflow description")
    model_framework: str = Field("deepseek", title="Model framework")
    model: str = Field("deepseek-chat", title="Model name")
    token_limit: int = Field(8096, title="Token limit")
    api_key: str = Field(..., title="API key")
    base_url: str = Field("https://api.deepseek.com/v1", title="Base URL")
    base_workspace: str = Field("agent_workspace", title="Base workspace")
    clean_memory: bool = Field(True, title="Clean memory")
    input_vars: List[InputVariableConfig] = Field(..., title="Input variables")
    agents: List[BaseAgentProxyConfig] = Field(..., title="Agents")
    output: str = Field(..., title="Output")
