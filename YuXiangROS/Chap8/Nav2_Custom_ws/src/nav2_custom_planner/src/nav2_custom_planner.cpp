#include "nav2_custom_planner/nav2_custom_planner.hpp"

#include <cmath>
#include <memory>
// #include <nav2_core/exceptions.hpp> // 在 Jazzy 版本已经拆分并移除
#include <nav2_core/planner_exceptions.hpp> // 原 exceptions 的子集, 用于 PlannerException
#include <nav2_util/node_utils.hpp>
#include <string>

namespace nav2_custom_planner {

void CustomPlanner::configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr& parent, std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf, std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros
) {
    tf_ = tf;
    plugin_name_ = name;
    costmap_ = costmap_ros->getCostmap();
    global_frame_ = costmap_ros->getGlobalFrameID();

    // 声明并获取参数
    // 插件类并没有继承 rclcpp::Node, 而是将节点指针作为参数通过 configure 传入并存储到成员变量中
    node_ = parent.lock();
    nav2_util::declare_parameter_if_not_declared(
        node_,
        plugin_name_ + ".interpolation_resolution",
        rclcpp::ParameterValue(0.1)
    );
    node_->get_parameter(plugin_name_ + ".interpolation_resolution", interpolation_resolution_);
}

void CustomPlanner::cleanup() {
    RCLCPP_INFO(
        node_->get_logger(),
        "Cleaning up plugin, type: CustomPlanner, name: %s",
        plugin_name_.c_str()
    );
}

void CustomPlanner::activate() {
    RCLCPP_INFO(
        node_->get_logger(),
        "Activating plugin, type: CustomPlanner, name: %s",
        plugin_name_.c_str()
    );
}

void CustomPlanner::deactivate() {
    RCLCPP_INFO(
        node_->get_logger(),
        "Deactivating plugin, type: CustomPlanner, name: %s",
        plugin_name_.c_str()
    );
}

/**
 * @brief 最简单的直线路径规划: 有障碍就拒绝, 无障碍物则直接返回直线路径
 * @param start 起始位姿
 * @param goal 目标位姿
 * @param cancel_checker 取消检查器, 用于检查是否取消了当前的路径规划请求
 * @return 全局路径
 * 
 * @note
 * cancel_checker 是 Jazzy版本新增参数, 可做如下处理以消除"未使用Warning": \note
 * 1. 在参数列表中注释 std::function<bool()> *cancel_checker*(此处为块注释) \note
 * 2. 在函数开头添加 (void)cancel_checker; , 从而欺骗编译器 \note 
 * 3. 在生成路径时检查 cancel_checker 是否有效, 这种最符合 ROS2 设计预期 \note
 */
nav_msgs::msg::Path CustomPlanner::createPlan(
    const geometry_msgs::msg::PoseStamped& start, const geometry_msgs::msg::PoseStamped& goal,
    std::function<bool()> cancel_checker
) {
    // 1. 声明并初始化全局路径
    nav_msgs::msg::Path global_path;
    global_path.poses.clear();
    global_path.header.stamp = node_->now();
    global_path.header.frame_id = global_frame_;

    // 2. 检查起始与目标是否在全局坐标系中
    if (start.header.frame_id != global_frame_) {
        RCLCPP_ERROR(
            node_->get_logger(),
            "Start pose is not in the global frame, frame_id: %s, global_frame: %s",
            start.header.frame_id.c_str(),
            global_frame_.c_str()
        );
        return global_path;
    }
    if (goal.header.frame_id != global_frame_) {
        RCLCPP_ERROR(
            node_->get_logger(),
            "Goal pose is not in the global frame, frame_id: %s, global_frame: %s",
            goal.header.frame_id.c_str(),
            global_frame_.c_str()
        );
        return global_path;
    }

    // 3. 计算当前差值分辨率下的循环次数和步进值
    int total_number_of_loop = std::hypot(
                                   goal.pose.position.x - start.pose.position.x,
                                   goal.pose.position.y - start.pose.position.y
                               ) /
                               interpolation_resolution_;
    double x_increment = (goal.pose.position.x - start.pose.position.x) / total_number_of_loop;
    double y_increment = (goal.pose.position.y - start.pose.position.y) / total_number_of_loop;

    // 4. 生成路径
    for (int i = 0; i < total_number_of_loop; ++i) {
        // 检查是否被取消
        if (cancel_checker()) {
            // 直接返回已经生成的路径
            // 由于到目前为止, 路径 global_path 中没有任何点, Nav2 会自动取消当前的路径规划请求
            return global_path;
        }

        // 生成一个点
        geometry_msgs::msg::PoseStamped pose;
        pose.pose.position.x = start.pose.position.x + x_increment * i;
        pose.pose.position.y = start.pose.position.y + y_increment * i;
        pose.pose.position.z = 0.0;
        pose.header.stamp = node_->now();
        pose.header.frame_id = global_frame_;

        // 将该点放到路径中
        global_path.poses.push_back(pose);
    }

    // 5. 检测路径是否经过障碍物
    for (geometry_msgs::msg::PoseStamped pose : global_path.poses) {
        // 将点坐标转换为栅格坐标
        unsigned int mx, my;
        if (costmap_->worldToMap(pose.pose.position.x, pose.pose.position.y, mx, my)) {
            // 获取对应栅格的代价值
            unsigned char cost = costmap_->getCost(mx, my);

            //如果存在致命障碍物则抛出异常
            if (cost == nav2_costmap_2d::LETHAL_OBSTACLE) {
                RCLCPP_WARN(
                    node_->get_logger(),
                    "Path passes through lethal obstacle at position (x: %.2f, y: %.2f)",
                    pose.pose.position.x,
                    pose.pose.position.y
                );
                throw nav2_core::PlannerException(
                    "Can't plan path to goal: (" + std::to_string(goal.pose.position.x) + ", " +
                    std::to_string(goal.pose.position.y) + ")"
                );
            }
        }
    }

    // 6. 将目标点作为路径的最后一个点并返回路径
    geometry_msgs::msg::PoseStamped last_pose = goal;
    last_pose.header.stamp = node_->now();
    last_pose.header.frame_id = global_frame_;
    global_path.poses.push_back(last_pose);

    return global_path;
}

} // namespace nav2_custom_planner

#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(nav2_custom_planner::CustomPlanner, nav2_core::GlobalPlanner)
