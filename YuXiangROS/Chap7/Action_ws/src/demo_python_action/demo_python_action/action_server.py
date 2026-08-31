"""
动作通信 - 常用命令(自定义动作接口 chap7_interfaces/action/NavigateToPose)

1. 查看所有动作
ros2 action list
2. 查看动作详情(动作名 /navigate_to_pose, 类型 NavigateToPose)
ros2 action info /navigate_to_pose -t
3. 查看动作接口定义
ros2 interface show chap7_interfaces/action/NavigateToPose
4. 命令行发送目标(等收到反馈)
ros2 action send_goal /navigate_to_pose chap7_interfaces/action/NavigateToPose "{target_x: 2.0, target_y: 2.0}" --feedback
"""

import math
import threading

import rclpy


# 导入自定义的动作接口类型
from chap7_interfaces.action import NavigateToPose

# 话题 /turtle1/cmd_vel 接口类型
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node

# 话题 /turtle1/pose 接口类型
from turtlesim.msg import Pose


class NavActionServer(Node):
    def __init__(self):
        super().__init__("nav_action_server")

        # 声明参数
        self.declare_parameter("linear_gain", 1.0)
        self.declare_parameter("angular_gain", 4.0)
        self.declare_parameter("max_speed", 3.0)
        self.declare_parameter("goal_tolerance", 0.1)
        # 获取参数值
        self.linear_gain_ = self.get_parameter("linear_gain").value
        self.angular_gain_ = self.get_parameter("angular_gain").value
        self.max_speed_ = self.get_parameter("max_speed").value
        self.goal_tolerance_ = self.get_parameter("goal_tolerance").value

        # 当前位姿, 默认取仿真器初始位置
        self.current_x_ = 5.54
        self.current_y_ = 5.54
        self.current_theta_ = 0.0
        # 目标点与初始距离
        self.target_x_ = 0.0
        self.target_y_ = 0.0
        self.initial_distance_ = 1.0

        # 创建速度发布者: 话题 /turtle1/cmd_vel, 队列大小 10, 类型 Twist
        self.velocity_publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        # 创建位置订阅者: 话题 /turtle1/pose, 队列大小 10, 类型 Pose
        self.pose_subscription_ = self.create_subscription(Pose, "/turtle1/pose", self.pose_callback, 10)
        # 创建动作服务端: 动作名 /navigate_to_pose, 类型 NavigateToPose
        # 三个回调分别用于: 校验目标 / 处理取消 / 执行目标
        self.action_server_ = ActionServer(
            self,
            NavigateToPose,
            "/navigate_to_pose",
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            handle_accepted_callback=self.handle_accepted_callback,
        )

    def pose_callback(self, pose):
        """
        订阅回调函数, 记录当前位姿
        Args:
            pose: pose 位置消息, 类型 turtlesim.msg.Pose
        """

        # 记录当前位置
        self.current_x_ = pose.x
        self.current_y_ = pose.y
        self.current_theta_ = pose.theta

    def goal_callback(self, goal_request):
        """
        目标校验回调函数
        Args:
            goal_request: 目标消息, 类型 NavigateToPose.Goal
        Returns:
            GoalResponse.ACCEPT: 接受目标
            GoalResponse.REJECT: 拒绝目标
        """

        self.get_logger().info(f"Received goal: ({goal_request.target_x}, {goal_request.target_y})")
        # 校验目标坐标是否在仿真器范围内
        if 0 < goal_request.target_x < 12.0 and 0 < goal_request.target_y < 12.0:
            return GoalResponse.ACCEPT
        else:
            self.get_logger().warn("Goal out of bounds, rejected")
            return GoalResponse.REJECT

    def cancel_callback(self, goal_handle):
        """
        取消回调函数
        Args:
            goal_handle: 目标句柄
        Returns:
            CancelResponse.ACCEPT: 接受取消
        """

        self.get_logger().info("Cancel requested, canceling...")
        return CancelResponse.ACCEPT

    def handle_accepted_callback(self, goal_handle):
        """
        目标接受回调: 另起线程执行目标 (异步)
        Args:
            goal_handle: 目标句柄
        """

        # 采用独立线程执行, 避免阻塞 executor 的事件循环
        # (与 C++ 版 handle_accepted_ 中 detach 线程的语义一致)
        threading.Thread(
            target=self.execute_callback,
            args=(goal_handle,),
            daemon=True,
        ).start()

    def execute_callback(self, goal_handle):
        """
        执行目标: 控制海龟移动到目标点, 周期性发布反馈
        Args:
            goal_handle: 目标句柄
        Returns:
            结果消息, 类型 NavigateToPose.Result
        """

        # 0. 将目标状态更新为执行中 (EXECUTING)
        # (rclpy 不会像 rclcpp 那样在接受目标时自动进入 EXECUTING, 需手动更新,
        #  否则取消请求到达时 C 层无法匹配该目标, 取消会被静默丢弃)
        if not goal_handle.is_cancel_requested:
            goal_handle.executing()

        # 1. 读取目标坐标
        self.target_x_ = goal_handle.request.target_x
        self.target_y_ = goal_handle.request.target_y
        self.get_logger().info(f"Executing goal: ({self.target_x_}, {self.target_y_})")

        # 2. 计算初始距离, 用于进度百分比
        self.initial_distance_ = math.sqrt(
            (self.target_x_ - self.current_x_) ** 2 + (self.target_y_ - self.current_y_) ** 2
        )

        # 3. 循环控制, 每 10Hz 刷新一次
        rate = self.create_rate(10)
        while rclpy.ok():
            # 3.1 计算当前距离与角度差
            distance = math.sqrt((self.target_x_ - self.current_x_) ** 2 + (self.target_y_ - self.current_y_) ** 2)
            angle = math.atan2(self.target_y_ - self.current_y_, self.target_x_ - self.current_x_) - self.current_theta_
            # 角度差归一化到 [-pi, pi]
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi

            # 3.2 处理取消: 停止运动并返回 CANCELED 结果
            if goal_handle.is_cancel_requested:
                self.stop_turtle()
                result = NavigateToPose.Result()
                result.result = NavigateToPose.Result.CANCELED
                result.final_distance = distance
                self.get_logger().info(f"Goal canceled, remaining distance: {distance:.2f}")
                goal_handle.canceled(result)
                return result

            # 3.3 到达目标: 停止运动并返回 SUCCESS 结果
            if distance < self.goal_tolerance_:
                self.stop_turtle()
                result = NavigateToPose.Result()
                result.result = NavigateToPose.Result.SUCCESS
                result.final_distance = distance
                self.get_logger().info(f"Goal reached, remaining distance: {distance:.2f}")
                goal_handle.succeed(result)
                return result

            # 3.4 发布反馈: 当前位置 / 距离 / 进度
            feedback = NavigateToPose.Feedback()
            feedback.current_x = self.current_x_
            feedback.current_y = self.current_y_
            feedback.distance = distance
            feedback.progress = max(0.0, min(1.0, 1.0 - distance / self.initial_distance_))
            goal_handle.publish_feedback(feedback)

            # 3.5 发布速度: 角度差较大时先转向, 否则直行
            msg = Twist()
            if abs(angle) > 0.1:
                msg.angular.z = max(-self.max_speed_, min(self.max_speed_, self.angular_gain_ * angle))
            else:
                msg.linear.x = max(0.0, min(self.max_speed_, self.linear_gain_ * distance))
            self.velocity_publisher_.publish(msg)

            rate.sleep()

    def stop_turtle(self):
        """
        停止海龟运动
        """

        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.velocity_publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = NavActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
