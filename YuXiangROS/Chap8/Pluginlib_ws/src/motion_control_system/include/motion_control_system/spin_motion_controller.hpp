#ifndef SPIN_MOTION_CONTROLLER_HPP
#define SPIN_MOTION_CONTROLLER_HPP

#include "motion_control_system/motion_control_interface.hpp"
namespace motion_control_system {

class SpinMotionController : public MotionController {
  public:
    // override: 表示派生类成员函数将覆盖基类虚函数
    void start() override;
    void stop() override;
};

} // namespace motion_control_system
#endif // SPIN_MOTION_CONTROLLER_HPP