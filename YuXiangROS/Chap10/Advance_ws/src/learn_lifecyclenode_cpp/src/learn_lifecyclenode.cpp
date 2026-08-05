#include <rclcpp/rclcpp.hpp>
#include <rclcpp_lifecycle/lifecycle_node.hpp>

using CallbackReturn = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

class LearnLifeCycleNode : public rclcpp_lifecycle::LifecycleNode {
  private:
    double timer_period_;
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    LearnLifeCycleNode() : rclcpp_lifecycle::LifecycleNode("lifecyclenode") {
        timer_period_ = 1.0;
        timer_ = nullptr;
        RCLCPP_INFO(get_logger(), "%s: has been created", get_name());
    }

    CallbackReturn on_configure(const rclcpp_lifecycle::State& state) override {
        (void)state;
        timer_period_ = 1.0;
        RCLCPP_INFO(get_logger(), "on_configure(): Setup timer_period");
        return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
    }

    CallbackReturn on_activate(const rclcpp_lifecycle::State& state) override {
        (void)state;
        timer_ = create_wall_timer(
            std::chrono::seconds(static_cast<int>(timer_period_)),
            std::bind(&LearnLifeCycleNode::timer_callback_, this)
        );
        RCLCPP_INFO(get_logger(), "on_activate(): Create timer");
        return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
    }

    CallbackReturn on_deactivate(const rclcpp_lifecycle::State& state) override {
        (void)state;
        timer_.reset();
        RCLCPP_INFO(get_logger(), "on_deactivate(): Destroy timer");
        return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
    }

    CallbackReturn on_shutdown(const rclcpp_lifecycle::State& state) override {
        (void)state;
        timer_.reset();
        RCLCPP_INFO(get_logger(), "on_shutdown()");
        return rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn::SUCCESS;
    }

  private:
    void timer_callback_() { RCLCPP_INFO(get_logger(), "Timer is outputting..."); }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<LearnLifeCycleNode>();
    rclcpp::spin(node->get_node_base_interface());
    rclcpp::shutdown();
    return 0;
}