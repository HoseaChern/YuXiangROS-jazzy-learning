#include <chap4_interfaces/srv/patrol.hpp>  // 导入自定义的服务接口类型
#include <chrono>                           // 时间库
#include <cstdlib>                          // 随机数库
#include <ctime>                            // 时间种子库
#include <rcl_interfaces/msg/parameter.hpp> // 用于构建参数服务消息
#include <rcl_interfaces/msg/parameter_type.hpp>
#include <rcl_interfaces/msg/parameter_value.hpp>
#include <rcl_interfaces/srv/set_parameters.hpp> // 导入参数服务的接口类型
#include <rclcpp/rclcpp.hpp>

using namespace std::chrono_literals; // 时间字面量
using Patrol = chap4_interfaces::srv::Patrol;
using SetParameters = rcl_interfaces::srv::SetParameters;

class PatrolClient : public rclcpp::Node {
  private:
    // 客户端智能指针: 类型 Patrol
    rclcpp::Client<Patrol>::SharedPtr patrol_client_;
    // 定时器智能指针
    rclcpp::TimerBase::SharedPtr timer_;

  public:
    PatrolClient() : Node("patrol_client") {
        // 创建客户端, 名称/patrol, 类型 Patrol
        patrol_client_ = this->create_client<Patrol>("/patrol");
        // 创建定时器: 10s周期
        timer_ = this->create_wall_timer(10s, std::bind(&PatrolClient::timer_callback_, this));
        // 设置随机数种子, 使用当前系统时间作为种子
        srand(time(NULL));
    }

    /**
     * @brief 参数更新服务
     * @param parameter 待更新的参数对象
     * @return 服务调用的结果
     */
    std::shared_ptr<SetParameters::Response>
    call_set_parameters(rcl_interfaces::msg::Parameter& parameter) {
        // 0. 创建参数更新客户端: 类型 SetParameters, 名称 /turtle_controller/set_parameters (注意: 服务名中应当为服务端节点名)
        auto param_client = this->create_client<SetParameters>("/turtle_controller/set_parameters");

        // 1. 等待服务端启动
        while (!param_client->wait_for_service(std::chrono::seconds(1))) {
            // 等待时检测rclcpp状态
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(
                    this->get_logger(),
                    "Client interrupted while waiting for service to appear."
                );
                return nullptr;
            }
            RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
        }

        // 2. 实例化请求消息
        auto request = std::make_shared<SetParameters::Request>();
        request->parameters.push_back(parameter);

        // 3. 发送异步请求
        auto future = param_client->async_send_request(request);
        // 这里是写法2
        rclcpp::spin_until_future_complete(this->get_node_base_interface(), future);
        auto response = future.get();
        return response;
    }

    /**
     * @brief 更新服务器参数k
     * @param k 新的k值
     */
    void update_server_param_k(double k) {
        // 1. 实例化参数消息
        auto param = rcl_interfaces::msg::Parameter();

        // 2. 设置参数名称和值
        // 参数名: k
        param.name = "k";
        // 参数值: k
        auto new_model_value = rcl_interfaces::msg::ParameterValue();
        new_model_value.type = rcl_interfaces::msg::ParameterType::PARAMETER_DOUBLE;
        new_model_value.double_value = k;
        param.value = new_model_value;

        auto response = call_set_parameters(param);
        if (response == nullptr) {
            RCLCPP_WARN(this->get_logger(), "Update k failed");
            return;
        }

        for (auto result : response->results) {
            if (result.successful) {
                RCLCPP_INFO(
                    this->get_logger(),
                    "Update %s to %lf successfully",
                    param.name.c_str(),
                    k
                );
            } else {
                RCLCPP_ERROR(
                    this->get_logger(),
                    "Update %s to %lf failed: %s",
                    param.name.c_str(),
                    k,
                    result.reason.c_str()
                );
            }
        }
    }

  private:
    /*
    定时器回调函数
    */
    void timer_callback_() {
        // 1. 等待服务端启动
        while (!patrol_client_->wait_for_service(std::chrono::seconds(1))) {
            // 等待时检测rclcpp状态
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(
                    this->get_logger(),
                    "Client interrupted while waiting for service to appear."
                );
                return;
            }
            RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
        }

        // 2. 实例化请求消息
        auto request = std::make_shared<Patrol::Request>();
        request->target_x = rand() % 15;
        request->target_y = rand() % 15;
        RCLCPP_INFO(
            this->get_logger(),
            "Sending request: target_x=%f, target_y=%f",
            request->target_x,
            request->target_y
        );

        // 3. 发送异步请求
        // 这里是写法1
        patrol_client_->async_send_request(
            request,
            std::bind(&PatrolClient::async_callback_, this, std::placeholders::_1)
        );
    }

    /**
     * @brief 异步回调函数
     * @param future 服务调用的结果Future对象
     * @note 注意参数类型是 SharedFuture 而不是 SharedPtr
     */
    void async_callback_(const rclcpp::Client<Patrol>::SharedFuture result_future) {
        // 4. 处理响应
        auto response = result_future.get();
        if (response->result == Patrol::Response::SUCCESS) {
            RCLCPP_INFO(this->get_logger(), "Patrol success");
        } else if (response->result == Patrol::Response::FAILURE) {
            RCLCPP_INFO(this->get_logger(), "Patrol failed");
        }
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PatrolClient>();
    node->update_server_param_k(1.5);
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}