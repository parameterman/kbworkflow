from typing import List
from config2llmworkflow.configs.nodes.base import InputVariableConfig
from config2llmworkflow.app.base import BaseApp
import streamlit as st
import json
from loguru import logger


class App(BaseApp):

    def create_input_container(self):
        # 根据 self.config.workflow.input_vars 来创建输入容器

        input_vars: List[InputVariableConfig] = self.config.workflow.input_vars
        for input_var in input_vars:
            logger.info("🔧[Input]创建输入变量: {}", input_var.name)
            input_var_type = input_var.type
            input_var_name = input_var.name
            input_var_component = input_var.component  # noqa

            if input_var_component == "text_area" and input_var_type == "str":
                exec(
                    f"{input_var_name} = st.text_area(label=input_var.label, value=input_var.default, height=300, placeholder=input_var.placeholder)"
                )
            elif input_var_component == "selectbox" and input_var_type in [
                "str",
                "int",
                "float",
            ]:
                exec(
                    f"{input_var_name} = st.selectbox(label=input_var.label, options=input_var.options, index=input_var.default)"
                )
            elif input_var_component == "multiselect" and input_var_type in [
                "list[str]",
                "list[int]",
                "list[float]",
            ]:
                exec(
                    f"{input_var_name} = st.multiselect(label=input_var.label, options=input_var.options, default=input_var.default)"
                )
            elif input_var_component == "text_input" and input_var_type in [
                "str",
                "int",
                "float",
            ]:
                exec(
                    f"{input_var_name} = st.text_input(label=input_var.label,value=input_var.default,placeholder=input_var.placeholder)"
                )
            elif input_var_component == "number_input" and input_var_type in [
                "int",
                "float",
            ]:
                exec(
                    f"{input_var_name} = st.number_input(label=input_var.label, value=input_var.default,placeholder=input_var.placeholder)"
                )
            elif input_var_component == "slider" and input_var_type in ["int", "float"]:
                exec(
                    f"{input_var_name} = st.slider(label=input_var.label, min_value=input_var.min, max_value=input_var.max, value=input_var.default)"
                )
            else:
                raise ValueError(
                    f"Unsupported input variable component: {input_var_component}"
                )

        local_vars = locals()
        # 删除其中的 "self" 和 "input_vars"
        del local_vars["self"]
        del local_vars["input_vars"]
        return local_vars

    def valid_input_vars(self, input_vars: dict) -> bool:
        # 验证输入变量
        if not all(input_vars.values()):
            for var_name, var_value in input_vars.items():
                if not var_value:
                    # 根据var_name找到var_label
                    var_label = next(
                        var.label
                        for var in self.config.workflow.input_vars
                        if var.name == var_name
                    )
                    st.error(f"请填写 :{var_label}")
            return False

        return True  # 证明所有的输入变量都已经填写

    def show_sidebar(self):
        # 在侧边栏显示每一个 AgentProxy 的输出
        st.sidebar.title("Agent 输出")
        # 显示一个下载json文件的按钮
        st.sidebar.download_button(
            label="下载日志",
            data=json.dumps(self.workflow.logs, ensure_ascii=False, indent=4),
        )
        st.sidebar.json(self.workflow.logs)

    def show_footer(self):
        # 显示页脚
        st.markdown("---")
        st.markdown(self.config.footer)

    def run(self) -> None:
        st.title(self.config.name)

        input_vars = self.create_input_container()

        if st.button("运行工作流"):
            if self.valid_input_vars(input_vars):
                with st.spinner("运行中..."):
                    # 运行工作流
                    all_out_vars = self.workflow.run(input_vars=input_vars)
                    # 格式化
                    output = self.config.output.format(**all_out_vars)
                    if self.config.show_sidebar:
                        self.show_sidebar()
                # 显示结果
                if output:
                    st.markdown("---")
                    st.title("结果")
                    logger.info("✨[Output]最终结果: \n{}", output)
                    st.write(output)
                else:
                    st.error("运行工作流失败")
        # 添加页脚
        self.show_footer()
