from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class BaseAgentProxyConfig(BaseModel):
    name: str = Field(..., title="Agent name")
    role: str = Field(..., title="Agent role")
    prompt: str = Field(..., title="Agent prompt")
    priority: int = Field(1, title="Agent priority")
    workspace: str = Field(..., title="Agent workspace")
    clean_memory: bool = Field(True, title="Clean memory")
    output_vars: List[Dict[str, str]] = Field(..., title="Output variables")
    # model parameters
    model: str = Field("deepseek-chat", title="Model name")
    token_limit: int = Field(8096, title="Token limit")
    api_key: str = Field("", title="API key")
    base_url: str = Field("https://api.deepseek.com/v1", title="Base URL")
    temperature: float = Field(0.0, title="Temperature")
    frequency_penalty: float = Field(2, title="Frequency penalty")
    reflect_times: int = Field(0, title="Reflect times")
    continue_run: bool = Field(True, title="Continue run")


class BaseVariableConfig(BaseModel):
    name: str = Field(..., title="Variable name")
    type: str = Field(..., title="Variable type")
    description: Optional[str] = Field(None, title="Variable description")


class InputVariableConfig(BaseVariableConfig):
    label: Optional[str] = Field(None, title="Variable label")
    placeholder: Optional[str] = Field(None, title="Variable placeholder")
    component: str = Field(..., title="Variable component")
    options: Optional[List[str | int | float]] = Field(None, title="Variable options")
    min: Optional[int | float] = Field(None, title="Variable min")
    max: Optional[int | float] = Field(None, title="Variable max")
    default: Optional[str | int | float | List[str | int | float]] = Field(
        None, title="Variable default"
    )
