cmake_minimum_required(VERSION 3.20)
project(demo_cpp_action)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(chap7_interfaces REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(turtlesim REQUIRED)

# 编译并链接动作服务端节点
add_executable(action_server src/action_server.cpp)
ament_target_dependencies(action_server chap7_interfaces rclcpp rclcpp_action geometry_msgs turtlesim)

# 编译并链接动作客户端节点
add_executable(action_client src/action_client.cpp)
ament_target_dependencies(action_client chap7_interfaces rclcpp rclcpp_action geometry_msgs turtlesim)

install(TARGETS
  action_server
  action_client
  DESTINATION lib/${PROJECT_NAME}
)

# 复制launch文件到 /install/share
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
