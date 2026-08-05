import espeakng
import rclpy
from autopatrol_interfaces.srv import SpeachText
from rclpy.node import Node


class Speaker(Node):
    def __init__(self, node_name="speaker"):
        super().__init__(node_name)

        # 创建服务端: 类型 SpeachText, 服务名 /speach_text
        self.speach_service = self.create_service(
            SpeachText,
            "/speach_text",
            self.speach_text_callback,
        )

        # 创建语音合成器
        self.speaker = espeakng.Speaker()
        # 语言: 英语
        self.speaker.voice = "en"

    def speach_text_callback(self, request, response):
        """
        语音合成服务回调函数

        Args:
            request
            response

        Returns:
            response
        """
        self.get_logger().info("Speaking: %s" % request.text)

        # 合成语音并播放
        self.speaker.say(request.text)
        self.speaker.wait()

        response.result = True
        return response


def main(args=None):
    rclpy.init(args=args)
    speaker = Speaker()

    try:
        rclpy.spin(speaker)
    except KeyboardInterrupt:
        pass
    finally:
        speaker.destroy_node()
        rclpy.shutdown()
