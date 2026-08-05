#include <chap4_interfaces/srv/patrol.hpp>              // 导入自定义的服务接口类型
#include <geometry_msgs/msg/twist.hpp>                  // 话题 /turtle1/cmd_vel 接口类型
#include <rcl_interfaces/msg/set_parameters_result.hpp> // 用于构建参数处理结果
#include <rclcpp/rclcpp.hpp>
#include <turtlesim/msg/pose.hpp> // 话题 /turtle1/Pose 接口类型

using Patrol = chap4_interfaces::srv::Patrol;
using SetParametersResult = rcl_interfaces::msg::SetParametersResult;

class TurtleControler : public rclcpp::Node {
  private:
    // 速度发布者智能指针: 话题 /turtle1/cmd_vel, 队列大小 10, 类型 geometry_msgs::msg::Twist
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr velocity_publisher_;
    // 位置订阅者智能指针: 话题 /turtle1/pose, 队列大小 10, 类型 turtlesim::msg::Pose
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscription_;
    // 服务端智能指针: 类型 Patrol
    rclcpp::Service<Patrol>::SharedPtr patrol_server_;
    // 参数回调函数句柄智能指针
    OnSetParametersCallbackHandle::SharedPtr parameters_callback_handle_;

    double target_x_{1.0};  // 目标x坐标, 默认1.0
    double target_y_{1.0};  // 目标y坐标, 默认1.0
    double k_{1.0};         // 比例系数, 输出 = k * 误差
    double max_speed_{3.0}; // 最大线速度, 默认3.0

  public:
    TurtleControler() : Node("turtle_controller") {
        // 创建速度发布者, 话题 /turtle1/cmd_vel, 队列大小 10, 类型 geometry_msgs::msg::Twist
        velocity_publisher_ =
            this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
        // 创建位置订阅者, 话题 /turtle1/pose, 队列大小 10, 类型 turtlesim::msg::Pose
        pose_subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            std::bind(&TurtleControler::pose_callback_, this, std::placeholders::_1)
        );
        // 创建服务端, 名称/patrol, 类型 Patrol
        patrol_server_ = this->create_service<Patrol>(
            "/patrol",
            std::bind(
                &TurtleControler::patrol_callback_,
                this,
                std::placeholders::_1,
                std::placeholders::_2
            )
        );

        // 声明参数
        // 参数名: k, 默认值: 1.0
        this->declare_parameter("k", 1.0);
        // 参数名: max_speed, 默认值: 3.0
        this->declare_parameter("max_speed", 3.0);

        // 获取参数值
        this->get_parameter("k", k_);
        this->get_parameter("max_speed", max_speed_);

        // 添加参数回调函数
        parameters_callback_handle_ = this->add_on_set_parameters_callback(
            std::bind(&TurtleControler::parameters_callback_, this, std::placeholders::_1)
        );
    }

  private:
    /**
     * @brief 订阅回调函数
     * @param pose: pose 位置消息, 类型 turtlesim::msg::Pose
     * @note
	 * 1. bind 打包: pose_callback_ + 对象this + 占位符 \note
	 * 2. 得到一个匿名函数对象, 传给 rclcpp 库 \note
	 * 3. 轮询时, 底层DDS(数据分发服务)收到二进制订阅消息, 先还原为C++对象, 再填充占位符, 最后调用 \note
	 * 显然, 被打包的方法有几个参数就应该有几个占位符 \note
	 */
    void pose_callback_(const turtlesim::msg::Pose::SharedPtr pose) {
        // 实例化一则消息
        auto msg = geometry_msgs::msg::Twist();

        // 1.记录当前位置
        double current_x = pose->x;
        double current_y = pose->y;

        // 2. 计算到目标距离与角度差
        double distance =
            std::sqrt(std::pow(target_x_ - current_x, 2) + std::pow(target_y_ - current_y, 2));
        double angle = std::atan2(target_y_ - current_y, target_x_ - current_x) - pose->theta;

        // 3. 控制策略:
        // 距离大于0.1则继续移动; 角度差大于0.2则转向, 否则直行
        if (distance > 0.1) {
            if (fabs(angle) > 0.1) {
                msg.angular.z = fabs(angle);
            } else {
                msg.linear.x = k_ * distance;
            }
        }

        // 4. 限制最大线速度
        if (msg.linear.x > max_speed_) {
            msg.linear.x = max_speed_;
        }

        // 5. 在话题上发布速度消息
        velocity_publisher_->publish(msg);
    }

    /**
     * @brief 服务回调函数
     * @param request: 请求消息指针
     * @param response: 响应消息指针
     */
    void patrol_callback_(
        const std::shared_ptr<Patrol::Request> request,
        const std::shared_ptr<Patrol::Response> response
    ) {
        // 检查目标坐标是否在范围内
        if ((0 < request->target_x && request->target_x < 12.0f) &&
            (0 < request->target_y && request->target_y < 12.0f)) {
            // 如果在范围内, 则设置目标坐标, 并返回成功
            target_x_ = request->target_x;
            target_y_ = request->target_y;
            response->result = Patrol::Response::SUCCESS;
        } else {
            response->result = Patrol::Response::FAILURE;
        }
    }

    /**
     * @brief 参数回调函数
     * @attention 有返回值, 而非void
     * @param parameters 参数向量
     * @return 参数处理结果
     */
    SetParametersResult parameters_callback_(const std::vector<rclcpp::Parameter>& parameters) {
        // 遍历参数向量, 根据参数名更新参数值
        for (auto parameter : parameters) {
            RCLCPP_INFO(
                this->get_logger(),
                "Parameter: %s is changed to %lf",
                parameter.get_name().c_str(),
                parameter.as_double()
            );
            if (parameter.get_name() == "k") {
                k_ = parameter.as_double();
            }
            if (parameter.get_name() == "max_speed") {
                max_speed_ = parameter.as_double();
            }
        }

        // 实例化参数处理结果 (C++必须实例化, Python不必)
        auto result = SetParametersResult();
        result.successful = true;
        return result;
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleControler>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
