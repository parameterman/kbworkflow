import streamlit as st
from config2llmworkflow.utils.factory import AppFactory
import yaml
import os
import logging
from datetime import datetime
from rich.logging import RichHandler


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir, f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[RichHandler(), logging.FileHandler(log_file)],
    )


setup_logging()

logger = logging.getLogger(__name__)


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


def main():
    st.title("Wisup Configuration Runner")

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
    main()
