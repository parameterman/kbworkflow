from typing import List, Dict, Any
import concurrent.futures

from config2llmworkflow.configs.workflows.base import BaseWorkflowConfig
from config2llmworkflow.nodes.base import Node
from config2llmworkflow.configs.nodes.base import NodeType
from loguru import logger


def run_node(node: Node, variables: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("🔄[Node]Running node: {}", node.config.name)
    logger.debug("🔄[Node]variables: {}", variables)
    return node(variables)


class BaseWorkflow(Node):
    type = NodeType.WORKFLOW

    def __init__(self, config: BaseWorkflowConfig = None):
        super().__init__(config)
        self.config = config
        self.variables = {}
        self.nodes = []

        logger.debug(
            "🏗️[Workflow]BaseWorkflow -> {}: {}", type(self.config), self.config
        )

        self._init_nodes()

    def _init_nodes(self) -> List[Node]:
        logger.debug("📋[Workflow]self.config.nodes: \n {}", self.config.nodes)

        from config2llmworkflow.utils.factory import NodeFactory

        # 根据类型来创建节点
        for node_config in self.config.nodes:
            logger.info(
                "🔨[Workflow]Creating node: {} \n config: {}",
                node_config.name,
                node_config,
            )
            node = NodeFactory.create(node_config.to_dict())
            self.nodes.append(node)

        logger.info(
            "✅[Workflow]Created nodes for {}: {}",
            self.config.name,
            [node.config.name for node in self.nodes],
        )
        return self.nodes

    @property
    def logs(self) -> Dict[str, Any]:
        logger.debug("📊[Workflow]Current workflow: {}", self.config.name)
        logger.debug(
            "📊[Workflow]Current nodes: {}", [node.config.name for node in self.nodes]
        )

        if self.nodes:
            self.node_log["nodes"] = [node.logs for node in self.nodes]

        return self.node_log


class DefaultWorkflow(BaseWorkflow):

    def __init__(self, config: BaseWorkflowConfig = None):
        super().__init__(config)

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("▶️[Workflow]Running default workflow: {}", self.config.name)
        logger.debug("📋[Workflow]All nodes: {}", self.nodes)
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
        logger.info("🔀[Workflow]node_priority_dict: {}", node_priority_dict)

        # 获取所有优先级，从 1 到 n 排序
        priorities = sorted(node_priority_dict.keys())

        # 逐个优先级运行智能体, 必须按照优先级顺序运行
        output_vars = {}
        for priority in priorities:
            logger.info("⚡[Workflow]Running nodes at priority {}", priority)
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

        logger.info(
            "✅[Workflow]Finished running default workflow: {}", self.config.name
        )
        return output_vars

    def to_dict(self):
        return {
            "config": self.config.model_dump(),
            "nodes": [node.to_dict() for node in self.nodes],
        }
