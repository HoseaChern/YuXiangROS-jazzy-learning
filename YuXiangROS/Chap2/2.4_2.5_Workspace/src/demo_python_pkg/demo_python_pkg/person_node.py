"""
1. 一包多节点: 在一个包中可以包含多个节点, 在 setup.py 中的 entry_points 中添加多个节点即可.
2. 节点类化: 将节点封装为类, 便于管理
"""

import rclpy
from rclpy.node import Node


class PersonNode(Node):
    def __init__(self, node_name: str, name: str, age: int) -> None:
        super().__init__(node_name)

        self.name = name
        self.age = age

    def say_hello(self, hobby: str):
        self.get_logger().info(f"Hello, my name is {self.name}, and I am {self.age} years old. I like {hobby}.")


def main(args=None):
    rclpy.init(args=args)
    person_node = PersonNode("person_node", "Changli", 20)
    person_node.say_hello("reading")
    try:
        rclpy.spin(person_node)
    except KeyboardInterrupt:
        pass
    finally:
        person_node.destroy_node()
        rclpy.shutdown()
