"""
caster.urdf.xacro
"""

import sys

sys.path.append("..")
import comman_inertia


def make_caster_link(caster_name: str, xyz: list) -> tuple:
    """返回万向轮相关 link 与 joint 的字典，与 xacro 宏一一对应。

    [修改说明] 2026-07-26: 跟随 xacro 更新，为万向轮增加 swivel 支架与转向关节，
               使万向轮在仿真中能自由随转向旋转；同时修正 kp 为 100000.0。

    Returns:
        (
            caster_swivel_link,      # 万向轮支架
            caster_swivel_joint,     # 垂直转向关节 (continuous)
            caster_link,             # 万向轮球体
            caster_wheel_joint,      # 球体到支架的固定关节
        )
    """
    swivel_link = {
        "name": f"{caster_name}_caster_swivel_link",
        "inertial": {
            "mass": 0.01,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": [
                1e-6, 0, 0,
                1e-6, 0,
                1e-6,
            ],
        },
    }

    # 垂直转向关节：让万向轮能随转向自由旋转
    swivel_joint = {
        "name": f"{caster_name}_caster_swivel_joint",
        "type": "continuous",
        "parent": "base_link",
        "child": f"{caster_name}_caster_swivel_link",
        # [说明] 与 xacro 一致，origin 只保留 xyz，旋转轴由 axis 表达。
        "origin": {
            "xyz": xyz,
        },
        "axis": [0, 0, 1],
    }

    caster_ball_link = {
        "name": f"{caster_name}_caster_link",
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "sphere",
                "radius": 0.016,
            },
            "material": {
                "name": "yellow",
                "color": [1, 1, 0, 0.8],
            },
        },
        "collision": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "sphere",
                "radius": 0.016,
            },
            "material": {
                "name": "yellow",
                "color": [1, 1, 0, 0.8],
            },
        },
        "inertial": {
            "mass": 0.01,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.sphere_inertia(0.01, 0.016),
        },
    }

    # 球体连到支架上
    caster_wheel_joint = {
        "name": f"{caster_name}_caster_wheel_joint",
        "type": "fixed",
        "parent": f"{caster_name}_caster_swivel_link",
        "child": f"{caster_name}_caster_link",
        # [说明] 与 xacro 一致，origin 只保留 xyz。
        "origin": {
            "xyz": [0, 0, 0],
        },
    }

    return swivel_link, swivel_joint, caster_ball_link, caster_wheel_joint


def make_caster_gazebo_params(caster_name: str) -> dict:
    """返回 caster_xacro 中定义的 Gazebo 摩擦参数，与 xacro 一一对应。"""
    return {
        "reference": f"{caster_name}_caster_link",
        # [说明] xacro 中使用 <mu1 value="0.0"/> 形式，
        #        因此 pyacro 用 {"@value": ...} 生成属性写法。
        # [修改说明] 2026-07-26: kp 从 1000000000000.0 同步为 xacro 的 100000.0。
        "mu1": {"@value": 0.0},
        "mu2": {"@value": 0.0},
        "kp": {"@value": 100000.0},
        "kd": {"@value": 1.0},
    }
