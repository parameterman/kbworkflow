# config2llmworkflow/configs/app/base.py

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
    show_sidebar: Optional[bool] = Field(False, title="Show sidebar")
    output: Optional[str] = Field(None, title="App output")
    workflow: BaseWorkflowConfig = Field(..., title="Workflow")

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "footer": self.footer,
            "show_sidebar": self.show_sidebar,
            "output": self.output,
            "workflow": self.workflow.to_dict(),
        }
