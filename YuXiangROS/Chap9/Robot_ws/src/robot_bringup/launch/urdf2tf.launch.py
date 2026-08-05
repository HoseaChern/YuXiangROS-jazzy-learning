import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 获取功能包路径
    urdf_tutorial_path = get_package_share_directory("robot_description")
    # 获取 URDF 路径
    fishbot_model_path = os.path.join(urdf_tutorial_path, "urdf/fishbot.urdf")

    # 声明路径参数
    action_declare_arg_mode_path = DeclareLaunchArgument(
        name="model",
        default_value=fishbot_model_path,
        description="Absolute path to URDF",
    )

    # 获取 URDF 内容以生成新的参数
    robot_description = ParameterValue(
        Command(
            [
                "cat ",
                LaunchConfiguration("model"),
            ]
        ),
        value_type=str,
    )

    # 状态发布节点
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    # 关节状态发布节点
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
    )

    launch_description = LaunchDescription(
        [
            action_declare_arg_mode_path,
            robot_state_publisher_node,
            joint_state_publisher_node,
        ]
    )

    return launch_description
