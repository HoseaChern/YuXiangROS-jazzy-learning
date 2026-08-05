/*
1. ros2 node info /turtlesim
查询节点关联的话题(与在话题中的身份和话题类型)&服务(与在服务中的身份和服务类型)&动作(与在动作中的身份和动作类型);
2. ros2 topic echo /turtle1/pose 查询指定话题上发布的消息;
3. ros2 topic info /turtle1/cmd_vel -v 查询话题具体信息;
4. ros2 interface show geometry_msgs/msg/Twist 查询话题接口类型具体结构;
5. ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}}" 在话题上/turtle1/cmd_vel发布消息.
*/

#include <chrono>                      // 时间相关头文件
#include <geometry_msgs/msg/twist.hpp> // 话题 /turtle1/cmd_vel 接口类型, 注意是.hpp
#include <rclcpp/rclcpp.hpp>

// 使用时间单位字面量, 可以使用s和ms表示时间
using namespace std::chrono_literals;

class TurtleCircle : public rclcpp::Node {
  private:
    // 定时器智能指针
    rclcpp::TimerBase::SharedPtr timer_;
    // 发布者智能指针: 话题 /turtle1/cmd_vel, 接口类型 geometry_msgs::msg::Twist
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;

  public:
    /*
	  explicit: 修饰构造函数, 禁止隐式类型转换, 只有明确写出构造函数句式才允许编译, 如:
	  - TurtleCircle node("turtle_circle");
	  - auto node = std::make_shared<TurtleCircle>("turtle_circle").
	  单参数构造函数是隐式转换的重灾区!
	  */
    explicit TurtleCircle(const std::string& node_name) : Node(node_name) {
        // 创建速度发布者: 话题 /turtle1/cmd_vel, 接口类型 geometry_msgs::msg::Twist, 队列大小为10
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
        // 创建定时器: 调用周期 1s
        // 在成员上下文中, 访问私有方法是合法的
        timer_ = this->create_wall_timer(1s, std::bind(&TurtleCircle::timer_callback_, this));
    }

  private:
    /*
    定时器回调函数
    
	  private封装: 禁止在类与友元的外部调用, 符合C++最小权限原则:
	  1. bind: 将函数timer_callback与对象this绑定;
	  2. 得到一个匿名的函数对象, 传给 rclcpp 库;
	  3. rclcpp::spin在类外部轮询时, 会调用匿名函数对象, 从而调用timer_callback.
	  */
    void timer_callback_() {
        auto msg = geometry_msgs::msg::Twist(); // 实例化一则消息
        msg.linear.x = 1.0;                     // geometry_msgs/msg/Twist: x方向线速度
        msg.angular.z = 0.5;                    // geometry_msgs/msg/Twist: z方向角速度
        publisher_->publish(msg);               // 在话题上发布速度消息
    }
};

// 先启动turtlesim_node, 再启动turtle_circle
int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleCircle>("turtle_circle");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}