"""
1. ros2 service list -t 查询当前活动服务列表
2. ros2 interface show turtlesim/srv/Spawn 查看服务接口结构
3. ros2 service call /spawn turtlesim/srv/Spawn "{x: 1, y: 1}" 调用服务(值与冒号之间必须有空格)

4. ros2 param list 查看活动参数列表
5. ros2 param deacribe /turtlesim background_r 查看指定节点的参数描述
6. ros2 param get /turtlesim background_r 获取指定节点的参数值
7. ros2 param set /turtlesim background_r 0.0 设置指定节点的参数值
8. ros2 param dump /turtlesim > turtlesim_params.yaml 将节点参数导出到文件
9. ros2 run demo_python_service face_detect_seerver --ros-args -p face_locations_model:=hog 指定参数值启动节点
10. ros2 run turtlesim turtlesim_node --ros-args --params-file turtlesim_params.yaml 使用参数文件启动节点

11. self.set_parameters([rclpy.Parameter("face_locations_model", rclpy.Parameter.Type.STRING, "hog")] 在脚本中设置参数值
"""

import time

import cv2
import face_recognition
import rclpy

# 用于拼接路径
from ament_index_python.packages import get_package_share_directory

# 导入自定义的服务接口类型
from chap4_interfaces.srv import FaceDetector

# 用于转换格式
from cv_bridge import CvBridge

# 用于构建参数处理结果
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node


class FaceDetectorServer(Node):
    def __init__(self):
        super().__init__("face_detection_server")

        # 实例化格式转换器
        self.brige = CvBridge()
        # 创建人脸识别服务端: 类型 FaceDetector, 服务名 /face_detect
        self.server = self.create_service(
            FaceDetector,
            "/face_detect",
            self.detect_face_callback,
        )
        # 默认图像路径
        self.default_image_path = (
            get_package_share_directory("demo_python_service") + "/resource/default.jpg"
        )

        # 声明参数
        # 参数名: face_locations_upsample_times, 默认值: 1
        self.declare_parameter("face_locations_upsample_times", 1)
        # 参数名: face_locations_model, 默认值: hog
        self.declare_parameter("face_locations_model", "hog")

        # 获取参数值 (注意: 建议使用 get_parameter_value().***_value 获取指定类型的值, 否则Pylance会报错)
        self.upsample_times = (
            self.get_parameter("face_locations_upsample_times")
            .get_parameter_value()
            .integer_value
        )
        self.model = (
            self.get_parameter("face_locations_model")
            .get_parameter_value()
            .string_value
        )

        # 添加参数回调函数
        self.add_on_set_parameters_callback(self.parameters_callback)

    def detect_face_callback(self, request, response):
        """
        服务回调函数
        Args:
            request: 请求消息
            response: 响应消息
        Returns:
            response: 响应消息
        """

        # 1. 获取请求
        if request.image.data:
            # 请求图像非空, 处理请求图像
            cv_image = self.brige.imgmsg_to_cv2(request.image)
        else:
            # 请求图像为空, 处理默认图像
            cv_image = cv2.imread(self.default_image_path)

        self.get_logger().info("Have Loaded Image, Start Detecting...")
        start_time = time.time()

        # 2. 核心: 识别人脸
        face_locations = face_recognition.face_locations(
            cv_image,
            number_of_times_to_upsample=self.upsample_times,
            model=self.model,
        )

        end_time = time.time()
        self.get_logger().info(f"Detect Finished, Cost {end_time - start_time}s")

        # 3. 封装响应
        response.number = len(face_locations)
        response.use_time = end_time - start_time
        for top, right, bottom, left in face_locations:
            response.top.append(top)
            response.right.append(right)
            response.bottom.append(bottom)
            response.left.append(left)

        return response

    def parameters_callback(self, parameters):
        """
        参数回调函数
        Args:
            parameters: 参数列表
        Returns:
            SetParametersResult: 参数设置结果
        """
        # 遍历参数列表, 根据参数名更新参数值
        for parameter in parameters:
            self.get_logger().info(
                f"Parameter: {parameter.name} is changed to {parameter.value}"
            )
            if parameter.name == "face_locations_upsample_times":
                self.upsample_times = parameter.value
            if parameter.name == "face_locations_model":
                self.model = parameter.value

        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    server = FaceDetectorServer()
    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        pass
    finally:
        server.destroy_node()
        rclpy.shutdown()
