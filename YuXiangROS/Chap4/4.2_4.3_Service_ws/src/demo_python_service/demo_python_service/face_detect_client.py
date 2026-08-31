import cv2
import rclpy

# 用于拼接路径
from ament_index_python.packages import get_package_share_directory

# 导入自定义的服务接口类型
from chap4_interfaces.srv import FaceDetector

# 用于转换格式
from cv_bridge import CvBridge

# 用于构建参数服务消息
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue

# 导入参数服务的接口类型
from rcl_interfaces.srv import SetParameters
from rclpy.node import Node


class FaceDetectorClient(Node):
    def __init__(self):
        super().__init__("face_detection_client")

        # 实例化格式转换器
        self.brige = CvBridge()
        # 创建人脸识别客户端: 类型 FaceDetector, 服务名 /face_detect (注意: 这里没有回调函数传参)
        self.client = self.create_client(FaceDetector, "/face_detect")
        # 图像路径
        self.test1_image_path = get_package_share_directory("demo_python_service") + "/resource/test1.jpg"
        self.image = cv2.imread(self.test1_image_path)

        # 用于在回调中标记检测到人脸
        self.detection_result = None
        self.result_image = None
        # 用于标记窗口是否创建
        self.window_created = False

        # 用于存储多次检测结果，支持按键切换查看
        self.result_queue = []
        self.display_idx = 0

        # 创建定时器，每 30ms 刷新一次 OpenCV 窗口
        self.timer = self.create_timer(0.03, self._cv_spin)

    def _cv_spin(self):
        """
        定时器回调，非阻塞刷新 OpenCV 窗口
        """

        # 优先显示队列中的结果（支持多次请求切换查看, 窗口中按n下一张, 按p上一张, 按q关闭）
        if self.result_queue:
            if not self.window_created:
                cv2.namedWindow("Face Detection", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Face Detection", 800, 600)
                self.window_created = True

            display_img = self.result_queue[self.display_idx].copy()
            info = f"[{self.display_idx + 1}/{len(self.result_queue)}]  n:next  p:prev  q:close"
            cv2.putText(
                display_img,
                info,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Face Detection", display_img)
            # waitKey(1) 只等待 1ms，不会阻塞 Executor
            key = cv2.waitKey(1) & 0xFF
            if key == ord("n") and self.display_idx < len(self.result_queue) - 1:
                self.display_idx += 1
            elif key == ord("p") and self.display_idx > 0:
                self.display_idx -= 1
            elif key == ord("q"):
                self.result_queue.clear()
                self.display_idx = 0
                self.window_created = False
                cv2.destroyAllWindows()
        # 兼容单次结果显示
        elif self.result_image is not None:
            if not self.window_created:
                cv2.namedWindow("Face Detection", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Face Detection", 800, 600)
                self.window_created = True

            cv2.imshow("Face Detection", self.result_image)
            # waitKey(1) 只等待 1ms，不会阻塞 Executor
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.result_image = None
                self.window_created = False
                cv2.destroyAllWindows()

    def send_request(self):

        # 1. 等待服务端启动
        while self.client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info("Service not available, waiting again...")

        # 2. 实例化请求消息
        request = FaceDetector.Request()
        request.image = self.brige.cv2_to_imgmsg(self.image)

        # 3. 发送请求
        future = self.client.call_async(request)

        # 这里是写法1
        def async_callback(result_future):
            """
            异步回调函数
            Args:
                result_future: 异步结果
            """

            # 4. 处理异步响应
            response = result_future.result()
            self.get_logger().info(
                f"Response: There are {response.number} faces in the image, using time: {response.use_time}s"
            )

            # 在原图上画框（注意复制一份，避免修改原始图像）
            display_image = self.image.copy()
            for i in range(response.number):
                top = response.top[i]
                right = response.right[i]
                bottom = response.bottom[i]
                left = response.left[i]
                cv2.rectangle(
                    display_image,
                    (left, top),
                    (right, bottom),
                    (0, 0, 255),
                    4,
                )

            cv2.namedWindow("Face Detection", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Face Detection", 800, 600)
            # 将结果保存到成员变量，由定时器负责显示
            self.result_image = display_image
            # 加入结果队列，支持多次结果切换查看
            self.result_queue.append(display_image)
            self.display_idx = len(self.result_queue) - 1
            self.window_created = True

        future.add_done_callback(async_callback)

    def call_set_parameters(self, parameters):
        """
        参数更新服务
        Args:
            parameters: 参数列表
        Returns:
            future.result(): 参数更新结果
        """

        # 0. 创建参数更新客户端: 类型 SetParameters, 名称 /face_detection_server/set_parameters (注意: 服务名中应当为服务端节点名)
        param_client = self.create_client(SetParameters, "/face_detection_server/set_parameters")

        # 1. 等待服务端启动
        while not param_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service not available, waiting again...")

        # 2. 实例化请求消息
        request = SetParameters.Request()
        request.parameters = parameters

        # 3. 发送请求
        future = param_client.call_async(request)
        # 这里是写法2
        rclpy.spin_until_future_complete(self, future)
        return future.result()

    def update_detect_model(self, model):
        """
        更新检测模型
        Args:
            model: 模型名称
        """

        # 1. 实例化参数消息
        param = Parameter()

        # 2. 设置参数名称和值
        # 参数名: face_locations_model
        param.name = "face_locations_model"
        # 参数值: model
        new_model_value = ParameterValue()
        new_model_value.type = ParameterType.PARAMETER_STRING
        new_model_value.string_value = model
        param.value = new_model_value

        # 3. 发送请求并处理响应
        response = self.call_set_parameters([param])
        # 防御性写法, 否则Pylance会报错
        if response is None:
            self.get_logger().error(f"Update detect model to {model} failed")
            return

        for result in response.results:
            if result.successful:
                self.get_logger().info(f"Update {param.name} to {model} successfully")
            else:
                self.get_logger().info(f"Update {param.name} to {model} failed: {result.reason}")


def main(args=None):
    rclpy.init(args=args)

    client = FaceDetectorClient()
    client.update_detect_model("hog")
    client.send_request()
    client.update_detect_model("hog")
    client.send_request()

    try:
        rclpy.spin(client)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        client.destroy_node()
        rclpy.shutdown()
