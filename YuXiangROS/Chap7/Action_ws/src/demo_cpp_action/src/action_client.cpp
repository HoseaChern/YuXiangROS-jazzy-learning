#include <chap7_interfaces/action/navigate_to_pose.hpp> // 导入自定义的动作接口类型
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp> // 动作通信库

#include <memory>
#include <random>

using namespace std::chrono_literals;

using NavigateToPose = chap7_interfaces::action::NavigateToPose;
using GoalHandleNavigate = rclcpp_action::ClientGoalHandle<NavigateToPose>;

class NavActionClient : public rclcpp::Node {
  private:
    // 动作客户端智能指针: 动作名 /navigate_to_pose, 类型 NavigateToPose
    rclcpp_action::Client<NavigateToPose>::SharedPtr action_client_;
    // 定时器: 周期性发送目标, 演示动作的异步性
    rclcpp::TimerBase::SharedPtr send_goal_timer_;
    // 当前目标句柄
    GoalHandleNavigate::SharedPtr goal_handle_;
    // 随机数生成器, 用于生成目标点
    std::mt19937 generator_;
    // 目标点坐标分布: [1.0, 10.0]
    std::uniform_real_distribution<double> coordinate_distribution_{1.0, 10.0};
    // 反馈累计次数
    int feedback_count_{0};
    // 反馈达到该次数后取消目标, 演示动作的可取消性
    int feedback_threshold_{5};
    // 是否已发送取消请求
    bool cancel_sent_{false};
    // 当前目标是否已结束
    bool goal_done_{true};

  public:
    NavActionClient() : Node("nav_action_client"), generator_(std::random_device{}()) {
        // 创建动作客户端: 动作名 /navigate_to_pose, 类型 NavigateToPose
        action_client_ = rclcpp_action::create_client<NavigateToPose>(this, "/navigate_to_pose");
        // 创建定时器: 每 10 秒发送一个新目标 (异步, 不阻塞主线程)
        send_goal_timer_ =
            this->create_wall_timer(10s, std::bind(&NavActionClient::send_new_goal_, this));
    }

  private:
    /**
     * @brief 定时器回调函数: 发送新目标
     */
    void send_new_goal_() {
        // 上一目标未结束, 跳过本轮
        if (goal_done_ == false) {
            return;
        }
        // 等待动作服务端启动
        if (this->action_client_->wait_for_action_server(1s) == false) {
            RCLCPP_INFO(this->get_logger(), "Server not ready, waiting...");
            return;
        }

        // 随机生成目标点
        auto goal = NavigateToPose::Goal();
        goal.target_x = coordinate_distribution_(generator_);
        goal.target_y = coordinate_distribution_(generator_);

        // 重置状态
        goal_done_ = false;
        cancel_sent_ = false;
        feedback_count_ = 0;

        RCLCPP_INFO(
            this->get_logger(),
            "Sending goal: (%.2f, %.2f), cancel after %d feedbacks",
            goal.target_x,
            goal.target_y,
            feedback_threshold_
        );

        // 注册三个回调后异步发送目标
        auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
        send_goal_options.goal_response_callback =
            std::bind(&NavActionClient::goal_response_callback_, this, std::placeholders::_1);
        send_goal_options.feedback_callback = std::bind(
            &NavActionClient::feedback_callback_,
            this,
            std::placeholders::_1,
            std::placeholders::_2
        );
        send_goal_options.result_callback =
            std::bind(&NavActionClient::result_callback_, this, std::placeholders::_1);
        this->action_client_->async_send_goal(goal, send_goal_options);
    }

    /**
     * @brief 目标响应回调函数
     * @param goal_handle: 目标句柄, 为空表示被拒绝
     */
    void goal_response_callback_(const GoalHandleNavigate::SharedPtr& goal_handle) {
        if (goal_handle != nullptr) {
            goal_handle_ = goal_handle;
            RCLCPP_INFO(this->get_logger(), "Goal accepted by server");
        } else {
            RCLCPP_INFO(this->get_logger(), "Goal rejected by server");
            goal_done_ = true;
        }
    }

    /**
     * @brief 反馈回调函数: 打印进度, 累计一定次数后取消目标
     * @param goal_handle: 目标句柄
     * @param feedback: 反馈消息, 类型 NavigateToPose::Feedback
     */
    void feedback_callback_(
        const GoalHandleNavigate::SharedPtr /* goal_handle */,
        const std::shared_ptr<const NavigateToPose::Feedback> feedback
    ) {
        RCLCPP_INFO(
            this->get_logger(),
            "Feedback: pos (%.2f, %.2f), dist %.2f, progress %.2f%%",
            feedback->current_x,
            feedback->current_y,
            feedback->distance,
            feedback->progress * 100
        );

        // 累计反馈次数, 达到阈值后发送取消请求
        feedback_count_++;
        if (feedback_count_ == feedback_threshold_ && cancel_sent_ == false) {
            cancel_sent_ = true;
            RCLCPP_INFO(this->get_logger(), "%d feedbacks, sending cancel...", feedback_threshold_);
            this->action_client_->async_cancel_goal(goal_handle_);
        }
    }

    /**
     * @brief 结果回调函数
     * @param result: 结果消息, 类型 NavigateToPose::Result
     */
    void result_callback_(const GoalHandleNavigate::WrappedResult& result) {
        goal_done_ = true;
        // 根据状态码打印执行结果
        switch (result.code) {
        case rclcpp_action::ResultCode::SUCCEEDED:
            RCLCPP_INFO(this->get_logger(), "Goal succeeded");
            break;
        case rclcpp_action::ResultCode::ABORTED:
            RCLCPP_INFO(this->get_logger(), "Goal aborted");
            return;
        case rclcpp_action::ResultCode::CANCELED:
            RCLCPP_INFO(this->get_logger(), "Goal canceled");
            break;
        default:
            RCLCPP_INFO(this->get_logger(), "Unknown goal status");
            return;
        }
        // 打印自定义结果字段
        RCLCPP_INFO(
            this->get_logger(),
            "Result: result=%d, final_distance: %.2f",
            result.result->result,
            result.result->final_distance
        );
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<NavActionClient>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
