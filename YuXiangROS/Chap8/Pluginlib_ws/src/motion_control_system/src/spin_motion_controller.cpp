#include "motion_control_system/spin_motion_controller.hpp"
#include <iostream>

namespace motion_control_system {

void SpinMotionController::start() {
    // TODO: 实现控制逻辑
    std::cout << "SpinMotionController::start" << std::endl;
}
void SpinMotionController::stop() {
    // TODO: 实现停止逻辑
    std::cout << "SpinMotionController::stop" << std::endl;
}
} // namespace motion_control_system

#include <pluginlib/class_list_macros.hpp>
// 对自定义插件进行导出
PLUGINLIB_EXPORT_CLASS(
    motion_control_system::SpinMotionController, motion_control_system::MotionController
)