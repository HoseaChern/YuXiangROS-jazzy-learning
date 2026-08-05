"""
gazebo_control_plugin.xacro

对应 urdf/fishbot/plugins/gazebo_control_plugin.xacro，
用 Python 字典描述 Gazebo Harmonic 原生差速驱动与关节状态发布插件。

[控制方式切换说明]
该插件与 fishbot_ros2_control_pyacro.py 不可同时启用，二者会争夺同一组
轮子关节（left_wheel_joint / right_wheel_joint）。
当前默认不启用本插件；如需使用 Gazebo 原生差速控制，请在 fishbot_pyacro.py
中取消注释对应代码，并禁用 ros2_control。
"""


def make_gazebo_control_plugin() -> list:
    """返回 Gazebo 原生差速控制插件字典列表，与 xacro 宏一一对应。"""
    return [
        {
            "plugin": {
                "@filename": "gz-sim-diff-drive-system",
                "@name": "gz::sim::systems::DiffDrive",
                "topic": "/cmd_vel",
                "odom_topic": "/odom",
                "tf_topic": "/tf",
                "left_joint": "left_wheel_joint",
                "right_joint": "right_wheel_joint",
                "wheel_separation": 0.2,
                "wheel_radius": 0.032,
                "frame_id": "odom",
                "child_frame_id": "base_footprint",
                "odom_publish_frequency": 30,
            }
        },
        {
            "plugin": {
                "@filename": "gz-sim-joint-state-publisher-system",
                "@name": "gz::sim::systems::JointStatePublisher",
                "topic": "/joint_states",
                "joint_name": [
                    "left_wheel_joint",
                    "right_wheel_joint",
                ],
            }
        },
    ]
