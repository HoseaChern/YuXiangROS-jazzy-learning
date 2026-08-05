"""
1. ros2 action list 查看当前动作列表
2. ros2 action info /navigate_to_pose -t 查看导航动作信息
3. ros2 interface show nav2_msgs/action/NavigateToPose 查看动作接口定义
4. ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 1.0}}}}" --feedback 发送导航动作请求
"""

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration


def main(args=None):
    rclpy.init(args=args)
    navigator = BasicNavigator()
    # 等待nav2激活
    navigator.waitUntilNav2Active()

    # 设置目标点坐标
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = "map"
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = 1.0
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0

    # 发送目标接收反馈结果
    navigator.goToPose(goal_pose)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback is None:
            navigator.get_logger().info("No feedback available")
            continue

        # navigator.get_logger().info(
        #     f"Remaining Time: {Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9} s"
        # )
        # 使用 distance_remaining 替代 estimated_time_remaining
        # 在 jazzy 中, estimated_time_remaining有已知问题, 始终返回默认值0.0
        navigator.get_logger().info(
            f"Remaining Distance: {feedback.distance_remaining:.2f} m"
        )

        # 超时自动取消
        if Duration.from_msg(feedback.navigation_time) > Duration(seconds=600.0):
            navigator.cancelTask()

    # 最终结果判断
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        navigator.get_logger().info("Navigation succeeded")
    elif result == TaskResult.CANCELED:
        navigator.get_logger().warn("Navigation canceled")
    elif result == TaskResult.FAILED:
        navigator.get_logger().error("Navigation failed")
    else:
        navigator.get_logger().error("Navigation unknown result")
