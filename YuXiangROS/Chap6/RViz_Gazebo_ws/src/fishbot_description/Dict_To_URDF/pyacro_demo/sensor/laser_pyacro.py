"""
laser.urdf.xacro
"""

import sys

sys.path.append("..")
import comman_inertia


def make_laser_links(xyz: list) -> tuple:
    cylinder_link = {
        "name": "laser_cylinder_link",
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": 0.10,
                "radius": 0.01,
            },
            "material": {
                "name": "green",
                "color": [0, 1, 0, 0.8],
            },
        },
        "collision": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": 0.10,
                "radius": 0.01,
            },
            "material": {
                "name": "green",
                "color": [0, 1, 0, 0.8],
            },
        },
        "inertial": {
            "mass": 0.01,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.cylinder_inertia(0.01, 0.01, 0.10),
        },
    }
    cylinder_joint = {
        "name": "laser_cylinder_joint",
        "type": "fixed",
        "parent": "base_link",
        "child": "laser_cylinder_link",
        # [说明] 与 xacro 一致，origin 只保留 xyz。
        "origin": {
            "xyz": xyz,
        },
    }
    laser_link = {
        "name": "laser_link",
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": 0.02,
                "radius": 0.02,
            },
            "material": {
                "name": "green",
                "color": [0, 1, 0, 0.8],
            },
        },
        "collision": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "cylinder",
                "length": 0.02,
                "radius": 0.02,
            },
            "material": {
                "name": "green",
                "color": [0, 1, 0, 0.8],
            },
        },
        "inertial": {
            "mass": 0.05,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.cylinder_inertia(0.05, 0.02, 0.02),
        },
    }
    laser_joint = {
        "name": "laser_joint",
        "type": "fixed",
        "parent": "laser_cylinder_link",
        "child": "laser_link",
        # [说明] 与 xacro 一致，origin 只保留 xyz。
        "origin": {
            "xyz": [0, 0, 0.05],
        },
    }
    return cylinder_link, cylinder_joint, laser_link, laser_joint


def make_laser_gazebo_materials() -> list:
    """返回 laser_xacro 中定义的 Gazebo 仿真材质，与 xacro 一一对应。

    xacro 中为激光雷达支撑杆和雷达本体分别设置了黑色 Harmonic 材质。
    """
    black_material = {
        "visual": {
            "material": {
                "ambient": "0 0 0 1",
                "diffuse": "0 0 0 1",
                "specular": "0.1 0.1 0.1 1",
                "emissive": "0.0 0.0 0.0 1.0",
            }
        }
    }
    return [
        {"reference": "laser_cylinder_link", **black_material},
        {"reference": "laser_link", **black_material},
    ]
