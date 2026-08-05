"""
1. 继承自父类
2. 调用父类方法
"""

import rclpy

# 必须用相对导入(demo_python_pkg.person_node或.person_node), 否则从系统库查找, 会报错
from demo_python_pkg.person_node import PersonNode


class WriterNode(PersonNode):
    def __init__(self, book: str):
        super().__init__("writer_node", "Changli", 20)  # 调用父类构造函数

        self.book = book

    def write_book(self):
        self.get_logger().info(f"I am writing a book titled '{self.book}'.")


def main(args=None):
    rclpy.init(args=args)
    writer_node = WriterNode("The Great Gatsby")
    writer_node.say_hello("reading")
    writer_node.write_book()
    try:
        rclpy.spin(writer_node)
    except KeyboardInterrupt:
        pass
    finally:
        writer_node.destroy_node()
        rclpy.shutdown()
