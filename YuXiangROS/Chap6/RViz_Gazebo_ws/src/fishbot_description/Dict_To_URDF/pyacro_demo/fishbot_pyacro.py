"""
fishbot.urdf.xacro
"""

import sys

from actuator.caster_pyacro import make_caster_gazebo_params, make_caster_link
from actuator.wheel_pyacro import make_wheel_gazebo_params, make_wheel_link
from base_pyacro import make_base_link
from plugins.fishbot_ros2_control_pyacro import make_fishbot_ros2_control
from plugins.gazebo_sensor_plugin_pyacro import make_gazebo_sensor_plugin
from sensor.camera_pyacro import make_camera_link
from sensor.imu_pyacro import make_imu_link
from sensor.laser_pyacro import make_laser_gazebo_materials, make_laser_links

sys.path.append("..")
from json_to_urdf import convert

# [控制方式切换说明]
# gazebo_control_plugin_pyacro 与 fishbot_ros2_control_pyacro 会争夺同一组
# 轮子关节，因此二者不可同时启用。
# from plugins.gazebo_control_plugin_pyacro import make_gazebo_control_plugin

links = []
joints = []
gazebo = []
ros2_control = []

base_link, footprint_link, footprint_joint = make_base_link(length=0.12, radius=0.1)
imu_link, imu_joint = make_imu_link(xyz=[0, 0, 0.02])
# [说明] 调用顺序与 xacro 中 base -> imu -> laser -> camera -> wheel -> caster 保持一致，
#        使 pyacro 生成的 URDF 元素顺序与 xacro 输出一致，便于对比。
cylinder_link, cylinder_joint, laser_link, laser_joint = make_laser_links(
    xyz=[0, 0, 0.10]
)
camera_link, camera_joint = make_camera_link(xyz=[0.10, 0, 0.075])
left_wheel_link, left_wheel_joint = make_wheel_link(
    wheel_name="left",
    xyz=[0, 0.10, -0.06],
)
right_wheel_link, right_wheel_joint = make_wheel_link(
    wheel_name="right",
    xyz=[0, -0.10, -0.06],
)
(
    front_caster_swivel_link,
    front_caster_swivel_joint,
    front_caster_link,
    front_caster_wheel_joint,
) = make_caster_link(
    caster_name="front",
    xyz=[0.08, 0, -0.076],
)
(
    back_caster_swivel_link,
    back_caster_swivel_joint,
    back_caster_link,
    back_caster_wheel_joint,
) = make_caster_link(
    caster_name="back",
    xyz=[-0.08, 0, -0.076],
)

links.extend(
    [
        base_link,
        footprint_link,
        imu_link,
        cylinder_link,
        laser_link,
        camera_link,
        left_wheel_link,
        right_wheel_link,
        # [修改说明] 2026-07-26: 跟随 xacro 更新，增加万向轮 swivel 支架 link。
        front_caster_swivel_link,
        front_caster_link,
        back_caster_swivel_link,
        back_caster_link,
    ]
)
joints.extend(
    [
        footprint_joint,
        imu_joint,
        cylinder_joint,
        laser_joint,
        camera_joint,
        left_wheel_joint,
        right_wheel_joint,
        # [修改说明] 2026-07-26: 跟随 xacro 更新，增加万向轮 swivel 关节与
        #           caster_wheel_joint（球体到支架的固定关节）。
        front_caster_swivel_joint,
        front_caster_wheel_joint,
        back_caster_swivel_joint,
        back_caster_wheel_joint,
    ]
)

# 传感器插件：两种控制方式都需要，始终启用
gazebo.extend(make_gazebo_sensor_plugin())

# laser_xacro 中定义的 Gazebo 仿真材质（支撑杆与雷达本体设为黑色）
gazebo.extend(make_laser_gazebo_materials())

# wheel / caster 的 Gazebo 摩擦参数，与 xacro 中一一对应
gazebo.append(make_wheel_gazebo_params("left"))
gazebo.append(make_wheel_gazebo_params("right"))
gazebo.append(make_caster_gazebo_params("front"))
gazebo.append(make_caster_gazebo_params("back"))

# [控制方式切换说明]
# 方式 B (默认): ros2_control
# 由 diff_drive_controller 处理 /cmd_vel，joint_state_broadcaster 发布 /joint_states，
# 不再需要 ros_gz_bridge 桥接这些话题。
ros2_control_part = make_fishbot_ros2_control()
ros2_control.append(ros2_control_part["ros2_control"])
gazebo.append(ros2_control_part["gazebo_plugin"])

# 方式 A: Gazebo 原生差速插件
# 如需切换，请取消下面两行注释，并注释掉上方 ros2_control 相关代码。
# gazebo.extend(make_gazebo_control_plugin())

robot_dict = {
    "name": "fishbot",
    "links": links,
    "joints": joints,
    "gazebo": gazebo,
    "ros2_control": ros2_control,
}
convert(robot_dict, output="fishbot.urdf")
