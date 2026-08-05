#ifndef NAV2_CUSTOM_CONTROLLER_HPP
#define NAV2_CUSTOM_CONTROLLER_HPP

#include <memory>
#include <nav2_core/controller.hpp>
#include <nav2_util/robot_utils.hpp>
#include <rclcpp/rclcpp.hpp>
#include <string>
#include <vector>

namespace nav2_custom_controller {

/**
 * @note 
 * 控制器变量习惯上会注册为 protected 类型, 从而具有在继承时的扩展能力
 */
class CustomController : public nav2_core::Controller {

  protected:
    // 插件名
    std::string plugin_name_;
    // 坐标变换缓存指针, 可用于查询坐标关系
    std::shared_ptr<tf2_ros::Buffer> tf_;
    // 代价地图
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros_;
    // 节点指针
    nav2_util::LifecycleNode::SharedPtr node_;
    // 全局代价地图
    nav2_costmap_2d::Costmap2D* costmap_;
    // setPlan 提供的全局路径
    nav_msgs::msg::Path global_plan_;
    // 最大线速度
    double max_linear_velocity_;
    // 最大角速度
    double max_angular_velocity_;

    // 获取路径中距离当前最近的点
    geometry_msgs::msg::PoseStamped
    getNearestTargetPose(const geometry_msgs::msg::PoseStamped& current_pose);

    // 计算目标点方向和当前方向的角度差
    double calculateAngleDifference(
        const geometry_msgs::msg::PoseStamped& current_pose,
        const geometry_msgs::msg::PoseStamped& target_pose
    );

  public:
    CustomController() = default;
    ~CustomController() override = default;

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

    // 速度控制
    geometry_msgs::msg::TwistStamped computeVelocityCommands(
        const geometry_msgs::msg::PoseStamped& pose, const geometry_msgs::msg::Twist& velocity,
        nav2_core::GoalChecker* goal_checker
    ) override;

    // 设置路径规划
    void setPlan(const nav_msgs::msg::Path& path) override;

    // 设置速度限制
    void setSpeedLimit(const double& speed_limit, const bool& percentage) override;
};

} // namespace nav2_custom_controller

#endif // NAV2_CUSTOM_CONTROLLER_HPP