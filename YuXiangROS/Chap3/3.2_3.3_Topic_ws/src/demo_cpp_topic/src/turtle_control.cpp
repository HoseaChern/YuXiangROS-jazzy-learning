#include <geometry_msgs/msg/twist.hpp> // 话题 /turtle1/cmd_vel 接口类型
#include <rclcpp/rclcpp.hpp>
#include <turtlesim/msg/pose.hpp> // 话题 /turtle1/Pose 接口类型

class TurtleControler : public rclcpp::Node {
  private:
    // 速度发布者智能指针: 话题 /turtle1/cmd_vel, 队列大小 10, 类型 geometry_msgs::msg::Twist
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr velocity_publisher_;
    // 位置订阅者智能指针: 话题 /turtle1/pose, 队列大小 10, 类型 turtlesim::msg::Pose
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscription_;

    double target_x_{1.0};  // 目标x坐标, 默认1.0
    double target_y_{1.0};  // 目标y坐标, 默认1.0
    double k_{1.0};         // 比例系数, 输出 = k * 误差
    double max_speed_{3.0}; // 最大线速度, 默认3.0

  public:
    TurtleControler() : Node("turtle_controller") {
        // 创建速度发布者, 话题 /turtle1/cmd_vel, 队列大小 10, 类型 geometry_msgs::msg::Twist
        velocity_publisher_ =
            this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
        // 创建位置订阅者, 话题 /turtle1/pose, 队列大小 10, 类型 turtlesim::msg::Pose
        pose_subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            std::bind(&TurtleControler::pose_callback_, this, std::placeholders::_1)
        );
    }

  private:
    /**
     * @brief 订阅回调函数
     * @param pose: pose 位置消息, 类型 turtlesim::msg::Pose
     * @note
	 * 1. bind 打包: pose_callback_ + 对象this + 占位符 \note
	 * 2. 得到一个匿名函数对象, 传给 rclcpp 库  \note
	 * 3. 轮询时, 底层DDS(数据分发服务)收到二进制订阅消息, 先还原为C++对象, 再填充占位符, 最后调用 \note
	 * 显然, 被打包的方法有几个参数就应该有几个占位符 \note
	 */
    void pose_callback_(const turtlesim::msg::Pose::SharedPtr pose) {
        // 实例化一则消息
        auto msg = geometry_msgs::msg::Twist();

        // 1.记录当前位置
        double current_x = pose->x;
        double current_y = pose->y;

        // 2. 计算到目标距离与角度差
        double distance =
            std::sqrt(std::pow(target_x_ - current_x, 2) + std::pow(target_y_ - current_y, 2));
        double angle = std::atan2(target_y_ - current_y, target_x_ - current_x) - pose->theta;

        // 3. 控制策略:
        // 距离大于0.1则继续移动; 角度差大于0.2则转向, 否则直行
        if (distance > 0.1) {
            if (fabs(angle) > 0.1) {
                msg.angular.z = fabs(angle);
            } else {
                msg.linear.x = k_ * distance;
            }
        }

        // 4. 限制最大线速度
        if (msg.linear.x > max_speed_) {
            msg.linear.x = max_speed_;
        }

        // 5. 在话题上发布速度消息
        velocity_publisher_->publish(msg);
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleControler>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}