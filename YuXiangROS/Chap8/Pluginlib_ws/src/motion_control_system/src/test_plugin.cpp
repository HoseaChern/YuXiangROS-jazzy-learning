/*
调用方法
source ./install/setup.zsh
ros2 run motion_control_system test_plugin motion_control_system/SpinMotionController

其中 motion_control_system/SpinMotionController 是插件名称, 需要和 spin_motion_plugins.xml 中定义的名称一致
*/

#include "motion_control_system/motion_control_interface.hpp"
#include <pluginlib/class_loader.hpp>

int main(int argc, char* argv[]) {

    // 检查参数个数是否合法
    if (argc != 2) {
        return 1;
    }

    // 通过命令行参数, 选择要加载的插件
    // argv[0] 是可执行文件名; argv[1] 是参数名(预期为控制器名称)
    // 在这里, 控制器名称就是在 spin_motion_plugins.xml 中定义的名称
    std::string controller_name = argv[1];

    // 通过功能包名和基类名, 创建插件加载器
    pluginlib::ClassLoader<motion_control_system::MotionController> controller_loader(
        "motion_control_system",
        "motion_control_system::MotionController"
    );

    // 使用加载器加载指定名称的插件, 返回的是指定插件类的对象的指针
    auto controller = controller_loader.createSharedInstance(controller_name);

    // 调用插件的方法
    controller->start();
    controller->stop();
    return 0;
}