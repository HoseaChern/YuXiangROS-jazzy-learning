#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2/utils.h>
#include <tf2_ros/transform_broadcaster.h>

class OdomTopic2TF : public rclcpp::Node {
  private:
    // 里程计订阅智能指针, 话题 /odom, 使用传感器QoS, 类型 nav_msgs::msg::Odometry
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_subscribe_;
    // 动态坐标变换广播指针
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

  public:
    OdomTopic2TF() : Node("odom2tf") {
        // 创建里程计订阅者, 话题 /odom, 使用传感器QoS, 类型 nav_msgs::msg::Odometry
        odom_subscribe_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/odom",
            rclcpp::SensorDataQoS(), // 因为发布节点使用了 best_effort
            std::bind(&OdomTopic2TF::odom_callback_, this, std::placeholders::_1)
        );
        // 创建动态坐标变换广播器
        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(this);
    }

  private:
    /**
     * @brief 里程计订阅回调函数
     * 
     * @param msg 订阅的里程计消息
     * 
     * @note 处理接收到的 odom 消息, 并广播 tf
     */
    void odom_callback_(const nav_msgs::msg::Odometry::SharedPtr msg) {
        geometry_msgs::msg::TransformStamped transform;

        // 使用消息的时间戳的框架ID
        transform.header = msg->header;
        transform.child_frame_id = msg->child_frame_id;

        transform.transform.translation.x = msg->pose.pose.position.x;
        transform.transform.translation.y = msg->pose.pose.position.y;
        transform.transform.translation.z = msg->pose.pose.position.z;
        transform.transform.rotation.x = msg->pose.pose.orientation.x;
        transform.transform.rotation.y = msg->pose.pose.orientation.y;
        transform.transform.rotation.z = msg->pose.pose.orientation.z;
        transform.transform.rotation.w = msg->pose.pose.orientation.w;

        // 广播坐标变换信息
        tf_broadcaster_->sendTransform(transform);
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<OdomTopic2TF>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}