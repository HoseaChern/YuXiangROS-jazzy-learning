#include <learn_compose/listener.hpp>
#include <learn_compose/talker.hpp>
#include <rclcpp/rclcpp.hpp>

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);

    rclcpp::NodeOptions options;           // 实例化节点选项
    options.use_intra_process_comms(true); // 启用进程内通信
    auto talker = std::make_shared<learn_compose::Talker>(options);
    auto listener = std::make_shared<learn_compose::Listener>(options);

    // 使用执行器组织多个节点
    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(talker);
    executor.add_node(listener);
    executor.spin();

    rclcpp::shutdown();
    return 0;
}

/**
 * 1. ros2 component types 查看已经注册的组件
 * 2. ros2 run rclcpp_components component_container --ros-args -r __node:=component_test 启动节点容器/component_test
 * 3. ros2 component list 查看容器列表
 * 4. ros2 component load /component_test learn_compose learn_compose::Talker -e use_intra_process_comms:=true 加载组建到节点
 * 5. ros2 component unload / component_test learn_compose::Talker 卸载组件
 */