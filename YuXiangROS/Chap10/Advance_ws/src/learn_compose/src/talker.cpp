#include "learn_compose/talker.hpp"

#include <chrono>

namespace learn_compose {

using namespace std::chrono_literals;

Talker::Talker(const rclcpp::NodeOptions& options) : Node("talker", options) {
    publisher_ = this->create_publisher<std_msgs::msg::Int32>("count", 10);
    timer_ = this->create_wall_timer(1s, std::bind(&Talker::timer_callback_, this));
}

void Talker::timer_callback_() {
    // 独占式智能指针, 进而采用零复制传输(直接传输地址, 而非数据, 仅限同一主机内), 减少开销
    auto msg = std::make_unique<std_msgs::msg::Int32>();
    msg->data = count_++;
    RCLCPP_INFO(
        this->get_logger(),
        "Publishing: %d (0x%lX)",
        msg->data,
        reinterpret_cast<std::uintptr_t>(msg.get())
    ); // std_msgs::msg::Int32* 与 std::uintptr_t 二者类型毫无关联, 只能reinterpret转换
    publisher_->publish(std::move(msg));
}

} // namespace learn_compose

// 使用组件(component)可以动态地将不同节点加载到统一进程, 也可以动态卸载
// 将 talker 节点注册到 rclcpp_components 组件管理器中
#include <rclcpp_components/register_node_macro.hpp>
RCLCPP_COMPONENTS_REGISTER_NODE(learn_compose::Talker)
