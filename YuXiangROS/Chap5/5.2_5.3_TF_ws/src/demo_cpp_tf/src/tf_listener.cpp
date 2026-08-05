#include <chrono>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/utils.h> // 提供 tf2::getEulerYPR 函数
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <tf2_ros/buffer.h>             // 提供坐标缓冲器类
#include <tf2_ros/transform_listener.h> // 提供坐标监听器类

using namespace std::chrono_literals;

class TFListener : public rclcpp::Node {
  private:
    // 缓冲区智能指针
    std::shared_ptr<tf2_ros::Buffer> buffer_;
    // 监听器智能指针
    std::shared_ptr<tf2_ros::TransformListener> listener_;
    // 定时器智能指针
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    TFListener() : Node("tf_listener") {
        // 创建缓冲区
        buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
        // 创建监听器
        listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_, this);
        // 创建定时器, 每5秒执行一次
        timer_ = this->create_wall_timer(5s, std::bind(&TFListener::get_transform_, this));
    }

  private:
    void get_transform_() {
        try {
            // 获取TF数据帧
            const auto result = buffer_->lookupTransform(
                "base_link",
                "target_point",
                this->get_clock()->now(),            // 获取最近的TF
                rclcpp::Duration::from_seconds(1.0f) // 超时时间
            );

            // 获取TF数据帧中的位姿数据
            const auto& transform = result.transform;
            const auto& translation = transform.translation;
            const auto& rotation = transform.rotation;

            double yaw;
            double pitch;
            double roll;
            // 四元数转换为欧拉角
            tf2::getEulerYPR(rotation, yaw, pitch, roll);

            RCLCPP_INFO(
                get_logger(),
                "Translation: (%f, %f, %f)",
                translation.x,
                translation.y,
                translation.z
            );
            RCLCPP_INFO(get_logger(), "Rotation: (%f, %f, %f)", yaw, pitch, roll);
        } catch (tf2::TransformException& ex) {
            // 异常处理
            RCLCPP_WARN(get_logger(), "Transform error: %s", ex.what());
        }
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TFListener>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}