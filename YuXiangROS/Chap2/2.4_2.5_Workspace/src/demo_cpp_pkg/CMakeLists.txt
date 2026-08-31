cmake_minimum_required(VERSION 3.20)
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
include_directories(include) # 添加头文件目录
# 2. 添加可执行文件 cpp_node
add_executable(cpp_node src/cpp_node.cpp)
add_executable(person_node src/person_node.cpp)
add_executable(writer_node src/writer_node.cpp)
add_executable(learn_thread src/learn_thread.cpp) # 在这里添加更多节点
# 3. 为 cpp_node 添加 rclcpp 依赖
ament_target_dependencies(cpp_node rclcpp)
ament_target_dependencies(person_node rclcpp) 
ament_target_dependencies(writer_node rclcpp)
ament_target_dependencies(learn_thread rclcpp) # 在这里添加更多节点
target_link_libraries(learn_thread cpp-httplib) # 由apt安装的httplib编译时需添加此行
install(TARGETS
cpp_node person_node writer_node learn_thread
  DESTINATION lib/${PROJECT_NAME}) # 在这里添加更多节点

install(DIRECTORY 
  include/
  DESTINATION include/
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
