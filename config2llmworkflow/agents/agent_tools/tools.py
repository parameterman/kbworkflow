# agent 2 tool
def calculate_gap_requirements(
    dL1: float, hL1: float, tL1: float, dU1: float, hU1: float, tU1: float
) -> dict:
    # Calculating the required gap for lower incisors
    L1 = 2 * dL1 + hL1 + 0.8 * tL1
    # Calculating the required gap for upper incisors
    U1 = 2 * dU1 + hU1 + 0.8 * tU1

    # Returning the results with proper sign indication
    return {"L1": f"{L1}mm", "U1": f"{U1}mm"}


calculate_gap_requirements_tool = {
    "type": "function",
    "function": {
        "name": "calculate_gap_requirements",
        "description": "Calculate the required dental arch space changes for lower and upper incisors based on the provided parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "dL1": {
                    "type": "number",
                    "description": "Lower incisor retrusion/protrusion amount in mm (positive for retrusion, negative for protrusion).",
                },
                "hL1": {
                    "type": "number",
                    "description": "Lower incisor intrusion/extrusion amount in mm (positive for intrusion).",
                },
                "tL1": {
                    "type": "number",
                    "description": "Lower incisor labial/lingual tilt amount in degrees (positive for lingual tilt, negative for labial tilt).",
                },
                "dU1": {
                    "type": "number",
                    "description": "Upper incisor retrusion/protrusion amount in mm (positive for retrusion, negative for protrusion).",
                },
                "hU1": {
                    "type": "number",
                    "description": "Upper incisor intrusion/extrusion amount in mm (positive for intrusion).",
                },
                "tU1": {
                    "type": "number",
                    "description": "Upper incisor labial/lingual tilt amount in degrees (positive for lingual tilt, negative for labial tilt).",
                },
            },
            "required": ["dL1", "hL1", "tL1", "dU1", "hU1", "tU1"],
            "additionalProperties": False,
        },
    },
}


# agent 3 tool
def calculate_space_requirements(
    D1: float,
    D2: float,
    upper_left_torque: float,
    upper_right_torque: float,
    lower_left_torque: float,
    lower_right_torque: float,
) -> dict:
    # Calculating torque averages
    upper_torque_avg = (upper_left_torque + upper_right_torque) / 2
    lower_torque_avg = (lower_left_torque + lower_right_torque) / 2

    # Calculating the impact of torque correction on space
    upper_space_impact = (upper_torque_avg + 9) * 0.2  # mm
    lower_space_impact = (lower_torque_avg + 30) * 0.2  # mm

    # Calculating expansion amount
    expansion_amount = D1 + 4 - D2  # mm

    # Calculating total space requirements
    upper_total_space = upper_space_impact + expansion_amount
    lower_total_space = lower_space_impact + expansion_amount

    # Returning the results with proper sign indication
    return {
        "upper_total_space": f"{upper_total_space}mm",
        "lower_total_space": f"{lower_total_space}mm",
    }


calculate_space_requirements_tool = {
    "type": "function",
    "function": {
        "name": "calculate_space_requirements",
        "description": "计算上颌和下颌牙弓横向扩弓和磨牙转矩变化所产生的间隙量。",
        "parameters": {
            "type": "object",
            "properties": {
                "D1": {"type": "number", "description": "FA点间距离 (mm)"},
                "D2": {"type": "number", "description": "FA点对应WALA嵴间距离 (mm)"},
                "upper_left_torque": {
                    "type": "number",
                    "description": "上颌左侧第一磨牙颊面转矩 (°)",
                },
                "upper_right_torque": {
                    "type": "number",
                    "description": "上颌右侧第一磨牙颊面转矩 (°)",
                },
                "lower_left_torque": {
                    "type": "number",
                    "description": "下颌左侧第一磨牙颊面转矩 (°)",
                },
                "lower_right_torque": {
                    "type": "number",
                    "description": "下颌右侧第一磨牙颊面转矩 (°)",
                },
            },
            "required": [
                "D1",
                "D2",
                "upper_left_torque",
                "upper_right_torque",
                "lower_left_torque",
                "lower_right_torque",
            ],
            "additionalProperties": False,
        },
    },
}


# agent 4 tool
def calculate_spee_space(left_spee_depth: float, right_spee_depth: float) -> float:
    # Calculating average depth
    average_depth = (left_spee_depth + right_spee_depth) / 2

    # Calculating space required for Spee curve leveling
    spee_space_required = average_depth + 0.5

    return spee_space_required


calculate_spee_space = {
    "type": "function",
    "function": {
        "name": "calculate_spee_space",
        "description": "计算整平Spee曲线所需的间隙。",
        "parameters": {
            "type": "object",
            "properties": {
                "left_spee_depth": {
                    "type": "number",
                    "description": "左侧Spee曲线深度 (mm)",
                },
                "right_spee_depth": {
                    "type": "number",
                    "description": "右侧Spee曲线深度 (mm)",
                },
            },
            "required": ["left_spee_depth", "right_spee_depth"],
            "additionalProperties": False,
        },
    },
}


# agent 6 tool
def calculate_total_space_requirement(
    A1: float, A2: float, B1: float, B2: float, C1: float, C2: float, D1: float, D2: float, E2: float
) -> dict:
    """
    计算上下颌总间隙需求量。

    参数:
    - A1: 上颌拥挤度，正值表示需要间隙，负值表示存在间隙。
    - A2: 下颌拥挤度，正值表示需要间隙，负值表示存在间隙。
    - B1: 上颌前牙垂直向和矢状向切牙目标位改变所需或提供的间隙，正值表示需要间隙，负值表示产生间隙。
    - B2: 下颌前牙垂直向和矢状向切牙目标位改变所需或提供的间隙，正值表示需要间隙，负值表示产生间隙。
    - C1: 上颌牙弓横向扩弓和磨牙转矩变化导致的间隙变化，正值表示需要间隙，负值表示产生间隙。
    - C2: 下颌牙弓横向扩弓和磨牙转矩变化导致的间隙变化，正值表示需要间隙，负值表示产生间隙。
    - D1: 上颌Bolton指数调整产生的间隙，负值表示产生间隙。
    - D2: 下颌Spee曲线整平所需间隙，正值表示需要间隙。
    - E2: 下颌Bolton指数调整产生的间隙，负值表示产生间隙。

    返回:
    - 包含上下颌总间隙需求量的字典，键值分别为 "upper_total_space" 和 "lower_total_space"。
    """

    # 计算总间隙需求量
    upper_total_space = A1 + B1 + C1 + D1
    lower_total_space = A2 + B2 + C2 + D2 + E2

    return {
        "上颌总间隙需求量": f"{upper_total_space} mm",
        "下颌总间隙需求量": f"{lower_total_space} mm",
    }

calculate_total_space_requirement_tool = {
    "type": "function",
    "function": {
        "name": "calculate_total_space_requirement",
        "description": "根据前几个智能体提供的结果计算上下颌总间隙需求量。",
        "parameters": {
            "type": "object",
            "properties": {
                "A1": {"type": "number", "description": "上颌拥挤度 (mm)"},
                "A2": {"type": "number", "description": "下颌拥挤度 (mm)"},
                "B1": {"type": "number", "description": "上颌前牙垂直向和矢状向切牙目标位改变所需或提供的间隙 (mm)"},
                "B2": {"type": "number", "description": "下颌前牙垂直向和矢状向切牙目标位改变所需或提供的间隙 (mm)"},
                "C1": {"type": "number", "description": "上颌牙弓横向扩弓和磨牙转矩变化导致的间隙变化 (mm)"},
                "C2": {"type": "number", "description": "下颌牙弓横向扩弓和磨牙转矩变化导致的间隙变化 (mm)"},
                "D1": {"type": "number", "description": "上颌Bolton指数调整产生的间隙 (mm)"},
                "D2": {"type": "number", "description": "下颌Spee曲线整平所需间隙 (mm)"},
                "E2": {"type": "number", "description": "下颌Bolton指数调整产生的间隙 (mm)"},
            },
            "required": ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E2"],
            "additionalProperties": False,
        },
    },
}


# Agent 7 tool
def calculate_molar_space(
    upper_molar_space: float, lower_distal_to_ramus: float
) -> dict:
    """
    根据患者信息计算上下颌磨牙可用空间。

    参数:
    - upper_molar_space: 患者的上颌磨牙空间，从患者信息中提取 (mm)。
    - lower_distal_to_ramus: 下颌第二磨牙远中至下颌升支骨皮质的距离，从患者信息中提取 (mm)。

    返回:
    - 包含上颌可用骨量空间和下颌可用骨量空间的字典，键值分别为 "upper_available_space" 和 "lower_available_space"。
    """

    # 计算下颌远中骨量
    lower_available_space = (0.715 * lower_distal_to_ramus) - 0.22

    # 上颌远中骨量直接来自输入
    upper_available_space = upper_molar_space

    return {
        "上颌可用骨量空间": f"{upper_available_space} mm",
        "下颌可用骨量空间": f"{lower_available_space} mm",
    }


calculate_molar_space_tool = {
    "type": "function",
    "function": {
        "name": "calculate_molar_space",
        "description": "根据患者信息计算上下颌磨牙可用空间。",
        "parameters": {
            "type": "object",
            "properties": {
                "upper_molar_space": {
                    "type": "number",
                    "description": "患者的上颌磨牙空间 (mm)",
                },
                "lower_distal_to_ramus": {
                    "type": "number",
                    "description": "下颌第二磨牙远中至下颌升支骨皮质的距离 (mm)",
                },
            },
            "required": ["upper_molar_space", "lower_distal_to_ramus"],
            "additionalProperties": False,
        },
    },
}


def sum_floats(*args: float) -> float:
    return sum(args)


sum_floats_tool = {
    "type": "function",
    "function": {
        "name": "sum_floats",
        "description": "Calculate the sum of an arbitrary number of float values. Call this whenever you need to sum up a list of numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "description": "An array of float values to sum.",
                    "items": {"type": "number", "format": "float"},
                }
            },
            "required": ["values"],
            "additionalProperties": False,
        },
    },
}
