#include <chrono>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals;

class OdomPublisherSubscriber : public rclcpp::Node {
  private:
    // 发布者智能指针
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_publisher_;
    // 订阅者智能指针
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_subscriber_;
    // 定时器智能指针
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    OdomPublisherSubscriber() : Node("odom_publisher_subscriber") {
        // 可以自定义 QoS 配置
        // rclcpp::QoS qos_profile(10);                                       // 队列深度
        // qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);   // 可靠性
        // qos_profile.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL); // 持久性
        // qos_profile.history(RMW_QOS_POLICY_HISTORY_KEEP_LAST);             // 历史记录
        // qos_profile.deadline(rclcpp::Duration(1, 0));                      // 截止时间

        // 创建发布者并设置 QoS 为 sensor
        odom_publisher_ =
            this->create_publisher<nav_msgs::msg::Odometry>("/odom", rclcpp::SensorDataQoS());

        // 创建订阅者, 默认 QoS 配置, 队列深度为5, 这时无法通信
        // odom_subscriber_ = this->create_subscription<nav_msgs::msg::Odometry>(
        //     "/odom",
        //     5,
        //     std::bind(&OdomPublisherSubscriber::odom_callback_, this, std::placeholders::_1)
        // );
        odom_subscriber_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/odom",
            rclcpp::SensorDataQoS(),
            std::bind(&OdomPublisherSubscriber::odom_callback_, this, std::placeholders::_1)
        );

        // 创建周期为1s的定时器
        timer_ =
            this->create_wall_timer(1s, std::bind(&OdomPublisherSubscriber::timer_callback_, this));
    }

  private:
    void odom_callback_(const nav_msgs::msg::Odometry::SharedPtr msg) {
        (void)msg;
        RCLCPP_INFO(this->get_logger(), "Received odometry.");
    }

    void timer_callback_() {
        // 实例化一个消息
        auto odom_msg = nav_msgs::msg::Odometry();
        // 发布消息
        odom_publisher_->publish(odom_msg);
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto odom_node = std::make_shared<OdomPublisherSubscriber>();
    rclcpp::spin(odom_node);
    rclcpp::shutdown();
    return 0;
}