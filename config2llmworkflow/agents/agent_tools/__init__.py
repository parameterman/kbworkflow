from config2llmworkflow.agents.agent_tools.tools import (
    sum_floats,
    sum_floats_tool,
    calculate_gap_requirements,
    calculate_gap_requirements_tool,
    calculate_space_requirements,
    calculate_space_requirements_tool,
    calculate_spee_space,
    calculate_space_requirements_tool,
    calculate_total_space_requirement,
    calculate_total_space_requirement_tool,
    calculate_molar_space,
    calculate_molar_space_tool,
)

tool_name_to_func_map = {
    "sum_floats": sum_floats,
    "calculate_gap_requirements": calculate_gap_requirements,
    "calculate_space_requirements": calculate_space_requirements,
    "calculate_spee_space": calculate_spee_space,
    "calculate_total_space_requirement": calculate_total_space_requirement,
    "calculate_molar_space": calculate_molar_space,
}

tool_name_to_schema_map = {
    "sum_floats": sum_floats_tool,
    "calculate_gap_requirements": calculate_gap_requirements_tool,
    "calculate_space_requirements": calculate_space_requirements_tool,
    "calculate_spee_space": calculate_space_requirements_tool,
    "calculate_total_space_requirement": calculate_total_space_requirement_tool,
    "calculate_molar_space": calculate_molar_space_tool,
}
