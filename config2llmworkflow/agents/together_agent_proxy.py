from typing import Dict, Any
from config2llmworkflow.agents.base import BaseAgentProxy

import logging

logger = logging.getLogger(__name__)


class TogetherAgentProxy(BaseAgentProxy):

    def _init_client(self):
        from together import Together

        self.client = Together(api_key=self.config.api_key)

    def _query(self, messages):
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.token_limit,
            temperature=self.config.temperature,
            top_p=0.7,
            top_k=50,
            repetition_penalty=self.config.frequency_penalty,
            stop=["<|eot_id|>"],
            stream=False,
        )

        return response.choices[0].message.content

    def run(self, input_vars: Dict[str, Any]) -> Dict[str, Any]:
        # 格式化 role 和 prompt
        logger.info(f"Setting input variables: {input_vars}")
        self.full_role = self.config.role.format(**input_vars)
        logger.info(f"Setting role: {self.full_role}")
        self.full_prompt = self.config.prompt.format(**input_vars)
        logger.info(f"Setting prompt: {self.full_prompt}")

        output_vars = self._query(
            messages=[
                {"role": "system", "content": self.full_role},
                {"role": "user", "content": self.full_prompt},
            ]
        )

        if isinstance(output_vars, str) and len(self.config.output_vars) == 1:
            output_vars = {self.config.output_vars[0]["name"]: output_vars}
        elif isinstance(output_vars, dict):
            output_vars = {
                var["name"]: output_vars.get(var["name"], "")
                for var in self.config.output_vars
            }

        self.answer = output_vars

        return output_vars
