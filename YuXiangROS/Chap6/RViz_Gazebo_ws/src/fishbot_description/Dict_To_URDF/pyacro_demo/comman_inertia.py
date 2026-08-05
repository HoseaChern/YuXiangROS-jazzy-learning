"""
comman_inertia.xacro
"""


def box_inertia(m: float, w: float, h: float, d: float) -> list:
    """
    长方体惯性张量 (绕几何中心)
    对应 <xacro:box_inertia m="..." w="..." h="..." d="..."/>
    """
    return [
        (m / 12) * (h * h + d * d),  # ixx
        0.0,  # ixy
        0.0,  # ixz
        (m / 12) * (w * w + d * d),  # iyy
        0.0,  # iyz
        (m / 12) * (w * w + h * h),  # izz
    ]


def cylinder_inertia(m: float, r: float, h: float) -> list:
    """
    圆柱体惯性张量 (绕中心轴)
    对应 <xacro:cylinder_inertia m="..." r="..." h="..."/>

    [修改说明] 2026-07-26: ixy / ixz / iyz 使用 0 而非 0.0，与 xacro 中
               cylinder_inertia 宏的输出格式保持一致。
    """
    return [
        (m / 12) * (3 * r * r + h * h),  # ixx
        0,  # ixy
        0,  # ixz
        (m / 12) * (3 * r * r + h * h),  # iyy
        0,  # iyz
        (m / 2) * (r * r),  # izz
    ]


def sphere_inertia(m: float, r: float) -> list:
    """
    球体惯性张量
    对应 <xacro:sphere_inertia m="..." r="..."/>
    """
    return [
        (2 / 5) * m * (r * r),  # ixx
        0.0,  # ixy
        0.0,  # ixz
        (2 / 5) * m * (r * r),  # iyy
        0.0,  # iyz
        (2 / 5) * m * (r * r),  # izz
    ]
