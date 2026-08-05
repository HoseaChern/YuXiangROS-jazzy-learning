"""
1. 命令行发布静态坐标变换关系
ros2 run tf2_ros static_transform_publisher --x 0.1 --y 0.2 --z 0.3 --roll 0.0 --pitch 0.0 --yaw 0.0 --frame-id base_link --child-frame-id base_laser
2. 使用命令行计算坐标系变换关系
ros2 run tf2_ros tf2_echo base_link wall_point
3. 查看坐标系连接关系(生成 PDF 和 GV)
ros2 run tf_tool view_frames
"""

# 角度与弧度转换
import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from tf_transformations import quaternion_from_euler


class StaticTFBroadcaster(Node):
    def __init__(self):
        super().__init__("static_tf2_broadcaster")

        # 创建静态坐标转换广播器
        self.static_broadcaster_ = StaticTransformBroadcaster(self)
        self.publish_static_tf()

    def publish_static_tf(self):
        # 创建静态坐标转换消息
        transform = TransformStamped()

        # 获取当前时间并转换为消息时间戳
        transform.header.stamp = self.get_clock().now().to_msg()
        # 父坐标系名称
        transform.header.frame_id = "base_link"
        # 子坐标系名称
        transform.child_frame_id = "camera_link"

        # 空间平移
        transform.transform.translation.x = 0.5
        transform.transform.translation.y = 0.3
        transform.transform.translation.z = 0.6

        # 空间旋转
        # 旋转180度，绕x轴; 转换为四元数
        rotation_quat = quaternion_from_euler(math.radians(180), 0, 0)
        transform.transform.rotation.x = rotation_quat[0]
        transform.transform.rotation.y = rotation_quat[1]
        transform.transform.rotation.z = rotation_quat[2]
        transform.transform.rotation.w = rotation_quat[3]

        # 发布静态坐标转换消息
        self.static_broadcaster_.sendTransform(transform)
        self.get_logger().info(f"Publish TF: {transform}")


def main(args=None):
    rclpy.init(args=args)
    node = StaticTFBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
