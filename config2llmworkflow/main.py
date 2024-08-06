import logging
from typing import List
from config2llmworkflow.configs.agents.base import (
    InputVariableConfig,
)
from config2llmworkflow.app.base import BaseApp
import streamlit as st


logger = logging.getLogger(__name__)


class App(BaseApp):

    def create_input_container(self):
        # 根据 self.config.workflow.input_vars 来创建输入容器

        input_vars: List[InputVariableConfig] = self.config.workflow.input_vars
        for input_var in input_vars:
            logger.info(f"Creating input variable: {input_var.name}")
            input_var_type = input_var.type
            input_var_name = input_var.name
            input_var_component = input_var.component  # noqa

            if input_var_component == "text_area" and input_var_type == "str":
                exec(
                    f"{input_var_name} = st.text_area(label=input_var.label, height=300, placeholder=input_var.placeholder)"
                )
            elif input_var_component == "selectbox" and input_var_type in [
                "str",
                "int",
                "float",
            ]:
                exec(
                    f"{input_var_name} = st.selectbox(label=input_var.label, options=input_var.options)"
                )
            elif input_var_component == "multiselect" and input_var_type in [
                "list[str]",
                "list[int]",
                "list[float]",
            ]:
                exec(
                    f"{input_var_name} = st.multiselect(label=input_var.label, options=input_var.options)"
                )
            elif input_var_component == "text_input" and input_var_type in [
                "str",
                "int",
                "float",
            ]:
                exec(
                    f"{input_var_name} = st.text_input(label=input_var.label, placeholder=input_var.placeholder)"
                )
            elif input_var_component == "number_input" and input_var_type in [
                "int",
                "float",
            ]:
                exec(
                    f"{input_var_name} = st.number_input(label=input_var.label, placeholder=input_var.placeholder)"
                )
            elif input_var_component == "slider" and input_var_type in ["int", "float"]:
                exec(
                    f"{input_var_name} = st.slider(label=input_var.label, min_value=input_var.min, max_value=input_var.max)"
                )
            else:
                raise ValueError(
                    f"Unsupported input variable component: {input_var_component}"
                )

        # 返回生成的输入变量
        return locals()

    def run(self) -> None:

        # st.set_page_config(page_title=self.config.name, layout="wide")

        st.title(self.config.name)

        input_vars = self.create_input_container()

        if st.button("运行工作流"):

            if not all(input_vars.values()):
                # 显示没有填写的输入变量
                for var_name, var_value in input_vars.items():
                    if not var_value:
                        # 根据var_name找到var_label
                        var_label = next(
                            var.label
                            for var in self.config.workflow.input_vars
                            if var.name == var_name
                        )
                        st.error(f"请填写 :{var_label}")
            else:
                with st.spinner("运行中..."):
                    # 运行工作流
                    result = self.workflow.run(input_vars=input_vars)

                # 显示结果
                if result:
                    st.markdown("---")
                    st.title("结果")
                    st.write(result)
                else:
                    st.error("运行工作流失败")

        # 添加页脚
        # 添加页脚
        st.markdown("---")
        st.markdown(self.footer)
