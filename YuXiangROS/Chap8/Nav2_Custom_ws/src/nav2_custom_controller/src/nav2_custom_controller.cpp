#include "nav2_custom_controller/nav2_custom_controller.hpp"

#include <algorithm>
#include <chrono>
#include <iostream>
#include <memory>
#include <nav2_core/planner_exceptions.hpp>
#include <nav2_util/geometry_utils.hpp>
#include <nav2_util/node_utils.hpp>
#include <string>
#include <thread>

namespace nav2_custom_controller {

void CustomController::configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr& parent, std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf, std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros
) {
    tf_ = tf;
    plugin_name_ = name;
    costmap_ = costmap_ros->getCostmap();

    // 声明并获取参数
    // 插件类并没有继承 rclcpp::Node, 而是将节点指针作为参数通过 configure 传入并存储到成员变量中
    node_ = parent.lock();
    nav2_util::declare_parameter_if_not_declared(
        node_,
        plugin_name_ + ".max_linear_velocity",
        rclcpp::ParameterValue(0.1)
    );
    nav2_util::declare_parameter_if_not_declared(
        node_,
        plugin_name_ + ".max_angular_velocity",
        rclcpp::ParameterValue(1.0)
    );
    node_->get_parameter(plugin_name_ + ".max_linear_velocity", max_linear_velocity_);
    node_->get_parameter(plugin_name_ + ".max_angular_velocity", max_angular_velocity_);
}

void CustomController::cleanup() {
    RCLCPP_INFO(
        node_->get_logger(),
        "Cleaning up plugin, type: CustomController, name: %s",
        plugin_name_.c_str()
    );
}

void CustomController::activate() {
    RCLCPP_INFO(
        node_->get_logger(),
        "Activating plugin, type: CustomController, name: %s",
        plugin_name_.c_str()
    );
}

void CustomController::deactivate() {
    RCLCPP_INFO(
        node_->get_logger(),
        "Deactivating plugin, type: CustomController, name: %s",
        plugin_name_.c_str()
    );
}

/**
 * @brief 计算速度指令
 * @param pose 当前位姿
 * @param velocity 当前速度
 * @param goal_checker 目标检查器, 用于检查是否到达了目标
 * @return 速度指令
 */
geometry_msgs::msg::TwistStamped CustomController::computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped& pose, const geometry_msgs::msg::Twist& /*velocity*/,
    nav2_core::GoalChecker* /*goal_checker*/
) {
    // 1. 检查路径是否为空
    if (global_plan_.poses.empty()) {
        throw nav2_core::PlannerException("Global plan is empty");
    }

    // 2. 将机器人当前姿态转换到全局计划坐标系中
    geometry_msgs::msg::PoseStamped pose_in_global_frame;
    if (!nav2_util::transformPoseInTargetFrame(
            pose,
            pose_in_global_frame,
            *tf_,
            global_plan_.header.frame_id,
            0.1
        )) {
        throw nav2_core::PlannerException("Fail to transform robot pose to global frame");
    }

    // 3. 获取最近的目标点和角度差
    geometry_msgs::msg::PoseStamped target_pose = getNearestTargetPose(pose_in_global_frame);
    double yaw_difference = calculateAngleDifference(pose_in_global_frame, target_pose);

    // 4. 根据角度差计算线速度和角速度
    geometry_msgs::msg::TwistStamped cmd_vel;
    cmd_vel.header.frame_id = pose_in_global_frame.header.frame_id;
    cmd_vel.header.stamp = node_->get_clock()->now();
    // 角度差 > pi/10 rad 则原地旋转, 否则直行
    if (fabs(yaw_difference) > M_PI / 10.0) {
        cmd_vel.twist.linear.x = 0.0;
        cmd_vel.twist.angular.z = fabs(yaw_difference) / yaw_difference * max_angular_velocity_;
    } else {
        cmd_vel.twist.linear.x = max_linear_velocity_;
        cmd_vel.twist.angular.z = 0.0;
    }
    RCLCPP_INFO(
        node_->get_logger(),
        "Controller: %s, cmd_vel: (%lf, %lf)",
        plugin_name_.c_str(),
        cmd_vel.twist.linear.x,
        cmd_vel.twist.angular.z
    );

    return cmd_vel;
}

/**
 * @brief 设置路径规划
 * @param path 规划路径
 */
void CustomController::setPlan(const nav_msgs::msg::Path& path) { global_plan_ = path; };

/**
 * @brief 设置速度限制
 * @param speed_limit 速度限制
 * @param percentage 是否为百分比
 */
void CustomController::setSpeedLimit(const double& speed_limit, const bool& percentage) {
    (void)speed_limit;
    (void)percentage;
}

/**
 * @brief 获取最近的目标位姿
 * @param current_pose 当前位姿
 * @return 最近的目标位姿
 * 
 * @note 
 * 总策略 \note
 * 当目标点方向与当前方向角度差较大时, 则原地旋转至同方向; 否则, 向目标点直线前进 \note
 * 因为要跟随路径, 所以目标点不是路径终点, 而是当前最近点的下一个点 \note
 */
geometry_msgs::msg::PoseStamped
CustomController::getNearestTargetPose(const geometry_msgs::msg::PoseStamped& current_pose) {
    // 1. 遍历路径, 获取路径中距离当前最近点的索引, 存储到 nearest_pose_index
    int nearest_pose_index = 0;
    using nav2_util::geometry_utils::euclidean_distance;
    double min_distance = euclidean_distance(current_pose, global_plan_.poses.at(0));

    for (unsigned int i = 1; i < global_plan_.poses.size(); ++i) {
        double distance = euclidean_distance(current_pose, global_plan_.poses.at(i));
        if (distance < min_distance) {
            nearest_pose_index = i;
            min_distance = distance;
        }
    }

    // 2. 从路径中擦除头部到最近点的路径
    //    擦除后, 最近点成为索引为0的点
    global_plan_.poses.erase(
        std::begin(global_plan_.poses),
        std::begin(global_plan_.poses) + nearest_pose_index
    );

    // 3. 如果只剩一个点, 则直接返回这个点作为目标点;
    //    否则返回下一个点作为目标点
    if (global_plan_.poses.size() == 1) {
        return global_plan_.poses.at(0);
    }
    return global_plan_.poses.at(1);
}

/**
 * @brief 计算角度差
 * @param current_pose 当前位姿
 * @param target_pose 目标位姿
 * @return 角度差
 */
double CustomController::calculateAngleDifference(
    const geometry_msgs::msg::PoseStamped& current_pose,
    const geometry_msgs::msg::PoseStamped& target_pose
) {
    // 1. 获取当前角度
    float current_robot_yaw = tf2::getYaw(current_pose.pose.orientation);

    // 2. 获取目标点朝向
    float target_yaw = std::atan2(
        target_pose.pose.position.y - current_pose.pose.position.y,
        target_pose.pose.position.x - current_pose.pose.position.x
    );

    // 3. 计算角度差, 并转换到 -pi 到 pi
    double yaw_diffrence = target_yaw - current_robot_yaw;
    if (yaw_diffrence < -M_PI) {
        yaw_diffrence += 2.0 * M_PI;
    } else if (yaw_diffrence > M_PI) {
        yaw_diffrence -= 2.0 * M_PI;
    }
    return yaw_diffrence;
}

} // namespace nav2_custom_controller

#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(nav2_custom_controller::CustomController, nav2_core::Controller)
