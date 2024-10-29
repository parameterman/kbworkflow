from loguru import logger
import importlib
from typing import Optional, Dict

from config2llmworkflow.nodes.base import Node
from config2llmworkflow.agents.base import BaseAgentProxy
from config2llmworkflow.workflows.base import BaseWorkflow


def load_class(class_type):
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class AgentProxyFactory:
    provider_to_class = {
        "general": "config2llmworkflow.agents.GeneralAgentProxy",
        "openai": "config2llmworkflow.agents.OpenaiAgentProxy",
        "gemini": "config2llmworkflow.agents.GeminiAgentProxy",
        "together": "config2llmworkflow.agents.TogetherAgentProxy",
        "litellm": "config2llmworkflow.agents.LitellmAgentProxy",
    }

    provider_to_config = {
        "*": "config2llmworkflow.configs.agents.base.BaseAgentProxyConfig",
    }

    @classmethod
    def create(
        cls, config, provider_name: Optional[str] = None
    ) -> BaseAgentProxy | None:
        provider_name = provider_name or config.get("provider")

        class_type = cls.provider_to_class.get(provider_name)
        config_type = cls.provider_to_config.get(
            provider_name, cls.provider_to_config["*"]
        )
        if class_type:
            agent_proxy_instance = load_class(class_type)
            config_instance = load_class(config_type)
            base_config = config_instance(**config)
            return agent_proxy_instance(base_config)
        else:
            raise ValueError(f"Unsupported Agent Proxy provider: {provider_name}")


class WorkflowFactory:
    provider_to_class = {
        "default": "config2llmworkflow.workflows.base.DefaultWorkflow",
        "loop": "config2llmworkflow.workflows.loop.LoopWorkflow",
    }

    provider_to_config = {
        "default": "config2llmworkflow.configs.workflows.base.BaseWorkflowConfig",
        "loop": "config2llmworkflow.configs.workflows.base.BaseLoopWorkflowConfig",
    }

    @classmethod
    def create(cls, config, provider_name: Optional[str] = None) -> BaseWorkflow | None:
        provider_name = provider_name or config.get("provider")
        if not provider_name:
            raise ValueError("provider_name not provided")

        logger.debug("🔧[Workflow]provider_name={}", provider_name)

        class_type = cls.provider_to_class.get(provider_name)
        config_type = cls.provider_to_config.get(
            provider_name,
        )
        if class_type:
            workflow_instance = load_class(class_type)
            config_instance = load_class(config_type)
            base_config = config_instance(**config)
            return workflow_instance(base_config)
        else:
            raise ValueError(f"Unsupported Workflow Proxy provider: {provider_name}")


class NodeFactory:

    type_to_factory = {"agent": AgentProxyFactory, "workflow": WorkflowFactory}

    @classmethod
    def create(
        cls,
        config: Dict,
        type_name: Optional[str] = None,
        provider_name: Optional[str] = None,
    ) -> Node | None:
        type_name = type_name or config.get("node_type", None)
        provider_name = provider_name or config.get("provider", None)

        if not (type_name and provider_name):
            raise ValueError(f"node_type or provider not supported in config: {config}")

        factory_class = cls.type_to_factory.get(type_name)
        if type_name:
            return factory_class.create(config=config, provider_name=provider_name)
        else:
            raise ValueError(f"Unsupported Node Type: {type_name}")


class AppFactory:

    provider_to_class = {
        "*": "config2llmworkflow.main.App",
    }
    provider_to_config = {
        "*": "config2llmworkflow.configs.app.base.BaseAppConfig",
    }

    @classmethod
    def create(cls, config, provider_name: Optional[str] = None):
        class_type = cls.provider_to_class.get(
            provider_name, cls.provider_to_class["*"]
        )
        config_type = cls.provider_to_config.get(
            provider_name, cls.provider_to_config["*"]
        )
        if class_type:
            app_instance = load_class(class_type)
            config_instance = load_class(config_type)
            base_config = config_instance(**config)
            return app_instance(base_config)
        else:
            raise ValueError(f"Unsupported app provider: {provider_name}")
