import cv2
import face_recognition

# 用于拼接路径
from ament_index_python.packages import get_package_share_directory


def main():
    # 1. 获取图片真实路径
    default_image_path = get_package_share_directory("demo_python_service") + "/resource/default.jpg"

    # 2. 使用 opencv 加载图像
    image = cv2.imread(default_image_path)

    # 3. 核心: 识别人脸
    face_locations = face_recognition.face_locations(
        image,
        number_of_times_to_upsample=1,
        model="hog",
    )

    # 4. 绘制边框
    for top, right, bottom, left in face_locations:
        cv2.rectangle(
            image,
            (left, top),
            (right, bottom),
            (0, 0, 255),
            4,
        )

    # 5. 创建并缩放窗口
    cv2.namedWindow("Face Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Face Detection", 800, 600)

    # 6. 显示结果图像
    cv2.imshow("Face Detection", image)
    cv2.waitKey(0)
