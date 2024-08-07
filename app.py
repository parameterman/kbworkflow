import streamlit as st
from config2llmworkflow.utils.factory import AppFactory
import yaml
import os
import logging
from rich.logging import RichHandler


logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler()])

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
    # if "app" not in st.session_state:
    #     st.session_state.app = AppFactory().from_config(config["app"])

    # st.session_state.app.run()

    AppFactory().from_config(config["app"]).run()


def main():
    st.title("Wisup Configuration Runner")

    uploaded_file = st.file_uploader("Upload your config file", type="yaml")

    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        if file_path:
            config = load_config(file_path)
            st.write("Config file loaded successfully.")

            run_app(config)

    else:
        st.write("Please upload a config file.")


if __name__ == "__main__":
    main()
