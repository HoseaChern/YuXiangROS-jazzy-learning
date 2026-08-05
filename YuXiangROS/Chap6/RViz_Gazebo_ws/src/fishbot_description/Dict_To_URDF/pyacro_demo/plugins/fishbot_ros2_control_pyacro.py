"""
fishbot.ros2_control.xacro

对应 urdf/fishbot/fishbot.ros2_control.xacro，
用 Python 字典描述 ros2_control 硬件系统与 Gazebo 侧 controller_manager 插件。

[控制方式切换说明]
该配置与 gazebo_control_plugin_pyacro.py 不可同时启用，二者会争夺同一组
轮子关节（left_wheel_joint / right_wheel_joint）。
当前默认启用本配置；如需切换为 Gazebo 原生差速控制，请在 fishbot_pyacro.py
中注释掉本模块相关代码，并启用 gazebo_control_plugin_pyacro。
"""


def make_fishbot_ros2_control() -> dict:
    """返回 ros2_control 与对应 Gazebo 插件字典，与 xacro 宏一一对应。

    Returns:
        {
            "ros2_control": <ros2_control> 元素字典,
            "gazebo_plugin": <gazebo> 包裹的 gz_ros2_control 插件字典
        }
    """
    return {
        "ros2_control": {
            "name": "FishBotGazeboSystem",
            "type": "system",
            "hardware": {
                "plugin": "gz_ros2_control/GazeboSimSystem",
            },
            "joints": [
                _make_wheel_joint("left_wheel_joint"),
                _make_wheel_joint("right_wheel_joint"),
                # [修改说明] 2026-07-26: 跟随 xacro 更新，为万向轮 swivel 关节增加
                #           状态接口，使 joint_state_broadcaster 能发布其位置/速度。
                _make_caster_swivel_joint("front_caster_swivel_joint"),
                _make_caster_swivel_joint("back_caster_swivel_joint"),
            ],
        },
        "gazebo_plugin": {
            "plugin": {
                "@filename": "gz_ros2_control-system",
                "@name": "gz_ros2_control::GazeboSimROS2ControlPlugin",
                "parameters": "$(find fishbot_description)/config/ros2_controller/fishbot_ros2_controller.yaml",
            }
        },
    }


def _make_wheel_joint(joint_name: str) -> dict:
    """生成单个轮子的 ros2_control <joint> 字典。"""
    return {
        "name": joint_name,
        "command_interfaces": [
            {
                "name": "velocity",
                "params": {"min": -1, "max": 1},
            },
            {
                "name": "effort",
                "params": {"min": -0.1, "max": 0.1},
            },
        ],
        "state_interfaces": [
            "position",
            "velocity",
            "effort",
        ],
    }


def _make_caster_swivel_joint(joint_name: str) -> dict:
    """生成万向轮 swivel 关节的 ros2_control <joint> 字典。

    swivel 关节为被动关节，只提供状态接口，不接收命令。
    """
    return {
        "name": joint_name,
        "state_interfaces": [
            "position",
            "velocity",
        ],
    }
