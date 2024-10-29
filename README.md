# Config2LlmWorkflow

一个基于配置文件的LLM工作流框架，支持多种LLM模型，支持多种数据源，支持多种输出格式。

## 如何启动项目

1. 安装环境

```bash
conda create -n config2llmworkflow python=3.10
conda activate config2llmworkflow
pip install poetry # 安装poetry包管理器
conda activate config2llmworkflow # 再次激活环境
```

2. 安装依赖

```bash
poetry install
```

3. 启动项目

```bash
streamlit run app.py -- --config ./configs/config.yaml
```
