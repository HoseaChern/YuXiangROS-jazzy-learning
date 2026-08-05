import rclpy
from rclpy.node import Node
from rclpy.time import Duration, Time
from tf2_ros import Buffer, TransformListener
from tf_transformations import euler_from_quaternion


class TFListener(Node):
    def __init__(self):
        super().__init__("tf_listener")

        # 创建缓冲区, 用于存储TF数据帧
        self.buffer_ = Buffer()
        # 创建监听器, 用于订阅TF数据
        self.listener_ = TransformListener(self.buffer_, self)
        # 创建定时器, 用于定时获取TF数据
        self.timer_ = self.create_timer(0.1, self.get_transform)

    def get_transform(self):
        try:
            # 获取TF数据帧
            result = self.buffer_.lookup_transform(
                "map",
                "base_footprint",
                Time(seconds=0),  # 获取最近的TF
                Duration(seconds=1),  # 超时时间
            )

            # 获取TF数据帧中的位姿数据
            transform = result.transform
            rotation_euler = euler_from_quaternion(
                [
                    transform.rotation.x,
                    transform.rotation.y,
                    transform.rotation.z,
                    transform.rotation.w,
                ]
            )
            self.get_logger().info(
                f"Transform: translation={transform.translation}, rotation_quaternion={transform.rotation}, rotation_euler={rotation_euler}"
            )
        except Exception as e:
            self.get_logger().warn(f"Transform not found, reason: {e}")


def main(args=None):
    rclpy.init(args=args)
    tf_listener = TFListener()
    try:
        rclpy.spin(tf_listener)
    except KeyboardInterrupt:
        pass
    finally:
        tf_listener.destroy_node()
        rclpy.shutdown()
