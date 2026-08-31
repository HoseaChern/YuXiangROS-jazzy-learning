import threading
import time

import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String


class LearnExecutorNode(Node):
    def __init__(self):
        super().__init__("learn_executor")

        # my_callback_group = ReentrantCallbackGroup()  # 可重入回调组
        my_callback_group = MutuallyExclusiveCallbackGroup()  # 互斥回调组

        self.publisher = self.create_publisher(String, "string_topic", 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.service = self.create_service(
            AddTwoInts,
            "add_two_ints",
            self.add_two_ints_callback,
            callback_group=my_callback_group,
        )

    def timer_callback(self):
        msg = String()
        msg.data = (
            f"Topic published: Thread ID: {threading.get_ident()}, Total Thread Numbers: {threading.active_count()}"
        )
        self.get_logger().info(msg.data)
        self.publisher.publish(msg)

    def add_two_ints_callback(self, request, response):
        self.get_logger().info(f"Service Handling, Tread ID:{threading.get_ident()}")
        time.sleep(10)
        response.sum = request.a + request.b
        self.get_logger().info(f"Service Finished, Tread ID:{threading.get_ident()}")
        return response


def main(args=None):
    rclpy.init(args=args)
    node = LearnExecutorNode()

    # executor = SingleThreadedExecutor()  # 单线程执行器
    N = 3  # 线程数
    executor = MultiThreadedExecutor(N)  # 多线程执行器
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
