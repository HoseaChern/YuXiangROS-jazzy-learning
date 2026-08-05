"""
imu.urdf.xacro
"""

import sys

sys.path.append("..")
import comman_inertia


def make_imu_link(xyz: list) -> tuple:
    link = {
        "name": "imu_link",
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
                "color": [0, 0, 0, 0.8],
            },
        },
        "collision": {
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
                "color": [0, 0, 0, 0.8],
            },
        },
        "inertial": {
            "mass": 0.25,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.box_inertia(0.25, 0.02, 0.02, 0.02),
        },
    }
    joint = {
        "name": "imu_joint",
        "type": "fixed",
        "parent": "base_link",
        "child": "imu_link",
        # [说明] 与 xacro 一致，origin 只保留 xyz。
        "origin": {
            "xyz": xyz,
        },
    }
    return link, joint
