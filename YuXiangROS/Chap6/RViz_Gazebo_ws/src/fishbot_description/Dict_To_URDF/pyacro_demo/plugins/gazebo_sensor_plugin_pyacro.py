"""
gazebo_sensor_plugin.xacro

对应 urdf/fishbot/plugins/gazebo_sensor_plugin.xacro，
用 Python 字典描述 Gazebo Harmonic 下的激光雷达、IMU、RGBD 相机传感器。
"""


def make_gazebo_sensor_plugin() -> list:
    """返回 gazebo 传感器插件字典列表，与 xacro 宏一一对应。"""
    return [
        {
            "reference": "laser_link",
            "sensor": {
                "@name": "laserscan",
                "@type": "gpu_lidar",
                "always_on": True,
                "visualize": True,
                # [修改说明] 2026-07-26: 跟随 xacro 更新，激光雷达 update_rate 从 5 改为 20，
                #           满足 SLAM 扫描建议的 10-20Hz。
                "update_rate": 20,
                "pose": "0 0 0 0 0 0",
                "topic": "scan",
                "frame_id": "laser_link",
                "gz_frame_id": "laser_link",
                "lidar": {
                    "scan": {
                        "horizontal": {
                            "samples": 360,
                            "resolution": 1.000000,
                            "min_angle": 0.000000,
                            "max_angle": 6.280000,
                        }
                    },
                    "range": {
                        "min": 0.120000,
                        "max": 8.0,
                        "resolution": 0.015000,
                    },
                    "noise": {
                        "type": "gaussian",
                        "mean": 0.0,
                        "stddev": 0.01,
                    },
                },
            },
        },
        {
            "reference": "imu_link",
            "sensor": {
                "@name": "imu_sensor",
                "@type": "imu",
                "topic": "imu",
                "frame_id": "imu_link",
                "gz_frame_id": "imu_link",
                "update_rate": 100,
                "always_on": True,
                "imu": {
                    "angular_velocity": {
                        "x": _make_imu_noise(),
                        "y": _make_imu_noise(),
                        "z": _make_imu_noise(),
                    },
                    "linear_acceleration": {
                        "x": _make_imu_noise(
                            stddev=1.7e-2,
                            bias_mean=0.1,
                            bias_stddev=0.001,
                        ),
                        "y": _make_imu_noise(
                            stddev=1.7e-2,
                            bias_mean=0.1,
                            bias_stddev=0.001,
                        ),
                        "z": _make_imu_noise(
                            stddev=1.7e-2,
                            bias_mean=0.1,
                            bias_stddev=0.001,
                        ),
                    },
                },
            },
        },
        {
            "reference": "camera_link",
            "sensor": {
                "@name": "camera_sensor",
                "@type": "rgbd_camera",
                "topic": "camera",
                "frame_id": "camera_optical_link",
                "gz_frame_id": "camera_optical_link",
                "always_on": True,
                "update_rate": 10,
                "camera": {
                    "@name": "camera",
                    "horizontal_fov": 1.5009831567,
                    "image": {
                        "width": 800,
                        "height": 600,
                        "format": "R8G8B8",
                    },
                    "distortion": {
                        "k1": 0.0,
                        "k2": 0.0,
                        "k3": 0.0,
                        "p1": 0.0,
                        "p2": 0.0,
                        "center": "0.5 0.5",
                    },
                },
            },
        },
    ]


def _make_imu_noise(
    stddev: float = 2e-4,
    bias_mean: float = 0.0000075,
    bias_stddev: float = 0.0000008,
) -> dict:
    """生成 IMU 高斯噪声字典，对应 xacro 中重复的 noise 块。"""
    return {
        "noise": {
            "@type": "gaussian",
            "mean": 0.0,
            "stddev": stddev,
            "bias_mean": bias_mean,
            "bias_stddev": bias_stddev,
        }
    }
