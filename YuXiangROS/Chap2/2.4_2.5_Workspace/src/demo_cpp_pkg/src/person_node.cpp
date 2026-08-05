/*
1. 一包多节点: 在一个包中可以包含多个节点, 在CMakeLists.txt中添加:
	add_executable(person_node src/person_node.cpp)
	target_link_libraries(person_node rclcpp)
	install(TARGETS person_node DESTINATION lib/${PROJECT_NAME})

2. 节点类化: 将节点封装为类, 便于管理
*/

#include <rclcpp/rclcpp.hpp>
#include <string>

class PersonNode : public rclcpp::Node {
  private:
    std::string name_;
    int age_;

  public:
    PersonNode(const std::string& node_name, const std::string& name, const int& age)
        : Node(node_name) {
        this->name_ = name;
        this->age_ = age;
    }

    void say_hello(const std::string& hobby) {
        RCLCPP_INFO(
            this->get_logger(),
            "Hello, my name is %s, and I am %d years old. I like %s.",
            this->name_.c_str(),
            this->age_,
            hobby.c_str()
        );
    } // .c_str() 将string转换为const char*
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto person_node = std::make_shared<PersonNode>("person_node", "ChangLi", 20);
    person_node->say_hello("reading");
    rclcpp::spin(person_node);
    rclcpp::shutdown();
    return 0;
}