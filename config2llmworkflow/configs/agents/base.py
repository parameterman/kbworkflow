# config2llmworkflow/configs/agents/base.py

from pydantic import Field, BaseModel
from typing import Optional

from config2llmworkflow.configs.nodes.base import BaseNodeConfig


class BaseAgentConfig(BaseNodeConfig):
    provider: str = Field("openai", title="Agent framework")
    clean_memory: bool = Field(True, title="Clean memory")

    # model parameters
    model: str = Field("deepseek-chat", title="Model name")
    token_limit: int = Field(8096, title="Token limit")
    api_key: str = Field("", title="API key")
    base_url: str = Field("https://api.deepseek.com/v1", title="Base URL")
    temperature: float = Field(0.0, title="Temperature")
    frequency_penalty: float = Field(2, title="Frequency penalty")
    reflect_times: int = Field(0, title="Reflect times")
    continue_run: bool = Field(True, title="Continue run")
    disable_python_run: bool = Field(False, title="Disable python run")


class GlobalAgentConfig(BaseModel):
    provider: str = Field("openai", title="Agent framework")
    clean_memory: bool = Field(True, title="Clean memory")

    # model parameters
    model: str = Field("deepseek-chat", title="Model name")
    token_limit: int = Field(8096, title="Token limit")
    api_key: str = Field("", title="API key")
    base_url: str = Field("https://api.deepseek.com/v1", title="Base URL")
    temperature: float = Field(0.0, title="Temperature")
    frequency_penalty: float = Field(2, title="Frequency penalty")
    reflect_times: int = Field(0, title="Reflect times")
    continue_run: bool = Field(True, title="Continue run")
    disable_python_run: bool = Field(False, title="Disable python run")

    def to_dict(self):
        return self.model_dump()


class BaseAgentProxyConfig(BaseAgentConfig):
    role: str = Field(..., title="Agent role")
    prompt: str = Field(..., title="Agent prompt")
    workspace: Optional[str] = Field(None, title="Workspace")
