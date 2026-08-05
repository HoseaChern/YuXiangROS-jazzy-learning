#include <chrono>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <tf2_ros/transform_broadcaster.h>

using namespace std::chrono_literals;

class DynamicTFBroadcaster : public rclcpp::Node {
  private:
    // 动态坐标变换广播智能指针
    std::shared_ptr<tf2_ros::TransformBroadcaster> dynamic_broadcaster_;
    // 定时器智能指针
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    DynamicTFBroadcaster() : Node("dynamic_tf_broadcaster") {
        // 创建动态坐标变换广播器
        dynamic_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
        // 创建定时器, 10ms 周期(100Hz)
        timer_ = this->create_wall_timer(
            10ms,
            std::bind(&DynamicTFBroadcaster::publish_dynamic_tf_, this)
        );
    }

  private:
    void publish_dynamic_tf_() {
        geometry_msgs::msg::TransformStamped transform;

        transform.header.stamp = this->get_clock()->now();
        transform.header.frame_id = "map";
        transform.child_frame_id = "base_link";

        transform.transform.translation.x = 2.0;
        transform.transform.translation.y = 3.0;
        transform.transform.translation.z = 0.0;

        tf2::Quaternion quat;
        quat.setRPY(0.0, 0.0, 30 * M_PI / 180);
        transform.transform.rotation = tf2::toMsg(quat);

        dynamic_broadcaster_->sendTransform(transform);
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DynamicTFBroadcaster>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}