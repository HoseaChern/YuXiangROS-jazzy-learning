"""
launch文件可以批量启动多个节点
可以使用的语言: Python/XML/YAML

1. ros2 launch demo_cpp_service demo.launch.py 从launch文件启动多个节点
2. ros2 launch demo_cpp_service demo.launch.py launch_max_speed:=3.0 指定参数值启动节点
"""

# Python 自身的启动库
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

# ROS2 在 launch 基础上的扩展库
from launch_ros.actions import Node


def generate_launch_description():
    # 声明参数, 用于解析 launch 命令后的参数
    action_declare_arg_max_speed = DeclareLaunchArgument(
        "launch_max_speed",
        # 命令行直接调用当前 launch 是使用的默认值
        default_value="2.0",
    )

    # 启动 turtle_control 节点
    action_node_turtle_control = Node(
        package="demo_cpp_service",  # 功能包名
        executable="turtle_control",  # 可执行文件名
        output="screen",  # 输出类型: screen屏幕, log日志, both合并
        # 使用 launch 中 launch_max_speed 替换节点中 max_speed
        parameters=[
            {
                "max_speed": LaunchConfiguration(
                    "launch_max_speed",
                    # 命令行被其他 launch 简介调用时"可能"起作用的默认值
                    default="2.0",
                )
            }
        ],
    )

    # 启动 patrol_client 节点
    action_node_patrol_client = Node(
        package="demo_cpp_service",
        executable="patrol_client",
        output="log",
    )

    # 启动 turtlesim_node 节点
    action_node_turtlesim_node = Node(
        package="turtlesim",
        executable="turtlesim_node",
        output="both",
    )

    # 总的启动描述
    launch_description = LaunchDescription(
        [
            action_declare_arg_max_speed,  # 声明参数
            action_node_turtle_control,
            action_node_patrol_client,
            action_node_turtlesim_node,
        ]
    )

    return launch_description
