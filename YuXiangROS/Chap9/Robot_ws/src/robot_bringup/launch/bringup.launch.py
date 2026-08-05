from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    fishbot_bringup_dir = get_package_share_directory("robot_bringup")
    ydlidar_ros2_dir = get_package_share_directory("ydlidar_ros2")

    urdf2tf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                fishbot_bringup_dir,
                "/launch",
                "/urdf2tf.launch.py",
            ]
        )
    )

    odom2tf = Node(
        package="robot_bringup",
        executable="odom2tf",
        output="screen",
    )

    micro_ros_agent = Node(
        package="micro_ros_agent",  # 注意: 其repo名为micro-ROS-Agent, package名为micro_ros_agent; package名详见package.xml
        executable="micro_ros_agent",
        arguments=[
            "udp4",
            "--port",
            "8888",
        ],
        output="screen",
    )

    ros_serial2wifi = Node(
        package="ros_serial2wifi",
        executable="tcp_server",
        parameters=[{"serial_port": "/tmp/tty_laser"}],
        output="screen",
    )

    ydlidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                ydlidar_ros2_dir,
                "/launch",
                "/ydlidar_launch.py",
            ]
        )
    )
    ydlidar_delay = TimerAction(period=5.0, actions=[ydlidar])

    launch_description = LaunchDescription(
        [
            urdf2tf,
            odom2tf,
            micro_ros_agent,
            ros_serial2wifi,
            ydlidar_delay,
        ]
    )

    return launch_description
