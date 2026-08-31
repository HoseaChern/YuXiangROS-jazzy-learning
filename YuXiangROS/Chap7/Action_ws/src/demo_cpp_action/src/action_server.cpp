#include <chap7_interfaces/action/navigate_to_pose.hpp> // 导入自定义的动作接口类型
#include <geometry_msgs/msg/twist.hpp>                  // 话题 /turtle1/cmd_vel 接口类型
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp> // 动作通信库
#include <turtlesim/msg/pose.hpp>          // 话题 /turtle1/pose 接口类型

#include <algorithm>
#include <cmath>
#include <memory>
#include <thread>

using namespace std::chrono_literals;

using NavigateToPose = chap7_interfaces::action::NavigateToPose;
using GoalHandleNavigate = rclcpp_action::ServerGoalHandle<NavigateToPose>;

class NavActionServer : public rclcpp::Node {
  private:
    // 动作服务端智能指针: 动作名 /navigate_to_pose, 类型 NavigateToPose
    rclcpp_action::Server<NavigateToPose>::SharedPtr action_server_;
    // 速度发布者智能指针: 话题 /turtle1/cmd_vel, 队列大小 10, 类型 geometry_msgs::msg::Twist
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr velocity_publisher_;
    // 位置订阅者智能指针: 话题 /turtle1/pose, 队列大小 10, 类型 turtlesim::msg::Pose
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscription_;

    double target_x_{1.0};              // 目标x坐标, 默认1.0
    double target_y_{1.0};              // 目标y坐标, 默认1.0
    double linear_gain_{1.0};           // 线速度比例系数, 默认1.0
    double angular_gain_{4.0};          // 角速度比例系数, 默认4.0
    double max_speed_{3.0};             // 最大线速度, 默认3.0
    double goal_tolerance_{0.1};        // 到达判定阈值, 默认0.1
    double initial_distance_{1.0};      // 起点到目标点的距离, 用于计算进度
    turtlesim::msg::Pose current_pose_; // 当前位姿

  public:
    NavActionServer() : Node("nav_action_server") {
        // 创建速度发布者, 话题 /turtle1/cmd_vel, 队列大小 10, 类型 geometry_msgs::msg::Twist
        velocity_publisher_ =
            this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
        // 创建位置订阅者, 话题 /turtle1/pose, 队列大小 10, 类型 turtlesim::msg::Pose
        pose_subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            std::bind(&NavActionServer::pose_callback_, this, std::placeholders::_1)
        );
        // 创建动作服务端: 动作名 /navigate_to_pose, 类型 NavigateToPose
        // 三个回调分别用于: 校验目标 / 处理取消 / 执行目标
        action_server_ = rclcpp_action::create_server<NavigateToPose>(
            this,
            "/navigate_to_pose",
            std::bind(
                &NavActionServer::handle_goal_,
                this,
                std::placeholders::_1,
                std::placeholders::_2
            ),
            std::bind(&NavActionServer::handle_cancel_, this, std::placeholders::_1),
            std::bind(&NavActionServer::handle_accepted_, this, std::placeholders::_1)
        );

        // 声明参数
        // 参数名: linear_gain, 默认值: 1.0
        this->declare_parameter("linear_gain", 1.0);
        // 参数名: angular_gain, 默认值: 4.0
        this->declare_parameter("angular_gain", 4.0);
        // 参数名: max_speed, 默认值: 3.0
        this->declare_parameter("max_speed", 3.0);
        // 参数名: goal_tolerance, 默认值: 0.1
        this->declare_parameter("goal_tolerance", 0.1);

        // 获取参数值
        this->get_parameter("linear_gain", linear_gain_);
        this->get_parameter("angular_gain", angular_gain_);
        this->get_parameter("max_speed", max_speed_);
        this->get_parameter("goal_tolerance", goal_tolerance_);
    }

  private:
    /**
     * @brief 订阅回调函数: 记录当前位姿
     * @param pose: pose 位置消息, 类型 turtlesim::msg::Pose
     */
    void pose_callback_(const turtlesim::msg::Pose::SharedPtr pose) { current_pose_ = *pose; }

    /**
     * @brief 目标校验回调函数
     * @param uuid: 目标唯一标识
     * @param goal: 目标消息, 类型 NavigateToPose::Goal
     * @return 接受并执行 / 拒绝
     */
    rclcpp_action::GoalResponse handle_goal_(
        const rclcpp_action::GoalUUID& /* uuid */, std::shared_ptr<const NavigateToPose::Goal> goal
    ) {
        RCLCPP_INFO(
            this->get_logger(),
            "Received goal: (%.2f, %.2f)",
            goal->target_x,
            goal->target_y
        );
        // 校验目标坐标是否在仿真器范围内
        if ((0 < goal->target_x && goal->target_x < 12.0f) &&
            (0 < goal->target_y && goal->target_y < 12.0f)) {
            return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        } else {
            RCLCPP_WARN(this->get_logger(), "Goal out of bounds, rejected");
            return rclcpp_action::GoalResponse::REJECT;
        }
    }

    /**
     * @brief 取消回调函数
     * @param goal_handle: 目标句柄
     * @return 接受取消
     */
    rclcpp_action::CancelResponse handle_cancel_(
        const std::shared_ptr<GoalHandleNavigate> /* goal_handle */
    ) {
        RCLCPP_INFO(this->get_logger(), "Cancel requested, canceling...");
        return rclcpp_action::CancelResponse::ACCEPT;
    }

    /**
     * @brief 目标接受回调函数: 另起线程执行目标 (异步)
     * @param goal_handle: 目标句柄
     */
    void handle_accepted_(const std::shared_ptr<GoalHandleNavigate> goal_handle) {
        // 采用 detach 线程, 避免阻塞 executor 的回调循环
        std::thread{std::bind(&NavActionServer::execute_, this, goal_handle)}.detach();
    }

    /**
     * @brief 执行目标: 控制海龟移动到目标点, 周期性发布反馈
     * @param goal_handle: 目标句柄
     */
    void execute_(const std::shared_ptr<GoalHandleNavigate> goal_handle) {
        // 1. 读取目标坐标
        const auto goal = goal_handle->get_goal();
        target_x_ = goal->target_x;
        target_y_ = goal->target_y;
        RCLCPP_INFO(this->get_logger(), "Executing goal: (%.2f, %.2f)", target_x_, target_y_);

        // 2. 计算初始距离, 用于进度百分比
        initial_distance_ = std::sqrt(
            std::pow(target_x_ - current_pose_.x, 2) + std::pow(target_y_ - current_pose_.y, 2)
        );

        // 3. 循环控制, 每 10Hz 刷新一次
        rclcpp::Rate loop_rate(10);
        while (rclcpp::ok()) {
            // 3.1 计算当前距离与角度差
            double distance = std::sqrt(
                std::pow(target_x_ - current_pose_.x, 2) + std::pow(target_y_ - current_pose_.y, 2)
            );
            double angle = std::atan2(target_y_ - current_pose_.y, target_x_ - current_pose_.x) -
                           current_pose_.theta;
            // 角度差归一化到 [-pi, pi]
            while (angle > M_PI) {
                angle -= 2 * M_PI;
            }
            while (angle < -M_PI) {
                angle += 2 * M_PI;
            }

            // 3.2 处理取消: 停止运动并返回 CANCELED 结果
            if (goal_handle->is_canceling()) {
                stop_turtle_();
                auto result = std::make_shared<NavigateToPose::Result>();
                result->result = NavigateToPose::Result::CANCELED;
                result->final_distance = distance;
                RCLCPP_INFO(
                    this->get_logger(),
                    "Goal canceled, remaining distance: %.2f",
                    distance
                );
                goal_handle->canceled(result);
                return;
            }

            // 3.3 到达目标: 停止运动并返回 SUCCESS 结果
            if (distance < goal_tolerance_) {
                stop_turtle_();
                auto result = std::make_shared<NavigateToPose::Result>();
                result->result = NavigateToPose::Result::SUCCESS;
                result->final_distance = distance;
                RCLCPP_INFO(this->get_logger(), "Goal reached, remaining distance: %.2f", distance);
                goal_handle->succeed(result);
                return;
            }

            // 3.4 发布反馈: 当前位置 / 距离 / 进度
            auto feedback = std::make_shared<NavigateToPose::Feedback>();
            feedback->current_x = current_pose_.x;
            feedback->current_y = current_pose_.y;
            feedback->distance = distance;
            feedback->progress = std::clamp(1.0 - distance / initial_distance_, 0.0, 1.0);
            goal_handle->publish_feedback(feedback);

            // 3.5 发布速度: 角度差较大时先转向, 否则直行
            auto msg = geometry_msgs::msg::Twist();
            if (std::fabs(angle) > 0.1) {
                msg.angular.z = std::clamp(angular_gain_ * angle, -max_speed_, max_speed_);
            } else {
                msg.linear.x = std::clamp(linear_gain_ * distance, 0.0, max_speed_);
            }
            velocity_publisher_->publish(msg);

            loop_rate.sleep();
        }
    }

    /**
     * @brief 停止海龟运动
     */
    void stop_turtle_() {
        auto msg = geometry_msgs::msg::Twist();
        msg.linear.x = 0.0;
        msg.angular.z = 0.0;
        velocity_publisher_->publish(msg);
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<NavActionServer>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
