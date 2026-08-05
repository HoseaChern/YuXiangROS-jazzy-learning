"""
wheel.urdf.xacro
"""

import sys

sys.path.append("..")
import comman_inertia


def make_wheel_link(wheel_name: str, xyz: list) -> tuple:
    link = {
        "name": f"{wheel_name}_wheel_link",
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [1.57079, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": 0.04,
                "radius": 0.032,
            },
            "material": {
                "name": "yellow",
                "color": [1, 1, 0, 0.8],
            },
        },
        "collision": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [1.57079, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": 0.04,
                "radius": 0.032,
            },
            "material": {
                "name": "yellow",
                "color": [1, 1, 0, 0.8],
            },
        },
        "inertial": {
            # [修改说明] 2026-07-26: 跟随 xacro 更新，车轮质量从 0.01 改为 0.15，
            #           满足"车轮质量至少为 1/10 车身质量"的设定。
            "mass": 0.15,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.cylinder_inertia(0.15, 0.032, 0.04),
        },
    }
    joint = {
        "name": f"{wheel_name}_wheel_joint",
        "type": "continuous",
        "parent": "base_link",
        "child": f"{wheel_name}_wheel_link",
        # [修改说明] 2026-07-26: 修正 origin 内容，与 xacro 一致只保留 xyz；
        #           旋转轴信息由 axis 字段表达，不应放在 origin 中。
        "origin": {
            "xyz": xyz,
        },
        "axis": [0, 1, 0],
    }
    return link, joint


def make_wheel_gazebo_params(wheel_name: str) -> dict:
    """返回 wheel_xacro 中定义的 Gazebo 摩擦参数，与 xacro 一一对应。"""
    return {
        "reference": f"{wheel_name}_wheel_link",
        # [说明] xacro 中使用 <mu1 value="20.0"/> 形式，
        #        因此 pyacro 用 {"@value": ...} 生成属性写法。
        "mu1": {"@value": 20.0},
        "mu2": {"@value": 20.0},
        # [修改说明] 2026-07-26: 跟随 xacro 更新，kp 从 1000000000000.0 改为 100000.0。
        "kp": {"@value": 100000.0},
        "kd": {"@value": 1.0},
    }
