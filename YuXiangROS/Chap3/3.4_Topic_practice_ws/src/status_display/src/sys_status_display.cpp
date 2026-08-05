#include <QApplication> // 应用类
#include <QLabel>       // 显示文本
#include <QString>      // 存储字符串
#include <rclcpp/rclcpp.hpp>
#include <status_interfaces/msg/system_status.hpp> // 导入自定义的话题接口类型

using SystemStatus = status_interfaces::msg::SystemStatus;

class SysStatusDisplay : public rclcpp::Node {
  private:
    // 订阅者智能指针: 接口类型 SystemStatus
    rclcpp::Subscription<SystemStatus>::SharedPtr subscription_;
    QLabel* label_;

  public:
    SysStatusDisplay() : Node("sys_status_display") {
        // 创建一个订阅者: 话题 /sys_status, 队列大小为10, 接口类型 SystemStatus
        subscription_ = this->create_subscription<SystemStatus>(
            "/sys_status",
            10,
            std::bind(&SysStatusDisplay::subscription_callback_, this, std::placeholders::_1)
        );
        // 创建一个空的SystemStatus对象, 转化为QString进行展示
        label_ = new QLabel(get_qstr_from_msg_(std::make_shared<SystemStatus>()));
        label_->show();
    }

  private:
    /**
     * @brief 订阅回调函数
     * @param msg 系统状态消息, 类型 SystemStatus::SharedPtr
     */
    void subscription_callback_(const SystemStatus::SharedPtr msg) {
        label_->setText(get_qstr_from_msg_(msg));
    }

    QString get_qstr_from_msg_(const SystemStatus::SharedPtr msg) {
        std::stringstream show_str;
        show_str << "==========System Status==========\n"
                 << "Time Stamp:\t" << msg->stamp.sec << "\ts\n"
                 << "User Name:\t" << msg->host_name << "\t\n"
                 << "CPU Usage:\t" << msg->cpu_percent << "\t%\n"
                 << "Memory Usage:\t" << msg->memory_percent << "\t%\n"
                 << "Memory Total:\t" << msg->memory_total << "\tMB\n"
                 << "Memory Free:\t" << msg->memory_available << "\tMB\n"
                 << "Network Send:\t" << msg->net_sent << "\tMB\n"
                 << "Network Receive:\t" << msg->net_recv << "\tMB\n"
                 << "================================\n";

        return QString::fromStdString(show_str.str());
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    QApplication app(argc, argv);
    auto node = std::make_shared<SysStatusDisplay>();

    // rclcpp::spin与QApplication::exec()都是轮询, 都会阻塞程序, 所以需要采用多线程
    std::thread spin_thread([&]() -> void { rclcpp::spin(node); });
    spin_thread.detach();

    app.exec();
    rclcpp::shutdown();
    return 0;
}