import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 获取与拼接默认路径
    fishbot_navigation2_dir = get_package_share_directory("fishbot_navigation2")
    nav2_bringup_dir = get_package_share_directory("nav2_bringup")
    rviz_config_dir = os.path.join(fishbot_navigation2_dir, "config", "nav2_fishbot_view.rviz")

    # 配置默认参数值
    use_sim_time = LaunchConfiguration(
        "use_sim_time",
        default="true",
    )

    map_yaml_path = LaunchConfiguration(
        "map",
        default=os.path.join(fishbot_navigation2_dir, "maps", "room.yaml"),
    )

    nav2_param_path = LaunchConfiguration(
        "params_file",
        default=os.path.join(fishbot_navigation2_dir, "config", "nav2_params.yaml"),
    )

    # 声明 launch 参数
    action_declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value=use_sim_time,
        description="Use simulation (Gazebo) clock if true",
    )

    action_declare_map_yaml_path = DeclareLaunchArgument(
        "map",
        default_value=map_yaml_path,
        description="Absolute path to map file to load",
    )

    action_declare_nav2_param_path = DeclareLaunchArgument(
        "params_file",
        default_value=nav2_param_path,
        description="Absolute path to param file to load",
    )

    launch_navigation2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                nav2_bringup_dir,
                "/launch",
                "/bringup_launch.py",
            ]
        ),
        # 使用 launch 参数替换原参数
        launch_arguments={
            "use_sim_time": use_sim_time,
            "map": map_yaml_path,
            "params_file": nav2_param_path,
        }.items(),
    )

    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=[
            "-d",
            rviz_config_dir,
        ],
        parameters=[
            {"use_sim_time": use_sim_time},
        ],
        output="screen",
    )

    launch_description = LaunchDescription(
        [
            action_declare_use_sim_time,
            action_declare_map_yaml_path,
            action_declare_nav2_param_path,
            launch_navigation2,
            rviz2_node,
        ]
    )

    return launch_description
