#ifndef LISTENER_HPP
#define LISTENER_HPP

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/int32.hpp>

namespace learn_compose {

class Listener : public rclcpp::Node {
  private:
    rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr subscription_;

  public:
    explicit Listener(const rclcpp::NodeOptions& options);

  private:
    void subscription_callback_(const std_msgs::msg::Int32::UniquePtr msg);
};

} // namespace learn_compose

#endif // LISTENER_HPP