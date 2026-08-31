import os

import cv2
import rclpy
from autopatrol_interfaces.srv import SpeachText
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.time import Duration, Time
from sensor_msgs.msg import Image
from tf2_ros import Buffer, TransformListener
from tf_transformations import euler_from_quaternion, quaternion_from_euler


class PatrolNode(BasicNavigator):
    def __init__(self, node_name="patrol_node"):
        super().__init__(node_name)

        # 创建缓冲区, 用于存储TF数据帧
        self.buffer_ = Buffer()
        # 创建监听器, 用于订阅TF数据
        self.listener_ = TransformListener(self.buffer_, self)

        # 声明自动巡检参数
        # 参数名: initial_point, 默认值: [0.0, 0.0, 0.0]
        # 参数名: target_points, 默认值: [0.0, 0.0, 0.0, 1.0, 1.0, 1.57]
        # 注意: 要加.0 否则会识别为 int 类型
        self.declare_parameter("initial_point", [0.0, 0.0, 0.0])
        self.declare_parameter("target_points", [0.0, 0.0, 0.0, 1.0, 1.0, 1.57])

        self.initial_point_ = self.get_parameter("initial_point").get_parameter_value().double_array_value
        self.target_points_ = self.get_parameter("target_points").get_parameter_value().double_array_value

        # 创建语音合成客户端: 类型 SpeachText, 服务名 /speach_text
        self.speach_client = self.create_client(SpeachText, "/speach_text")

        # 声明图像保存路径参数
        # 参数名: image_save_path, 默认值: ""
        self.declare_parameter(
            "image_save_path",
            "",
        )
        self.image_save_path_ = self.get_parameter("image_save_path").get_parameter_value().string_value

        # 实例化格式转换器
        self.bridge = CvBridge()
        self.latest_image = None
        # 创建图像订阅器: 类型 Image, 话题名 /camera/image, 队列大小 10
        self.subscription_image = self.create_subscription(Image, "/camera/image", self.image_callback, 10)

    def get_pose_by_xyyaw(self, x, y, yaw):
        """
        通过 x, y, yaw 合成 PoseStamped 消息对象

        Args:
            x : x 坐标
            y : y 坐标
            yaw : 偏航角
        """

        # 实例化消息对象
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        rotation_quat = quaternion_from_euler(0, 0, yaw)
        pose.pose.orientation.x = rotation_quat[0]
        pose.pose.orientation.y = rotation_quat[1]
        pose.pose.orientation.z = rotation_quat[2]
        pose.pose.orientation.w = rotation_quat[3]
        return pose

    def init_robot_pose(self):
        """
        初始化机器人位姿
        """

        # 从参数获取初始化点
        self.initial_point_ = self.get_parameter("initial_point").get_parameter_value().double_array_value
        # 合成位姿并调用初始化
        self.setInitialPose(
            self.get_pose_by_xyyaw(
                self.initial_point_[0],
                self.initial_point_[1],
                self.initial_point_[2],
            )
        )
        # 等待 nav2 激活
        self.waitUntilNav2Active()

    def get_target_points(self):
        """
        通过参数值获取目标点集合
        """

        points = []
        self.target_points_ = self.get_parameter("target_points").get_parameter_value().double_array_value

        # 按三个一组进行分割
        for index in range(int(len(self.target_points_) / 3)):
            x = self.target_points_[index * 3]
            y = self.target_points_[index * 3 + 1]
            yaw = self.target_points_[index * 3 + 2]

            # 重新拼装为二维数组
            points.append([x, y, yaw])
            self.get_logger().info(f"Find Target Point: {index}->({x}, {y}, {yaw})")
        return points

    def nav_to_pose(self, target_pose):
        """
        导航到指定位姿

        Args:
            target_pose : 目标位姿集合
        """

        # 等待 nav2 激活
        self.waitUntilNav2Active()

        self.goToPose(target_pose)

        while not self.isTaskComplete():
            feedback = self.getFeedback()
            if feedback is None:
                self.get_logger().info("No feedback available")
                continue

            self.get_logger().info(f"Remaining Distance: {feedback.distance_remaining:.2f} m")

        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Navigation succeeded")
        elif result == TaskResult.CANCELED:
            self.get_logger().warn("Navigation canceled")
        elif result == TaskResult.FAILED:
            self.get_logger().error("Navigation failed")
        else:
            self.get_logger().error("Navigation unknown result")

    def get_current_pose(self):
        """
        通过TF获取当前位姿
        """
        while rclpy.ok():
            try:
                # 获取TF数据帧
                result = self.buffer_.lookup_transform(
                    "map",
                    "base_footprint",
                    Time(seconds=0),  # 获取最近的TF
                    Duration(seconds=1),  # 超时时间
                )

                # 获取TF数据帧中的位姿数据
                transform = result.transform
                rotation_euler = euler_from_quaternion(
                    [
                        transform.rotation.x,
                        transform.rotation.y,
                        transform.rotation.z,
                        transform.rotation.w,
                    ]
                )
                self.get_logger().info(
                    f"Transform: translation={transform.translation}, rotation_quaternion={transform.rotation}, rotation_euler={rotation_euler}"
                )
                return transform

            except Exception as e:
                self.get_logger().warn(f"Can't get TF, reason: {str(e)}")

    def speach_text(self, text):
        # 1. 等待服务端启动
        while self.speach_client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info("Service not available, waiting again...")

        # 2. 实例化请求消息
        request = SpeachText.Request()
        request.text = text

        # 3. 发送请求
        future = self.speach_client.call_async(request)

        def async_callback(result_future):
            """
            异步回调函数
            Args:
                result_future: 异步结果
            """

            # 4. 处理异步响应
            response = result_future.result()

            if response.result:
                self.get_logger().info(f"Speach Text: {text} successfully")
            else:
                self.get_logger().warn(f"Speach Text: {text} failed")

        future.add_done_callback(async_callback)

    def image_callback(self, msg):
        """
        订阅回调函数

        Args:
            msg : 最新图像消息
        """
        self.latest_image = msg

    def record_image(self):
        if self.latest_image is not None:
            # 获取当前位姿(用于图片命名)
            pose = self.get_current_pose()
            if pose is None:
                return

            cv_image = self.bridge.imgmsg_to_cv2(self.latest_image)

            filename = f"image_{pose.translation.x:3.2f}_{pose.translation.y:3.2f}.jpg"
            full_path = os.path.join(self.image_save_path_, filename)
            cv2.imwrite(full_path, cv_image)
            self.get_logger().info(f"Image saved to: {full_path}")


def main(args=None):
    rclpy.init(args=args)
    patrol = PatrolNode()
    patrol.init_robot_pose()

    while rclpy.ok():
        # 全部目标点
        points = patrol.get_target_points()
        # 逐个点巡逻
        for point in points:
            x, y, yaw = point[0], point[1], point[2]
            target_pose = patrol.get_pose_by_xyyaw(x, y, yaw)
            # 播报当前目标
            patrol.speach_text(text=f"Targets already: {x}, {y}")
            patrol.nav_to_pose(target_pose)

            # 到达目标后，记录图像
            patrol.speach_text(text=f"Reached: {x}, {y}. Recording image.")
            patrol.record_image()
            patrol.speach_text(text="Image recorded.")

    patrol.destroy_node()
    rclpy.shutdown()
