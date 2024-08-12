from typing import List, Dict, Any
import concurrent.futures

from config2llmworkflow.configs.workflows.base import BaseWorkflowConfig
from config2llmworkflow.nodes.base import Node
from config2llmworkflow.configs.nodes.base import NodeType
from config2llmworkflow.agents.base import BaseAgentProxyConfig
from config2llmworkflow.configs.workflows.base import BaseLoopWorkflowConfig


import logging

logger = logging.getLogger(__name__)


def run_node(node: Node, variables: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug(f"Running node: {node.config.name}")
    logger.debug(f"variables: {variables}")
    return node(variables)


class BaseWorkflow(Node):
    type = NodeType.WORKFLOW

    def __init__(self, config: BaseWorkflowConfig = None):
        self.config = config
        self.variables = {}
        self.nodes = []

        logger.debug(f"BaseWorkflow -> {type(self.config)}: {self.config}")

        self._init_nodes()

    def _init_nodes(self) -> List[Node]:
        # 如果当前配置的 global_agent 不是 None，那么需要将 global_agent 覆盖到所有的 agent 中
        # if (
        #     "global_agent" in self.config.model_fields
        #     and self.config.global_agent is not None
        # ):
        #     logger.debug(f"self.config.global_agent = {self.config.global_agent}")

        # 用global_agent里的非空字段来替换 每个 self.config.nodes 里的值

        # for field_name, field_value in self.config.global_agent.to_dict().items():
        #     if field_value:
        #         for node_config in self.config.nodes:
        #             # 设置变量
        #             # logger.debug(
        #             #     f"Before setting type of node_config: {type(node_config)}"
        #             # )
        #             # node_config.__setattr__(field_name, field_value)
        #             # logger.debug(
        #             #     f"After setting type of node_config: {type(node_config)}"
        #             # )

        #             # 如果 node_config 包含 watchdog_agent 字段，则也覆盖 watchdog_agent
        #             if "watchdog_agent" in node_config.model_fields:
        #                 logger.debug(
        #                     f"Before setting: node_config.watchdog_agent = {node_config.watchdog_agent}"
        #                 )

        #                 old_watchdog_agent_config = node_config.watchdog_agent
        #                 logger.debug(
        #                     f"type of old_watchdog_agent_config: {type(old_watchdog_agent_config)}"
        #                 )
        #                 old_watchdog_agent_config_dict = (
        #                     old_watchdog_agent_config.to_dict()
        #                 )
        #                 logger.debug(
        #                     f"type of old_watchdog_agent_config_dict: {type(old_watchdog_agent_config_dict)}"
        #                 )
        #                 old_watchdog_agent_config_dict.__setattr__(
        #                     field_name, field_value
        #                 )

        #                 if not node_config.watchdog_agent.get(field_name, ""):
        #                     node_config.watchdog_agent[field_name] = field_value

        #                 logger.debug(
        #                     f"After setting node_config.watchdog_agent = {node_config.watchdog_agent}"
        #                 )

        #             if "global_agent" in node_config.to_dict().keys():
        #                 if node_config.global_agent is None:
        #                     node_config.global_agent = {}

        #                 logger.debug(
        #                     f"Before setting: node_config.global_agent = {node_config.global_agent}"
        #                 )
        #                 # node_config.global_agent.__setattr__(field_name, field_value)

        #                 if not node_config.global_agent.get(field_name, ""):
        #                     node_config.global_agent[field_name] = field_value

        #                 logger.debug(
        #                     f"After setting node_config.global_agent = {node_config.global_agent}"
        #                 )

        logger.debug(f"self.config.nodes: \n {self.config.nodes}")

        from config2llmworkflow.utils.factory import NodeFactory

        # 根据类型来创建节点
        for node_config in self.config.nodes:
            logger.info(f"Creating node: {node_config.name}\n config: {node_config}")
            node = NodeFactory.create(node_config.to_dict())
            self.nodes.append(node)

        logger.info(
            f"Created nodes for {self.config.name}: {[node.config.name for node in self.nodes]}"
        )
        return self.nodes

    @property
    def logs(self) -> Dict[str, Any]:
        self.node_log["nodes"] = [node.logs for node in self.nodes]

        return self.node_log


class DefaultWorkflow(BaseWorkflow):

    def __init__(self, config: BaseWorkflowConfig = None):
        super().__init__(config)

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Running default workflow: {self.config.name}")
        logger.info(f"All nodes: {self.nodes}")
        # 验证输入变量
        for var in self.config.input_vars:
            if var.name not in input_vars:
                raise ValueError(f"Missing input variable: {var.name}")

        # 合并输入变量和已有变量
        self.variables.update(input_vars)

        # 对智能体进行优先级排序
        node_priority_dict = {}
        for node in self.nodes:
            if node.config.priority not in node_priority_dict:
                node_priority_dict[node.config.priority] = []
            node_priority_dict[node.config.priority].append(node)
        logger.info(f"node_priority_dict: {node_priority_dict}")

        # 获取所有优先级，从 1 到 n 排序
        priorities = sorted(node_priority_dict.keys())

        # 逐个优先级运行智能体, 必须按照优先级顺序运行
        output_vars = {}
        for priority in priorities:
            logger.info(f"Running nodes at priority {priority}")
            nodes = node_priority_dict[priority]

            # 多线程并行运行智能体
            # run_node 返回 Dict[str, Any]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(run_node, node, self.variables) for node in nodes
                ]
                results = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                ]

            # 更新变量
            for result in results:
                self.variables.update(result)

            # 更新输出变量
            for node in nodes:
                for var in node.config.output_vars:
                    output_vars[var.name] = self.variables[var.name]

        logger.info(f"Finished running default workflow: {self.config.name}")
        return output_vars

    def to_dict(self):
        return {
            "config": self.config.model_dump(),
            "nodes": [node.to_dict() for node in self.nodes],
        }
