#ifndef TALKER_HPP
#define TALKER_HPP

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/int32.hpp>

namespace learn_compose {

class Talker : public rclcpp::Node {
  private:
    int32_t count_;
    rclcpp::Publisher<std_msgs::msg::Int32>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    explicit Talker(const rclcpp::NodeOptions& options);

  private:
    void timer_callback_();
};

} // namespace learn_compose

#endif // TALKER_HPP