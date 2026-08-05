#include <rclcpp/rclcpp.hpp>

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::Node::SharedPtr node = rclcpp::Node::make_shared("cpp_node");
    RCLCPP_INFO(node->get_logger(), "Hello, ROS2 C++ Node!");
    rclcpp::spin(node); // 轮询
    rclcpp::shutdown();
    return 0;
}
