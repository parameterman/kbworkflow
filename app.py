import streamlit as st
from config2llmworkflow.utils.factory import AppFactory
import yaml
import os
from datetime import datetime
from loguru import logger
import argparse

logger.add(os.path.join("logs", f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"))

def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join("/tmp", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join("/tmp", uploaded_file.name)
    except Exception as e:
        st.error(f"Failed to save uploaded file: {e}")
        return None

def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def run_app(config):
    AppFactory.create(config=config["app"]).run()

def main(config_path=None):
    # st.title("Wisup Configuration Runner")

    if config_path:
        # 从命令行参数指定的文件路径加载配置
        if os.path.exists(config_path):
            config = load_config(config_path)
            # st.write("配置文件加载成功")
            run_app(config)
        else:
            st.error(f"指定的配置文件不存在: {config_path}")
    else:
        # 使用Streamlit界面上传配置文件
        uploaded_file = st.file_uploader("请上传配置文件", type="yaml")

        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            if file_path:
                config = load_config(file_path)
                st.write("配置文件加载成功")
                run_app(config)
        else:
            st.write("Please upload a config file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Streamlit app with optional config file argument.")
    parser.add_argument("--config", type=str, help="Path to the configuration file.")
    
    args = parser.parse_args()
    
    main(config_path=args.config)