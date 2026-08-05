import rclpy
from nav_msgs.msg import Odometry
from rclpy import qos
from rclpy.node import Node

# 用于自定义 QoS 配置
# from rclpy.duration import Duration


class OdomPublisherSubscriber(Node):
    def __init__(self):
        super().__init__("odom_publisher_subscriber")

        # 可以自定义 QoS 配置
        # qos_profile = qos.QoSProfile(
        #     depth=10,  # 队列深度
        #     reliability=qos.ReliabilityPolicy.BEST_EFFORT,  # 可靠性
        #     durability=qos.DurabilityPolicy.TRANSIENT_LOCAL,  # 持久性
        #     history=qos.HistoryPolicy.KEEP_LAST,  # 历史记录
        #     deadline=Duration(seconds=1.0, nanoseconds=0),  # 截止时间
        # )

        # 创建发布者并设置 QoS 为 sensor
        self.odom_publisher = self.create_publisher(
            Odometry,
            "/odom",
            qos_profile=qos.qos_profile_sensor_data,
        )

        # 创建订阅者, 默认 QoS 配置, 队列深度为5, 这时无法通信
        # self.odom_subscriber = self.create_subscription(
        #     Odometry,
        #     "/odom",
        #     self.odom_callback,
        #     5,
        # )
        self.odom_subscriber = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            qos_profile=qos.qos_profile_sensor_data,
        )

        # 创建周期为1s的定时器
        self.timer = self.create_timer(1.0, self.timer_callback)

    def odom_callback(self, msg):
        self.get_logger().info("Received odometry.")

    def timer_callback(self):
        # 实例化一个消息
        odom_msg = Odometry()
        # 发布消息
        self.odom_publisher.publish(odom_msg)


def main(args=None):
    rclpy.init(args=args)
    odom_node = OdomPublisherSubscriber()

    try:
        rclpy.spin(odom_node)
    except KeyboardInterrupt:
        pass
    finally:
        odom_node.destroy_node()
        rclpy.shutdown()
