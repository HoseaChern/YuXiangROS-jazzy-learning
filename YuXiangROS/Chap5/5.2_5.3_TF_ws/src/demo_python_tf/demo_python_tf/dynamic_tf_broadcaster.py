import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler


class DynamicTFBroadcaster(Node):
    def __init__(self):
        super().__init__("dynamic_tf2_broadcaster")

        # 创建动态坐标转换广播器
        self.dynamic_broadcaster_ = TransformBroadcaster(self)
        # 创建定时器，每0.01秒(100Hz)发布一次动态坐标转换消息
        self.timer_ = self.create_timer(0.01, self.publish_dynamic_tf)

    def publish_dynamic_tf(self):
        # 创建动态坐标转换消息
        transform = TransformStamped()

        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = "camera_link"
        transform.child_frame_id = "bottle_link"

        transform.transform.translation.x = 0.2
        transform.transform.translation.y = 0.0
        transform.transform.translation.z = 0.5

        rotation_quat = quaternion_from_euler(0, 0, 0)
        transform.transform.rotation.x = rotation_quat[0]
        transform.transform.rotation.y = rotation_quat[1]
        transform.transform.rotation.z = rotation_quat[2]
        transform.transform.rotation.w = rotation_quat[3]

        # 发布动态坐标转换消息
        self.dynamic_broadcaster_.sendTransform(transform)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicTFBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
