import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 获取功能包路径
    urdf_tutorial_path = get_package_share_directory("fishbot_description")
    # 获取默认 URDF/Xacro 路径 (总之是描述文件路径)
    default_model_path = os.path.join(urdf_tutorial_path, "urdf", "fishbot", "fishbot.urdf.xacro")
    # 获取当前RViz配置路径
    default_rviz_config_path = os.path.join(urdf_tutorial_path, "config", "rviz", "display_model.rviz")

    # 为路径声明 launch 参数
    action_declare_arg_mode_path = DeclareLaunchArgument(
        name="model",
        default_value=default_model_path,
        description="Absolute path to URDF file",
    )

    robot_description = ParameterValue(
        # 运行终端 cat 命令获取参数"model"对应路径文件的内容, 作为参数 robot_description 的值
        # 若是从.xacro解析, 则需要使用 xacro 命令(兼容 .urdf)
        # !每次修改后必须重新 colcon (避免方法: --symlink-install install/复制变为创建符号链接)
        Command(
            [
                "xacro ",
                LaunchConfiguration(
                    "model",
                    default=default_model_path,
                ),
            ]
        ),
        value_type=str,
    )

    # 状态发布节点
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        # 将 robot_description 参数传递给节点
        parameters=[{"robot_description": robot_description}],
    )

    # 关节状态发布节点
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
    )

    # RViz 节点
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        # 设定从当前RViz配置文件中加载配置
        arguments=["-d", default_rviz_config_path],
    )
    # 注意: parameters为ROS2参数服务调用, arguments是CLI终端指令选项

    launch_description = LaunchDescription(
        [
            action_declare_arg_mode_path,
            robot_state_publisher_node,
            joint_state_publisher_node,
            rviz_node,
        ]
    )

    return launch_description
