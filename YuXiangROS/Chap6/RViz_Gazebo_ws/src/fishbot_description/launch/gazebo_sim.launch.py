# [新增] 用于拼接控制器参数文件的绝对路径
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 仿真机器人名称
    robot_name_in_model = "fishbot"
    # 获取功能包路径
    urdf_tutorial_path = get_package_share_directory("fishbot_description")
    # 默认模型路径
    default_model_path = os.path.join(
        urdf_tutorial_path, "urdf", "fishbot", "fishbot.urdf.xacro"
    )
    # 默认世界路径, 旧版: .world
    default_world_path = os.path.join(urdf_tutorial_path, "world", "custom_room.sdf")

    # 为路径声明 launch 参数
    action_declare_arg_mode_path = DeclareLaunchArgument(
        name="model",
        default_value=default_model_path,
        description="Absolute path to URDF",
    )

    robot_description = ParameterValue(
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

    # [修改说明] 新增 use_sim_time: True
    # 原因: Gazebo Harmonic 发布 /clock 仿真时钟, robot_state_publisher 需要订阅该时钟,
    #       否则 TF 时间戳与 Gazebo 不一致, RViz 中会出现警告或显示异常。
    robot_state_publiser_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        # 将 robot_description 参数传递给节点
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
            }
        ],
    )

    # !========== Harmonic 改动 1: 启动 Gazebo Sim ==========
    launch_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                get_package_share_directory("ros_gz_sim"),  # 旧版: gazebo_ros
                "/launch",
                "/gz_sim.launch.py",  # 旧版: gazebo.launch.py
            ]
        ),
        launch_arguments=[
            # gz_args 格式: "-r -v 4 <world_path>"
            # -r: 运行即开始仿真; -v 4: verbose 级别
            # 旧版: [("world", "<path>"), ("verbose", "true")]
            ("gz_args", f"-r -v 4 {default_world_path}"),
        ],
    )

    # !========== Harmonic 改动 2: 生成实体 ==========
    spawn_entity_node = Node(
        package="ros_gz_sim",  # 旧版: gazebo_ros
        executable="create",  # 旧版: spawn_entity.py
        arguments=[
            "-topic",
            "/robot_description",
            "-name",  # 旧版: -entity
            robot_name_in_model,
        ],
        output="screen",
    )

    # !========== Harmonic 改动 3: 桥接器 <ros_topic_name>@<ros_msg_type><方向符号><gz_msg_type> ==========
    # [控制方式切换说明]
    # 本 launch 默认使用 ros2_control 控制小车, 此时以下 ROS 话题由控制器直接接管,
    # 不能再通过 ros_gz_bridge 桥接, 否则控制器与桥会同时发布/订阅同一话题, 导致冲突。
    #   方式 A: Gazebo 原生差速插件 (urdf/fishbot/plugins/gazebo_control_plugin.xacro)
    #           Gazebo 直接处理 /cmd_vel, 发布 /odom /tf /joint_states,
    #           这些话题必须通过 ros_gz_bridge 桥接。
    #   方式 B: ros2_control (urdf/fishbot/fishbot.ros2_control.xacro)
    #           diff_drive_controller 处理 /cmd_vel, 发布 /odom /tf,
    #           joint_state_broadcaster 发布 /joint_states,
    #           这些话题不再需要桥接。
    # 如需从方式 B 切换回方式 A, 请:
    #   1. 取消下面 4 条桥接注释;
    #   2. 在 urdf/fishbot/fishbot.urdf.xacro 中注释掉 fishbot.ros2_control.xacro,
    #      取消注释 gazebo_control_plugin.xacro;
    #   3. 注释掉本 launch 中的 twist_stamper_node 和两个控制器 spawner。
    """
    # 1. 启动仿真后，查看 Gazebo 侧发布了哪些 gz 话题
    gz topic -l

    # 2. 查看某个话题的消息类型
    gz topic -i -t /model/fishbot/odometry

    # 3. 查看该消息类型的详细定义
    gz msg -i gz.msgs.Odometry
    """

    brige = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # GZ → ROS: 仿真时钟, 由 Gazebo 仿真步长决定
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # -----------------------------------------------------------------
            # [ros2_control 方式下需注释] 以下 4 条由控制器接管, 桥接会导致话题冲突。
            # [Gazebo 原生插件方式下需启用] 取消注释后, Gazebo 与 ROS 通过这些话题通信。
            # -----------------------------------------------------------------
            # ROS → GZ: 键盘/节点发 Twist 速度指令给 Gazebo
            # "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            # GZ → ROS: Gazebo 发里程计给 ROS
            # "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            # GZ → ROS: Gazebo 发 TF 给 ROS
            # "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            # GZ → ROS: Gazebo 发关节状态给 ROS
            # "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
            # -----------------------------------------------------------------
            # [传感器数据] 两种控制方式都需要, 继续桥接, 频率由 Gazebo 传感器插件配置决定
            # -----------------------------------------------------------------
            # GZ → ROS: 激光雷达扫描数据
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            # GZ → ROS: IMU 数据
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            # GZ → ROS: 相机彩色图像
            "/camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            # GZ → ROS: 相机深度图像
            "/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
            # GZ → ROS: 相机内参
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            # GZ → ROS: 相机点云
            "/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        output="screen",
    )

    # !========== 新增: ros2_control 控制器参数文件路径 ==========
    # [说明] Jazzy 的 controller_manager spawner 必须通过 --param-file 显式指定参数文件,
    #        否则控制器只使用默认参数, 不会读取 yaml 配置。
    controller_params_file = os.path.join(
        urdf_tutorial_path,
        "config",
        "ros2_controller",
        "fishbot_ros2_controller.yaml",
    )

    # !========== 新增: 使用 controller_manager 的 spawner 加载关节状态广播器 ==========
    # [说明] 等机器人实体(spawn_entity_node)创建完成后, 按顺序加载控制器。
    # --controller-manager-timeout 30: 等待 /controller_manager 服务就绪, 避免启动时序问题。
    # --param-file: 指定控制器参数文件, 使控制器读取 yaml 中的具体配置。
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "fishbot_joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
            "--param-file",
            controller_params_file,
        ],
        output="screen",
    )

    # !========== 新增: 使用 controller_manager 的 spawner 加载差速控制器 ==========
    # [说明] Jazzy 的 diff_drive_controller 已移除 use_stamped_vel 参数,
    #        强制订阅 geometry_msgs/msg/TwistStamped。
    # --controller-ros-args: 将控制器默认订阅的 ~/cmd_vel remap 到 /cmd_vel_stamped,
    #                        由 twist_stamper 负责把 /cmd_vel (Twist) 转换过来。
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "fishbot_diff_drive_controller",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "30",
            "--param-file",
            controller_params_file,
            "--controller-ros-args",
            "-r /fishbot_diff_drive_controller/cmd_vel:=/cmd_vel_stamped",
        ],
        output="screen",
    )

    # !========== 新增: Jazzy 适配 twist_stamper ==========
    # [说明] teleop_twist_keyboard 发布 geometry_msgs/msg/Twist,
    #        Jazzy 的 diff_drive_controller 需要 geometry_msgs/msg/TwistStamped,
    #        因此启动 twist_stamper 做消息类型转换。
    # [注意] cmd_vel_in / cmd_vel_out 是 twist_stamper 内部话题名, 必须用 remappings 映射,
    #        不能写成 parameters。
    twist_stamper_node = Node(
        package="twist_stamper",
        executable="twist_stamper",
        parameters=[{"frame_id": "base_link"}],
        remappings=[
            ("cmd_vel_in", "/cmd_vel"),
            ("cmd_vel_out", "/cmd_vel_stamped"),
        ],
    )

    # $如果发生改了代码没效果: 请执行
    # $killall -9 gz sim ruby robot_state_publisher 2>/dev/null; ros2 daemon stop
    # $杀死残余进程

    # $观察仿真启动错误信息
    # $ros2 launch fishbot_description gazebo_sim.launch.py 2>&1 | grep -i "error\|warn"
    launch_description = LaunchDescription(
        [
            action_declare_arg_mode_path,
            robot_state_publiser_node,
            launch_gazebo,
            spawn_entity_node,
            brige,
            # [说明] twist_stamper 需要在差速控制器启动前运行,
            #        因此直接加入 LaunchDescription, 不通过事件触发。
            twist_stamper_node,
            # 事件动作: 实体创建完成后, 先加载并激活 joint_state_broadcaster
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=spawn_entity_node,
                    on_exit=[joint_state_broadcaster_spawner],
                )
            ),
            # 事件动作: joint_state_broadcaster 激活后, 再加载并激活差速控制器
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster_spawner,
                    on_exit=[diff_drive_controller_spawner],
                )
            ),
        ]
    )

    return launch_description
