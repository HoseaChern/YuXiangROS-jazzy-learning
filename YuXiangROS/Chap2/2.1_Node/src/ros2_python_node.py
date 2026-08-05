import rclpy

from rclpy.node import Node


def main(args=None):
    rclpy.init(args=args)
    node = Node("python_node")
    node.get_logger().info("Hello, ROS2 Python Node!")
    try:
        # 轮询
        rclpy.spin(node)
    # 按下Ctrl+C时, 安静退出, 否则报错 (C++节点内部已封装)
    except KeyboardInterrupt:
        pass
    finally:
        # 销毁节点 (C++节点会自动析构)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
