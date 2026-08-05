#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/sync_policies/exact_time.h>
#include <message_filters/sync_policies/latest_time.h>
#include <message_filters/time_synchronizer.h>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>

using Imu = sensor_msgs::msg::Imu;
using Odometry = nav_msgs::msg::Odometry;
using namespace message_filters;

// 同步策略：严格时间对齐策略
// using MySyncPolicy = sync_policies::ExactTime<Imu, Odometry>;
// 同步策略：大约时间对齐策略
using MySyncPolicy = sync_policies::ApproximateTime<Imu, Odometry>;
// 同步策略：最新时间对齐策略
// using MySyncPolicy = sync_policies::LatestTime<Imu, Odometry>;

class TimeSyncTestNode : public rclcpp::Node {
  private:
    std::shared_ptr<Subscriber<Imu>> imu_sub_;
    std::shared_ptr<Subscriber<Odometry>> odom_sub_;
    std::shared_ptr<Synchronizer<MySyncPolicy>> synchronizer_;

  public:
    TimeSyncTestNode() : Node("sync_node") {
        // 1. 订阅 imu 话题并注册回调输出时间戳
        imu_sub_ = std::make_shared<Subscriber<Imu>>(this, "imu");
        imu_sub_->registerCallback<Imu::SharedPtr>(
            std::bind(&TimeSyncTestNode::imu_callback_, this, std::placeholders::_1)
        );
        // 2. 订阅 odom 话题并注册回调函数输出时间戳
        odom_sub_ = std::make_shared<Subscriber<Odometry>>(this, "odom");
        odom_sub_->registerCallback<Odometry::SharedPtr>(
            std::bind(&TimeSyncTestNode::odom_callback_, this, std::placeholders::_1)
        );
        // 3. 创建对应策略的同步器同步两个话题，并注册回调函数输出数据
        synchronizer_ =
            std::make_shared<Synchronizer<MySyncPolicy>>(MySyncPolicy(10), *imu_sub_, *odom_sub_);
        // 若为 LatestTime, 则 MySyncPolicy() 不得传入参数
        // synchronizer_ =
        //     std::make_shared<Synchronizer<MySyncPolicy>>(MySyncPolicy(), *imu_sub_, *odom_sub_);
        synchronizer_->registerCallback(std::bind(
            &TimeSyncTestNode::result_callback_,
            this,
            std::placeholders::_1,
            std::placeholders::_2
        ));
    }

  private:
    void imu_callback_(const Imu::SharedPtr& imu_msg) {
        RCLCPP_INFO(
            get_logger(),
            "imu(%u,%u)",
            imu_msg->header.stamp.sec,
            imu_msg->header.stamp.nanosec
        );
    }

    void odom_callback_(const Odometry::SharedPtr& odom_msg) {
        RCLCPP_INFO(
            get_logger(),
            "odom(%u,%u)",
            odom_msg->header.stamp.sec,
            odom_msg->header.stamp.nanosec
        );
    }

    void
    result_callback_(const Imu::ConstSharedPtr imu_msg, const Odometry::ConstSharedPtr odom_msg) {
        RCLCPP_INFO(
            get_logger(),
            "imu(%u,%u),odom(%u,%u))",
            imu_msg->header.stamp.sec,
            imu_msg->header.stamp.nanosec,
            odom_msg->header.stamp.sec,
            odom_msg->header.stamp.nanosec
        );
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TimeSyncTestNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}