#include "learn_compose/listener.hpp"

#include <chrono>

namespace learn_compose {

using namespace std::chrono_literals;

Listener::Listener(const rclcpp::NodeOptions& options) : Node("listener", options) {
    subscription_ = this->create_subscription<std_msgs::msg::Int32>(
        "count",
        10,
        std::bind(&Listener::subscription_callback_, this, std::placeholders::_1)
    );
}

void Listener::subscription_callback_(const std_msgs::msg::Int32::UniquePtr msg) {
    RCLCPP_INFO(
        this->get_logger(),
        "Received: %d (0x%lX)",
        msg->data,
        reinterpret_cast<std::uintptr_t>(msg.get())
    );
}
} // namespace learn_compose

// 将 listener 节点注册到 rclcpp_components 组件管理器中
#include <rclcpp_components/register_node_macro.hpp>
RCLCPP_COMPONENTS_REGISTER_NODE(learn_compose::Listener)