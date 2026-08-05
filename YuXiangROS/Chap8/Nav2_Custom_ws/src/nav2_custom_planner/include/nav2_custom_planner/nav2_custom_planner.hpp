#ifndef NAV2_CUSTOM_PLANNER_HPP
#define NAV2_CUSTOM_PLANNER_HPP

#include <geometry_msgs/msg/point.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <memory>
#include <nav2_core/global_planner.hpp>
#include <nav2_costmap_2d/costmap_2d_ros.hpp>
#include <nav2_util/lifecycle_node.hpp>
#include <nav2_util/robot_utils.hpp>
#include <nav_msgs/msg/path.hpp>
#include <rclcpp/rclcpp.hpp>
#include <string>

namespace nav2_custom_planner {

// 自定义导航规划器类
class CustomPlanner : public nav2_core::GlobalPlanner {

  private:
    // 坐标变换缓存指针, 可用于查询坐标关系
    std::shared_ptr<tf2_ros::Buffer> tf_;
    // 节点指针
    nav2_util::LifecycleNode::SharedPtr node_;
    // 全局代价地图
    nav2_costmap_2d::Costmap2D* costmap_;
    // 全局代价地图的坐标系名
    std::string global_frame_;
    // 插件名
    std::string plugin_name_;
    // 差值分辨率
    double interpolation_resolution_;

  public:
    CustomPlanner() = default;
    ~CustomPlanner() = default;

    // 插件配置方法
    void configure(
        const rclcpp_lifecycle::LifecycleNode::WeakPtr& parent, std::string name,
        std::shared_ptr<tf2_ros::Buffer> tf,
        std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros
    ) override;

    // 插件清理方法
    void cleanup() override;

    // 插件激活方法
    void activate() override;

    // 插件停用方法
    void deactivate() override;

    // 根据给定的起始和目标位姿创建路径的方法
    nav_msgs::msg::Path createPlan(
        const geometry_msgs::msg::PoseStamped& start, const geometry_msgs::msg::PoseStamped& goal,
        std::function<bool()> cancel_checker // 为 Jazzy 版本新增参数, 处理方法见.cpp实现
    ) override;
};

} // namespace nav2_custom_planner

#endif // NAV2_CUSTOM_PLANNER_HPP