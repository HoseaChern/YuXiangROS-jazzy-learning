import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    autopatrol_robot_dir = get_package_share_directory("autopatrol_robot")
    patrol_config_path = os.path.join(autopatrol_robot_dir, "config", "patrol_config.yaml")

    action_node_patrol_server = Node(
        package="autopatrol_robot",
        executable="speaker",
    )

    action_node_patrol_client = Node(
        package="autopatrol_robot",
        executable="patrol_node",
        parameters=[patrol_config_path],
    )

    launch_description = LaunchDescription(
        [
            action_node_patrol_server,
            action_node_patrol_client,
        ]
    )

    return launch_description
