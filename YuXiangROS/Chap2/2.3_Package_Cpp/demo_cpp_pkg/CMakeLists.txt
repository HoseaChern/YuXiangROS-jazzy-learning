cmake_minimum_required(VERSION 3.8)
project(demo_cpp_pkg)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.

# 以下是手动添加

# 1. 查找 rclcpp 头文件和库
find_package(rclcpp REQUIRED)
# 2. 添加可执行文件 cpp_node
add_executable(cpp_node src/cpp_node.cpp)
# 3. 为 cpp_node 添加 rclcpp 依赖
ament_target_dependencies(cpp_node rclcpp)
# 4. 将 cpp_node 复制到 install 目录下
install(TARGETS
  cpp_node
  DESTINATION lib/${PROJECT_NAME}
)

# 以上是手动添加


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
