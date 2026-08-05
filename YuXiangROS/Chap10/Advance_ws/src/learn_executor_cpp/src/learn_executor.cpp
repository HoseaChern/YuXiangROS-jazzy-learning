#include <example_interfaces/srv/add_two_ints.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sstream>
#include <std_msgs/msg/string.hpp>

using namespace std::chrono_literals;

class LearnExecutorNode : public rclcpp::Node {
  private:
    rclcpp::CallbackGroup::SharedPtr my_callback_group_;

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Service<example_interfaces::srv::AddTwoInts>::SharedPtr service_;

  public:
    LearnExecutorNode() : Node("learn_executor") {
        // my_callback_group_ =
        //     this->create_callback_group(rclcpp::CallbackGroupType::Reentrant); // 可重入回调组
        my_callback_group_ =
            this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive); // 互斥回调组

        publisher_ = this->create_publisher<std_msgs::msg::String>("string_topic", 10);
        timer_ = this->create_wall_timer(1s, std::bind(&LearnExecutorNode::timer_callback_, this));
        service_ = this->create_service<example_interfaces::srv::AddTwoInts>(
            "add_two_ints",
            std::bind(
                &LearnExecutorNode::add_two_ints_callback_,
                this,
                std::placeholders::_1,
                std::placeholders::_2
            ),
            rclcpp::QoS(rclcpp::ServicesQoS()), // 写一个默认qos占位, 否则没有重载
            my_callback_group_
        );
    }

  private:
    void timer_callback_() {
        auto msg = std_msgs::msg::String();
        msg.data = "Topic published: " + thread_info_();
        RCLCPP_INFO(this->get_logger(), msg.data.c_str());
        publisher_->publish(msg);
    }

    void add_two_ints_callback_(
        const std::shared_ptr<example_interfaces::srv::AddTwoInts::Request> request,
        std::shared_ptr<example_interfaces::srv::AddTwoInts::Response> response
    ) {
        RCLCPP_INFO(this->get_logger(), "Service Handling: %s", thread_info_().c_str());
        std::this_thread::sleep_for(std::chrono::seconds(10));
        response->sum = request->a + request->b;
        RCLCPP_INFO(this->get_logger(), "Service Finished: %s", thread_info_().c_str());
    }

    std::string thread_info_() {
        std::ostringstream thread_str;
        thread_str << "Tread ID: " << std::this_thread::get_id();
        return thread_str.str();
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<LearnExecutorNode>();

    auto options = rclcpp::ExecutorOptions();
    // auto executor = rclcpp::executors::SingleThreadedExecutor(options); // 单线程执行器
    size_t N = 3;                                                         // 线程数
    auto executor = rclcpp::executors::MultiThreadedExecutor(options, N); // 多线程执行器
    executor.add_node(node);
    executor.spin();

    rclcpp::shutdown();
    return 0;
}