from typing import Any, Dict
from config2llmworkflow.configs.nodes.base import NodeType

from config2llmworkflow.workflows.base import DefaultWorkflow
from config2llmworkflow.configs.workflows.base import BaseLoopWorkflowConfig

import logging

logger = logging.getLogger(__name__)


def _match_condition(condition: str, vars: dict) -> bool:
    # end_condition 是一个 python 表达式, 例如: "1 == 1"
    try:
        # 格式化
        condition = condition.format(**vars)
        return eval(condition)
    except Exception as e:
        logger.error(f"Error when match condition: {condition}, {e}")
        return False


class LoopWorkflow(DefaultWorkflow):
    type = NodeType.LOOP

    def __init__(self, config: BaseLoopWorkflowConfig = None):
        super().__init__(config)
        self._init_watchdog_agent()

    def _init_watchdog_agent(self):
        from config2llmworkflow.utils.factory import AgentProxyFactory

        self.watchdog_agent = AgentProxyFactory.create(
            config=self.config.watchdog_agent.to_dict()
        )

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 先运行完所有的节点，再让 watchdog_agent 运行判断结果
        logger.debug(f"Start running loop workflow, name: {self.config.name}")
        output_vars = input_vars.copy()
        # output_vars = input_vars
        loop_time = 1

        while True:
            logger.info(
                f"Loop work flow [{self.config.name}] running loop time: {loop_time}"
            )
            logger.debug(f"{input_vars=}")
            logger.info(f"Start running nodes")
            logger.info(f"nodes: {self.nodes}")
            tmp_output_vars = super().run(input_vars)
            logger.info(f"End running nodes")
            logger.debug(f"{tmp_output_vars=}")
            # 让 watchdog_agent 运行
            tmp_watchdog_output_vars = self.watchdog_agent.run(tmp_output_vars)

            logger.debug(
                f"{tmp_watchdog_output_vars=}"
            )  # {'result_match': '0', 'result_2': ''}

            # 检查是否满足结束条件
            end_condition = self.config.end_condition.format(**tmp_watchdog_output_vars)
            logger.info(f"Check end condition: {end_condition}")
            if (
                _match_condition(end_condition, tmp_watchdog_output_vars)
                or loop_time > self.config.max_loops
            ):
                logger.info(f"loop has match condition or above max loops")
                output_vars.update(tmp_output_vars)
                output_vars.update(tmp_watchdog_output_vars)
                break

            loop_time += 1
            logger.info(f"loop time update to {loop_time}")

        logger.debug(f"End running loop workflow, name: {self.config.name}")
        logger.debug(f"output_vars: {output_vars}")

        return output_vars

    def to_dict(self):
        return {
            "config": self.config.to_dict(),
            "nodes": [node.to_dict() for node in self.nodes],
            "watchdog_agent": self.watchdog_agent.to_dict(),
        }

    @property
    def logs(self) -> Dict[str, Any]:
        self.node_log["nodes"] = [node.logs for node in self.nodes]
        self.node_log["watchdog_agent"] = self.watchdog_agent.logs

        return self.node_log
