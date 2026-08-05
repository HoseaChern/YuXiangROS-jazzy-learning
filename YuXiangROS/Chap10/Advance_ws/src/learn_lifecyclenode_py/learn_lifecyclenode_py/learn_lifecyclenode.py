import rclpy
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn


class LearnLifeCycleNode(LifecycleNode):
    """
    设置生命状态
    ros2 lifecycle set /lifecyclenode [state]

    state:
    configure, activate, deactivate, shutdown
    """

    def __init__(self):
        super().__init__("lifecyclenode")
        self.timer_period = 0
        self.timer_ = None
        self.get_logger().info(f"{self.get_name()}: has been created")

    def timer_callback(self):
        self.get_logger().info("Timer is outputting...")

    def on_configure(self, state):
        self.timer_period = 1.0  # 设置定时器周期
        self.get_logger().info("on_configure(): Setup timer_period")
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state):
        self.timer_ = self.create_timer(self.timer_period, self.timer_callback)
        self.get_logger().info("on_activate(): Create timer")
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state):
        if self.timer_ is None:
            self.get_logger().warn("on_deactivate(): Timer has been destroyed!")
            return TransitionCallbackReturn.SUCCESS
        self.destroy_timer(self.timer_)  # 销毁定时器
        self.get_logger().info("on_deactivate(): Destroy timer")
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state):
        # 定时器未销毁则销毁
        if self.timer_ is not None:
            self.destroy_timer(self.timer_)
        self.get_logger().info("on_shutdown()")
        return TransitionCallbackReturn.SUCCESS


def main():
    rclpy.init()
    node = LearnLifeCycleNode()
    rclpy.spin(node)
    rclpy.shutdown()
