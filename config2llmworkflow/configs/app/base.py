from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from config2llmworkflow.configs.workflows.base import BaseWorkflowConfig


class BaseAppConfig(BaseModel):
    """
    This app can convert a configuration file to a LLM workflow.
    """

    name: Optional[str] = Field(None, title="App name")
    description: Optional[str] = Field(None, title="App description")
    footer: Optional[str] = Field(None, title="App footer")
    workflow: BaseWorkflowConfig = Field(..., title="Workflow")
