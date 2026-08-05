/*
1. 继承自父类
2. 调用父类方法
*/

#include "demo_cpp_pkg/person_node.hpp" // 必须新建头文件, 否则main函数会重复定义
#include <rclcpp/rclcpp.hpp>
#include <string>

class WriterNode : public PersonNode {
  private:
    std::string book_;

  public:
    WriterNode(const std::string& book) : PersonNode("writer_node", "ChangLi", 20) {
        this->book_ = book;
    }

    void write_book() {
        RCLCPP_INFO(this->get_logger(), "I am writing a book titled '%s'.", this->book_.c_str());
    }
};

int main(int argc, char* argv[]) {
    rclcpp::init(argc, argv);
    auto writer_node = std::make_shared<WriterNode>("The Great Gatsby");
    writer_node->say_hello("reading");
    writer_node->write_book();
    rclcpp::spin(writer_node);
    rclcpp::shutdown();
    return 0;
}