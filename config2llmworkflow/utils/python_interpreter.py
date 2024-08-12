import re
import subprocess
import sys

import logging

logger = logging.getLogger(__name__)


class PythonInterpreter:
    code_pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
    code: str = None
    result: str = None

    def __init__(self, text: str):
        self.text = text

    def include_python_code(self):
        # 找到python代码，如果有则返回代码，没有则返回None
        match = self.code_pattern.search(self.text)
        if match:
            self.code = match.group(1)
            return self.code
        return None

    def run_python_code(self):
        if self.code is None:
            logger.error("No code to run")
            return None

        logger.info(f"Running Python code: {self.code}")

        try:
            # 开启进程，使用python运行代码
            result = subprocess.run(
                [sys.executable, "-c", self.code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            # 获取输出
            self.result = result.stdout.strip()
            logger.info(f"Python code output: {self.result}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running Python code: {e.stderr}")
            self.result = e.stderr.strip()

        return self.result
