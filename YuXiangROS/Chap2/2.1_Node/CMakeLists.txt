cmake_minimum_required(VERSION 3.8)

project(ros2_cpp)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 设置 C++ 标准（Jazzy 推荐 C++20）
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(ros2_cpp_node src/ros2_cpp_node.cpp)

find_package(rclcpp REQUIRED)

target_include_directories(ros2_cpp_node PUBLIC ${rclcpp_INCLUDE_DIRS})

target_link_libraries(ros2_cpp_node ${rclcpp_LIBRARIES})