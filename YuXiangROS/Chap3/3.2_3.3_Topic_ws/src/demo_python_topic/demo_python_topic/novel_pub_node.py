"""
1. ros2 topic list -v 查询活动话题列表
2. ros2 topic echo /novels 查询指定话题上发布的消息
"""

from queue import Queue

import rclpy
import requests  # http请求库

# 要用到的话题接口的类型 example_interfaces/msg/String
from example_interfaces.msg import String
from rclpy.node import Node


class NovelPubNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)

        # 存放小说的队列
        self.novels_queue_ = Queue()
        # 创建定时器, 每5秒发布一行
        self.timer_ = self.create_timer(5, self.timer_callback)
        # 创建发布者: 类型 String, 话题 /novels, 队列大小为10
        self.novels_publisher_ = self.create_publisher(String, "/novels", 10)

    def download_novel(self, url):
        response = requests.get(url)
        response.encoding = "utf-8"
        self.get_logger().info(f"Downloading Finished: {url}")

        # 按行分割, 放入队列
        for line in response.text.splitlines():
            self.novels_queue_.put(line)

    def timer_callback(self):
        """
        定时器回调函数
        """
        # 当队列中有数据时, 取出并发布一行
        if self.novels_queue_.qsize() > 0:
            msg = String()  # 实例化一则消息
            msg.data = self.novels_queue_.get()  # 对消息数据进行赋值(从队列取出一行)
            self.novels_publisher_.publish(msg)  # 在话题上发布消息
            self.get_logger().info(f"Publishing: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = NovelPubNode("novel_pub")
    node.download_novel("http://0.0.0.0:8000/novel1.txt")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
