# config2llmworkflow/configs/nodes/base.py


from pydantic import BaseModel, Field, field_validator

from typing import List, Optional
from enum import Enum


class BaseVariableConfig(BaseModel):
    name: str = Field(..., title="Variable name")
    type: str = Field(..., title="Variable type")
    description: Optional[str] = Field(None, title="Variable description")


class InputVariableConfig(BaseVariableConfig):
    label: Optional[str] = Field(None, title="Variable label")
    placeholder: Optional[str] = Field(None, title="Variable placeholder")
    component: Optional[str] = Field(None, title="Variable component")
    options: Optional[List[str | int | float]] = Field(None, title="Variable options")
    min: Optional[int | float] = Field(None, title="Variable min")
    max: Optional[int | float] = Field(None, title="Variable max")
    default: Optional[str | int | float | List[str | int | float]] = Field(
        None, title="Variable default"
    )


class OutputVariableConfig(BaseVariableConfig):
    pass


class NodeType(Enum):
    AGENT = "agent"
    WORKFLOW = "workflow"
    LOOP = "loop"


class BaseNodeConfig(BaseModel):
    """Node最小的可执行单元"""

    name: str = Field(..., description="节点名称")
    node_type: str = Field(..., description="节点类型")
    description: str = Field("", description="节点描述")
    input_vars: Optional[List[InputVariableConfig]] = Field([], description="输入变量")
    output_vars: Optional[List[OutputVariableConfig]] = Field(
        [], description="输出变量"
    )
    priority: float = Field(1.0, description="优先级")

    class Config:
        extra = "allow"

    def to_dict(self):
        return self.model_dump()
