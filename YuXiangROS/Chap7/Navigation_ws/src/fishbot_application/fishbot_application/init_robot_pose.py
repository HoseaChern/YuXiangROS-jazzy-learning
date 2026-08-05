import rclpy
from geometry_msgs.msg import PoseStamped

# BasicNavigator 节点类: 用于导航操作
from nav2_simple_commander.robot_navigator import BasicNavigator


def main(args=None):
    rclpy.init(args=args)
    navigator = BasicNavigator()

    # 实例化消息对象
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = "map"
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 0.0
    initial_pose.pose.position.y = 0.0
    initial_pose.pose.orientation.w = 1.0

    # 发送初始位姿消息
    navigator.setInitialPose(initial_pose)
    # 等待 nav2 激活
    navigator.waitUntilNav2Active()

    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()
