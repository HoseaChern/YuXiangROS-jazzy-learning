import rclpy
from message_filters import ApproximateTimeSynchronizer, Subscriber
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Imu


class TimeSyncTestNode(Node):
    def __init__(self):
        super().__init__("sync_node")
        # 1. 订阅 imu 话题并注册回调输出时间戳
        self.imu_sub = Subscriber(self, Imu, "imu")
        self.imu_sub.registerCallback(self.imu_callback)
        # 2. 订阅 odom 话题并注册回调函数输出时间戳
        self.odom_sub = Subscriber(self, Odometry, "odom")
        self.odom_sub.registerCallback(self.odom_callback)
        # 3. 创建对应策略的同步器同步两个话题，并注册回调函数输出数据
        self.synchronizer = ApproximateTimeSynchronizer(
            [self.imu_sub, self.odom_sub],
            10,
            slop=0.01,  # slop 表示时间窗口单位为 s
        )
        self.synchronizer.registerCallback(self.result_callback)

    def imu_callback(self, imu_msg):
        self.get_logger().info(
            f"imu({imu_msg.header.stamp.sec},{imu_msg.header.stamp.nanosec})"
        )

    def odom_callback(self, odom_msg):
        self.get_logger().info(
            f"odom({odom_msg.header.stamp.sec},{odom_msg.header.stamp.nanosec})"
        )

    def result_callback(self, imu_msg, odom_msg):
        self.get_logger().info(
            f"imu({imu_msg.header.stamp.sec},{imu_msg.header.stamp.nanosec}),"
            f"odom({odom_msg.header.stamp.sec},{odom_msg.header.stamp.nanosec})"
        )


def main(args=None):
    rclpy.init(args=args)
    node = TimeSyncTestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
