#ifndef PERSON_NODE_HPP
#define PERSON_NODE_HPP

#include <rclcpp/rclcpp.hpp>
#include <string>

class PersonNode : public rclcpp::Node {
  private:
    std::string name_;
    int age_;

  public:
    PersonNode(const std::string& node_name, const std::string& name, const int& age)
        : Node(node_name), name_(name), age_(age) {}

    void say_hello(const std::string& hobby) {
        RCLCPP_INFO(
            this->get_logger(),
            "Hello, my name is %s, and I am %d years old. I like %s.",
            name_.c_str(),
            age_,
            hobby.c_str()
        );
    }
};

#endif // PERSON_NODE_HPP