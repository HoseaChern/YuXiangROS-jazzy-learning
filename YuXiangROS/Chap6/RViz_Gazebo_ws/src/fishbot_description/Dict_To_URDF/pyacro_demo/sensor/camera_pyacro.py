"""
camera.urdf.xacro
"""

import sys

sys.path.append("..")
import comman_inertia


def make_camera_link(xyz: list) -> tuple:
    link = {
        "name": "camera_link",
        "visual": {
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "geometry": {
                "type": "box",
                "size": [0.02, 0.10, 0.02],
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
                "type": "box",
                "size": [0.02, 0.10, 0.02],
            },
            "material": {
                "name": "green",
                "color": [0, 1, 0, 0.8],
            },
        },
        "inertial": {
            "mass": 0.5,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.box_inertia(0.5, 0.02, 0.10, 0.02),
        },
    }
    joint = {
        "name": "camera_joint",
        "type": "fixed",
        "parent": "base_link",
        "child": "camera_link",
        # [说明] 与 xacro 一致，origin 只保留 xyz。
        "origin": {
            "xyz": xyz,
        },
    }
    return link, joint
