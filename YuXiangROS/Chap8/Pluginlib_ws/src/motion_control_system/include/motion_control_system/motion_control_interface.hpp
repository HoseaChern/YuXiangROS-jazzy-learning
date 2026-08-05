#ifndef MOTION_CONTROL_INTERFACE_HPP
#define MOTION_CONTROL_INTERFACE_HPP

namespace motion_control_system {

// 抽象运动控制接口
// virtual 关键字用于声明虚函数
// = 0 语法用于声明纯虚函数
// 派生类必须重写纯虚函数, 至少有一个纯虚函数的类叫做抽象类
class MotionController {
  public:
    virtual void start() = 0;
    virtual void stop() = 0;
    virtual ~MotionController(){};
};

} // namespace motion_control_system

#endif // MOTION_CONTROL_INTERFACE_HPP