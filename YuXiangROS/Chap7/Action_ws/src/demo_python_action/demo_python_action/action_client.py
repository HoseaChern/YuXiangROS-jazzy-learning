import random

import rclpy


# 用于判断目标执行状态
from action_msgs.msg import GoalStatus

# 导入自定义的动作接口类型
from chap7_interfaces.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node


class NavActionClient(Node):
    def __init__(self):
        super().__init__("nav_action_client")

        # 创建动作客户端: 动作名 /navigate_to_pose, 类型 NavigateToPose
        self.action_client_ = ActionClient(self, NavigateToPose, "/navigate_to_pose")

        # 当前目标句柄与状态标记
        self.goal_handle_ = None
        self.feedback_count_ = 0
        # 反馈达到该次数后取消目标, 演示动作的可取消性
        self.feedback_threshold_ = 5
        self.cancel_sent_ = False
        self.goal_done_ = True

        # 创建定时器: 每 10 秒发送一个新目标 (异步, 不阻塞主线程)
        self.send_goal_timer_ = self.create_timer(10.0, self.send_new_goal)

    def send_new_goal(self):
        """
        定时器回调函数, 发送新目标
        """

        # 上一目标未结束, 跳过本轮
        if not self.goal_done_:
            return
        # 等待动作服务端启动
        if not self.action_client_.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("Server not ready, waiting...")
            return

        # 随机生成目标点
        goal = NavigateToPose.Goal()
        goal.target_x = random.uniform(1.0, 10.0)
        goal.target_y = random.uniform(1.0, 10.0)

        # 重置状态
        self.goal_done_ = False
        self.cancel_sent_ = False
        self.feedback_count_ = 0

        self.get_logger().info(
            f"Sending goal: ({goal.target_x:.2f}, {goal.target_y:.2f}), "
            f"cancel after {self.feedback_threshold_} feedbacks"
        )

        # 注册反馈回调后异步发送目标
        self.send_goal_future_ = self.action_client_.send_goal_async(goal, feedback_callback=self.feedback_callback)
        self.send_goal_future_.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """
        目标响应回调函数
        Args:
            future: 异步结果
        """

        goal_handle = future.result()
        # 目标被拒绝时返回空句柄
        if not goal_handle.accepted:
            self.get_logger().info("Goal rejected by server")
            self.goal_done_ = True
            return

        # 记录目标句柄, 用于后续取消
        self.goal_handle_ = goal_handle
        self.get_logger().info("Goal accepted by server")
        # 注册结果回调
        self.result_future_ = goal_handle.get_result_async()
        self.result_future_.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        """
        反馈回调函数: 打印进度, 累计一定次数后取消目标
        Args:
            feedback_msg: 反馈消息, 类型 NavigateToPose.Feedback
        """

        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"Feedback: pos ({feedback.current_x:.2f}, {feedback.current_y:.2f}), "
            f"dist {feedback.distance:.2f}, progress {feedback.progress * 100:.2f}%"
        )

        # 累计反馈次数, 达到阈值后发送取消请求
        self.feedback_count_ += 1
        if self.feedback_count_ == self.feedback_threshold_ and not self.cancel_sent_:
            self.cancel_sent_ = True
            self.get_logger().info(f"{self.feedback_threshold_} feedbacks, sending cancel...")
            # 发送取消请求 (对应 C++ 版 action_client_->async_cancel_goal)
            self.goal_handle_.cancel_goal_async()

    def result_callback(self, future):
        """
        结果回调函数
        Args:
            future: 异步结果
        """

        # 标记当前目标结束
        self.goal_done_ = True

        # 根据状态码打印执行结果
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal succeeded")
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("Goal aborted")
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("Goal canceled")
        else:
            self.get_logger().info(f"Unknown goal status: {status}")

        # 打印自定义结果字段
        action_result = future.result().result
        self.get_logger().info(
            f"Result: result={action_result.result}, final_distance: {action_result.final_distance:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = NavActionClient()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
