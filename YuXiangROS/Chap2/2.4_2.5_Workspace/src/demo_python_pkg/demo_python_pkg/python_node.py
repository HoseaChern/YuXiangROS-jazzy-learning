import rclpy

from rclpy.node import Node


def main(args=None):
    rclpy.init(args=args)
    node = Node("python_node")
    node.get_logger().info("Hello, ROS2 Python Node!")
    rclpy.spin(node)
    rclpy.shutdown()
