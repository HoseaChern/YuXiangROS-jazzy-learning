import platform

import psutil
import rclpy
from rclpy.node import Node

# 导入自定义的话题接口类型
from status_interfaces.msg import SystemStatus


class SysStatusPub(Node):
    def __init__(self, node_name):
        super().__init__(node_name)

        # 创建发布者: 类型 SystemStatus, 话题 /sys_status, 队列大小为10
        self.status_publisher_ = self.create_publisher(SystemStatus, "/sys_status", 10)
        # 创建定时器, 每1秒发布一则消息
        self.timer = self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        """
        定时器回调函数
        """
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        net_io_counters = psutil.net_io_counters()

        msg = SystemStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.host_name = platform.node()
        msg.cpu_percent = cpu_percent
        msg.memory_percent = memory_info.percent
        msg.memory_total = memory_info.total / 1024 / 1024
        msg.memory_available = memory_info.available / 1024 / 1024
        msg.net_sent = net_io_counters.bytes_sent / 1024 / 1024
        msg.net_recv = net_io_counters.bytes_recv / 1024 / 1024

        self.get_logger().info(f"Publishing system status: {str(msg)}")
        # 用 ros2 topic echo /sys_status 查看是否真实发布
        self.status_publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SysStatusPub("sys_status_pub")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
