#include <geometry_msgs/msg/transform_stamped.hpp> //提供消息接口
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Quaternion.h>             // 提供四元数接口
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp> // 提供消息类型转换函数
#include <tf2_ros/static_transform_broadcaster.h>  // 提供静态坐标变换广播类

class StaticTFBroadcaster : public rclcpp::Node {
  private:
    // 静态坐标变换广播智能指针
    std::shared_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;

  public:
    StaticTFBroadcaster() : Node("static_tf_broadcaster") {
        // 创建静态坐标变换广播器
        static_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);
        this->publish_static_tf_();
    }

  private:
    void publish_static_tf_() {
        geometry_msgs::msg::TransformStamped transform;

        transform.header.stamp = this->get_clock()->now();
        transform.header.frame_id = "map";
        transform.child_frame_id = "target_point";

        transform.transform.translation.x = 5.0;
        transform.transform.translation.y = 3.0;
        transform.transform.translation.z = 0.0;

        tf2::Quaternion quat;
        quat.setRPY(0, 0, 60 * M_PI / 180); // 弧度制欧拉角转四元数
        transform.transform.rotation =
            tf2::toMsg(quat); // 直接转成消息接口类型 (也可以仿照Python写法)

        static_broadcaster_->sendTransform(transform);
    };
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<StaticTFBroadcaster>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}