#!/usr/bin/env python3
"""
用 Python 模拟 Xacro 宏 —— 对应书本示例: first_robot.urdf.xacro
Xacro: base_link + imu_link 宏的 Python 等效实现
"""

from json_to_urdf import convert  # 需要 json_to_urdf.py 在同目录

# ========== 宏定义（模拟 xacro:macro）==========


def make_base_link(length: float, radius: float) -> dict:
    """模拟 <xacro:macro name="base_link" params="length radius">"""
    return {
        "name": "base_link",
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": length,
                "radius": radius,
            },
            "material": {
                "name": "white",
                "color": [1.0, 1.0, 1.0, 0.5],
            },
        },
    }


def make_imu_link(imu_name: str, xyz: list) -> tuple:
    """
    模拟 <xacro:macro name="imu_link" params="imu_name xyz">
    返回 (link_dict, joint_dict)
    """
    link_name = f"{imu_name}_link"
    joint_name = f"{imu_name}_joint"

    link = {
        "name": link_name,
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "box",
                "size": [0.02, 0.02, 0.02],
            },
            "material": {
                "name": "black",
                "color": [0, 0, 0, 0.5],
            },
        },
    }

    joint = {
        "name": joint_name,
        "type": "fixed",
        "parent": "base_link",
        "child": link_name,
        "origin": {
            "xyz": xyz,
            "rpy": [0, 0, 0],
        },
    }

    return link, joint


# ========== 宏调用（模拟 <xacro:base_link .../>）==========

links = []
joints = []

# <xacro:base_link length="0.12" radius="0.1" />
links.append(make_base_link(length=0.12, radius=0.1))

# <xacro:imu_link imu_name="imu_up" xyz="0 0 0.02" />
link_up, joint_up = make_imu_link(imu_name="imu_up", xyz=[0, 0, 0.02])
links.append(link_up)
joints.append(joint_up)

# <xacro:imu_link imu_name="imu_down" xyz="0 0 -0.02" />
link_down, joint_down = make_imu_link(imu_name="imu_down", xyz=[0, 0, -0.02])
links.append(link_down)
joints.append(joint_down)

# 组装
robot_dict = {"name": "first_robot", "links": links, "joints": joints}

# ========== 生成 URDF ==========
convert(robot_dict, output="Python_Xacro_demo.urdf")
print("✓ 已生成 Python_Xacro_demo.urdf")
