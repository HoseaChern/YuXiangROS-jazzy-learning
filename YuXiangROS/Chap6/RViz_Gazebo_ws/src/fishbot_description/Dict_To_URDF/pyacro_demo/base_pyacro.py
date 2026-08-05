"""
base.urdf.xacro
"""

import comman_inertia


def make_base_link(length: float, radius: float) -> tuple:
    footprint_link = {
        "name": "base_footprint",
    }

    link = {
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
        "collision": {
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
        "inertial": {
            "mass": 1.0,
            "origin": {
                "xyz": [0, 0, 0],
                "rpy": [0, 0, 0],
            },
            "inertia": comman_inertia.cylinder_inertia(1.0, radius, length),
        },
    }

    footprint_joint = {
        "name": "base_joint",
        "type": "fixed",
        "parent": "base_footprint",
        "child": "base_link",
        "origin": {
            "xyz": [
                0,
                0,
                length / 2.0 + 0.032 - 0.001,
            ],
            "rpy": [0, 0, 0],
        },
    }
    return link, footprint_link, footprint_joint
