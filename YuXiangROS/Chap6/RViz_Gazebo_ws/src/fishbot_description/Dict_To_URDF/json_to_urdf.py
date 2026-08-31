#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON → URDF XML 转换器
======================
完整支持 URDF 1.0 规范的所有标准元素，包含命令行接口。

用法:
    python json_to_urdf.py robot.json -o robot.urdf
    python json_to_urdf.py robot.json -o robot.urdf --validate

JSON 格式规范见文件末尾的 SCHEMA 说明。
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ============================================================
# 数据模型 (URDF 元素)
# ============================================================


@dataclass
class Origin:
    """空间位姿: xyz [m] + rpy [rad]

    [修改说明] 2026-07-26: 增加 has_rpy 标志，记录 rpy 是否由用户显式提供。
               这样 <origin> 输出时可以与 xacro 保持一致：
               显式写了 rpy 才输出 rpy 属性，否则只输出 xyz（或不输出）。
    """

    xyz: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rpy: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    has_rpy: bool = False

    @classmethod
    def from_dict(cls, d: Optional[Dict]) -> "Origin":
        if d is None:
            return cls()
        return cls(
            xyz=d.get("xyz", [0.0, 0.0, 0.0]),
            rpy=d.get("rpy", [0.0, 0.0, 0.0]),
            has_rpy="rpy" in d,
        )


@dataclass
class Geometry:
    """几何形状: box | cylinder | sphere | mesh"""

    type: str  # "box", "cylinder", "sphere", "mesh"
    size: Optional[List[float]] = None  # box: [x, y, z]
    radius: Optional[float] = None  # cylinder / sphere
    length: Optional[float] = None  # cylinder
    filename: Optional[str] = None  # mesh
    scale: Optional[List[float]] = None  # mesh: [x, y, z]

    @classmethod
    def from_dict(cls, d: Dict) -> "Geometry":
        return cls(**d)


@dataclass
class Material:
    """材质/颜色定义"""

    name: str
    color: Optional[List[float]] = None  # rgba [0..1]
    texture: Optional[str] = None  # 纹理图片路径

    @classmethod
    def from_dict(cls, d: Dict) -> "Material":
        return cls(name=d["name"], color=d.get("color"), texture=d.get("texture"))


@dataclass
class Inertial:
    """惯性参数"""

    mass: float
    origin: Origin = field(default_factory=Origin)
    inertia: List[float] = field(default_factory=lambda: [0.0] * 6)
    # inertia 顺序: [ixx, ixy, ixz, iyy, iyz, izz]

    @classmethod
    def from_dict(cls, d: Dict) -> "Inertial":
        return cls(
            mass=d["mass"],
            origin=Origin.from_dict(d.get("origin")),
            inertia=d.get("inertia", [0.0] * 6),
        )


@dataclass
class Visual:
    """视觉属性"""

    geometry: Geometry
    origin: Origin = field(default_factory=Origin)
    # str=引用名, Material=内联定义
    material: Optional[Union[str, Material]] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Visual":
        mat = d.get("material")
        if isinstance(mat, str):
            material = mat
        elif isinstance(mat, dict):
            material = Material.from_dict(mat)
        else:
            material = None
        return cls(
            geometry=Geometry.from_dict(d["geometry"]),
            origin=Origin.from_dict(d.get("origin")),
            material=material,
        )


@dataclass
class Collision:
    """碰撞属性"""

    geometry: Geometry
    origin: Origin = field(default_factory=Origin)
    # [新增] 碰撞体也可附带材质，与 xacro 中常见写法保持一致
    material: Optional[Union[str, Material]] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Collision":
        mat = d.get("material")
        if isinstance(mat, str):
            material = mat
        elif isinstance(mat, dict):
            material = Material.from_dict(mat)
        else:
            material = None
        return cls(
            geometry=Geometry.from_dict(d["geometry"]),
            origin=Origin.from_dict(d.get("origin")),
            material=material,
        )


@dataclass
class Link:
    """连杆"""

    name: str
    visual: Optional[Visual] = None
    collision: Optional[Collision] = None
    inertial: Optional[Inertial] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Link":
        return cls(
            name=d["name"],
            visual=Visual.from_dict(d["visual"]) if "visual" in d else None,
            collision=Collision.from_dict(d["collision"]) if "collision" in d else None,
            inertial=Inertial.from_dict(d["inertial"]) if "inertial" in d else None,
        )


@dataclass
class Limit:
    """关节限位"""

    lower: float
    upper: float
    effort: float
    velocity: float

    @classmethod
    def from_dict(cls, d: Dict) -> "Limit":
        return cls(**d)


@dataclass
class Dynamics:
    """关节动力学: 阻尼 & 摩擦"""

    damping: Optional[float] = None
    friction: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Dynamics":
        return cls(damping=d.get("damping"), friction=d.get("friction"))


@dataclass
class Mimic:
    """从动关节"""

    joint: str
    multiplier: Optional[float] = None
    offset: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Mimic":
        return cls(joint=d["joint"], multiplier=d.get("multiplier"), offset=d.get("offset"))


@dataclass
class SafetyController:
    """安全控制器"""

    soft_lower_limit: Optional[float] = None
    soft_upper_limit: Optional[float] = None
    k_position: Optional[float] = None
    k_velocity: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "SafetyController":
        return cls(
            soft_lower_limit=d.get("soft_lower_limit"),
            soft_upper_limit=d.get("soft_upper_limit"),
            k_position=d.get("k_position"),
            k_velocity=d.get("k_velocity"),
        )


@dataclass
class Joint:
    """关节"""

    name: str
    type: str  # revolute, continuous, prismatic, fixed, floating, planar
    parent: str
    child: str
    origin: Origin = field(default_factory=Origin)
    axis: Optional[List[float]] = None
    limits: Optional[Limit] = None
    dynamics: Optional[Dynamics] = None
    mimic: Optional[Mimic] = None
    safety_controller: Optional[SafetyController] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Joint":
        return cls(
            name=d["name"],
            type=d["type"],
            parent=d["parent"],
            child=d["child"],
            origin=Origin.from_dict(d.get("origin")),
            axis=d.get("axis"),
            limits=Limit.from_dict(d["limits"]) if "limits" in d else None,
            dynamics=Dynamics.from_dict(d["dynamics"]) if "dynamics" in d else None,
            mimic=Mimic.from_dict(d["mimic"]) if "mimic" in d else None,
            safety_controller=SafetyController.from_dict(d["safety_controller"]) if "safety_controller" in d else None,
        )


@dataclass
class Transmission:
    """传动机构 (用于 ros2_control)"""

    name: str
    type: str
    joint: str
    actuator: str
    mechanical_reduction: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict) -> "Transmission":
        return cls(
            name=d["name"],
            type=d["type"],
            joint=d["joint"],
            actuator=d["actuator"],
            mechanical_reduction=d.get("mechanical_reduction"),
        )


# ============================================================
# Gazebo / ROS 2 Control 数据模型
# ============================================================


# [修改说明] 旧版使用 PLUGIN_REGISTRY 注册表和 SUPPORTED_SENSOR_TYPES 集合
#           来映射插件与传感器类型，导致无法表达当前 fishbot 中复杂的 Gazebo
#           配置。新版改为通用“字典 -> XML”映射，因此删除这些注册表。
#           详见本节开头注释与 _build_xml_from_dict 的“@属性 / #text”约定。


@dataclass
class Robot:
    """机器人模型根节点"""

    name: str
    links: List[Link] = field(default_factory=list)
    joints: List[Joint] = field(default_factory=list)
    materials: List[Material] = field(default_factory=list)
    transmissions: List[Transmission] = field(default_factory=list)  # 保留兼容旧版 ros_control
    # [修改说明] 新版直接用字典表示 gazebo / ros2_control 元素，不再使用中间 dataclass，
    #           使 JSON/pyacro 与最终 XML 结构更贴近。
    gazebo: List[Dict[str, Any]] = field(default_factory=list)
    ros2_control: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================
# XML 构建器
# ============================================================


class URDFBuilder:
    """将 Robot 数据模型序列化为标准 URDF XML"""

    def __init__(self, robot: Robot):
        self.robot = robot
        try:
            import xml.etree.ElementTree as ET

            self.ET = ET
        except ImportError:
            raise RuntimeError("xml.etree.ElementTree 是 Python 标准库，不应缺失")
        self.root = self.ET.Element("robot", name=robot.name)

    # ---------- 辅助方法 ----------

    def _sub(self, parent, tag, text=None, **attrib):
        """创建子元素"""
        elem = self.ET.SubElement(parent, tag, **attrib)
        if text is not None:
            elem.text = text
        return elem

    def _origin(self, parent, origin: Origin):
        """添加 <origin>

        [修改说明] 2026-07-26: 只有显式提供了 rpy 时才输出 rpy 属性，
                   与 xacro 的 origin 输出习惯保持一致。
        """
        attrs = {"xyz": " ".join(map(str, origin.xyz))}
        if origin.has_rpy:
            attrs["rpy"] = " ".join(map(str, origin.rpy))
        self._sub(parent, "origin", **attrs)

    def _geometry(self, parent, geo: Geometry):
        """添加 <geometry> 及子形状"""
        g = self._sub(parent, "geometry")
        if geo.type == "box":
            size = geo.size if geo.size is not None else []
            self._sub(g, "box", size=" ".join(map(str, size)))
        elif geo.type == "cylinder":
            self._sub(g, "cylinder", radius=str(geo.radius), length=str(geo.length))
        elif geo.type == "sphere":
            self._sub(g, "sphere", radius=str(geo.radius))
        elif geo.type == "mesh":
            attrs = {"filename": geo.filename}
            if geo.scale:
                attrs["scale"] = " ".join(map(str, geo.scale))
            self._sub(g, "mesh", **attrs)
        else:
            raise ValueError(f"未知几何类型: {geo.type}")

    def _material(self, parent, mat: Union[str, Material]):
        """添加 <material>"""
        if isinstance(mat, str):
            # 引用全局材质
            self._sub(parent, "material", name=mat)
        else:
            m = self._sub(parent, "material", name=mat.name)
            if mat.color:
                self._sub(m, "color", rgba=" ".join(map(str, mat.color)))
            if mat.texture:
                self._sub(m, "texture", filename=mat.texture)

    # ---------- 主要元素 ----------

    def _build_link(self, link: Link):
        """构建 <link>"""
        link_elem = self._sub(self.root, "link", name=link.name)

        if link.visual:
            v = self._sub(link_elem, "visual")
            self._origin(v, link.visual.origin)
            self._geometry(v, link.visual.geometry)
            if link.visual.material:
                self._material(v, link.visual.material)

        if link.collision:
            c = self._sub(link_elem, "collision")
            self._origin(c, link.collision.origin)
            self._geometry(c, link.collision.geometry)
            if link.collision.material:
                self._material(c, link.collision.material)

        if link.inertial:
            i = self._sub(link_elem, "inertial")
            # [修改说明] 2026-07-26: 与 xacro 保持一致，<inertial> 中的 <origin>
            #           只在有非零偏移时输出；默认的 xyz="0 0 0" rpy="0 0 0" 省略。
            if link.inertial.origin.xyz != [0.0, 0.0, 0.0]:
                self._origin(i, link.inertial.origin)
            self._sub(i, "mass", value=str(link.inertial.mass))
            iner = link.inertial.inertia
            self._sub(
                i,
                "inertia",
                ixx=str(iner[0]),
                ixy=str(iner[1]),
                ixz=str(iner[2]),
                iyy=str(iner[3]),
                iyz=str(iner[4]),
                izz=str(iner[5]),
            )

    def _build_joint(self, joint: Joint):
        """构建 <joint>"""
        j = self._sub(self.root, "joint", name=joint.name, type=joint.type)
        self._sub(j, "parent", link=joint.parent)
        self._sub(j, "child", link=joint.child)
        self._origin(j, joint.origin)

        if joint.axis:
            self._sub(j, "axis", xyz=" ".join(map(str, joint.axis)))

        if joint.limits:
            self._sub(
                j,
                "limit",
                lower=str(joint.limits.lower),
                upper=str(joint.limits.upper),
                effort=str(joint.limits.effort),
                velocity=str(joint.limits.velocity),
            )

        if joint.dynamics:
            attrs = {}
            if joint.dynamics.damping is not None:
                attrs["damping"] = str(joint.dynamics.damping)
            if joint.dynamics.friction is not None:
                attrs["friction"] = str(joint.dynamics.friction)
            if attrs:
                self._sub(j, "dynamics", **attrs)

        if joint.mimic:
            attrs = {"joint": joint.mimic.joint}
            if joint.mimic.multiplier is not None:
                attrs["multiplier"] = str(joint.mimic.multiplier)
            if joint.mimic.offset is not None:
                attrs["offset"] = str(joint.mimic.offset)
            self._sub(j, "mimic", **attrs)

        if joint.safety_controller:
            attrs = {}
            sc = joint.safety_controller
            if sc.soft_lower_limit is not None:
                attrs["soft_lower_limit"] = str(sc.soft_lower_limit)
            if sc.soft_upper_limit is not None:
                attrs["soft_upper_limit"] = str(sc.soft_upper_limit)
            if sc.k_position is not None:
                attrs["k_position"] = str(sc.k_position)
            if sc.k_velocity is not None:
                attrs["k_velocity"] = str(sc.k_velocity)
            if attrs:
                self._sub(j, "safety_controller", **attrs)

    def _build_transmission(self, trans: Transmission):
        """构建 <transmission> (ROS Control)"""
        t = self._sub(self.root, "transmission", name=trans.name)
        self._sub(t, "type", text=trans.type)
        j = self._sub(t, "joint", name=trans.joint)
        self._sub(j, "hardwareInterface", text="hardware_interface/EffortJointInterface")
        a = self._sub(t, "actuator", name=trans.actuator)
        self._sub(a, "hardwareInterface", text="hardware_interface/EffortJointInterface")
        if trans.mechanical_reduction is not None:
            self._sub(a, "mechanicalReduction", text=str(trans.mechanical_reduction))

    # ---------- Gazebo / ROS2 Control ----------

    def _xml_value(self, value: Any) -> str:
        """将 Python 值转换为 XML 文本"""
        if isinstance(value, (list, tuple)):
            return " ".join(map(str, value))
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _build_xml_from_dict(self, parent, data: Dict[str, Any]):
        """递归将字典转为 XML 子元素，保持键与标签一一对应。

        [新增约定]
        - 键以 "@" 开头：转为父元素的 XML 属性，如 {"@name": "x"} -> name="x";
        - 键为 "#text"：设为元素文本内容，如 {"#text": "foo"} -> <tag>foo</tag>;
        - 其他键：生成 XML 子元素。
        该约定使 JSON/pyacro 能精确表达 <sensor name="..." type="..."> 这类带属性标签。
        """
        for tag, content in data.items():
            if tag.startswith("@"):
                parent.set(tag[1:], self._xml_value(content))
            elif tag == "#text":
                parent.text = self._xml_value(content)
            else:
                self._build_xml_content(parent, tag, content)

    def _build_xml_content(self, parent, tag: str, content: Any):
        """递归生成单个 XML 元素/文本

        标量列表（如 [0,0,1]）转为空格分隔文本，生成单个标签；
        dict 列表则生成多个同名子元素。
        """
        if content is None:
            self._sub(parent, tag)
        elif isinstance(content, dict):
            sub = self._sub(parent, tag)
            self._build_xml_from_dict(sub, content)
        elif isinstance(content, (list, tuple)):
            if not content or all(not isinstance(item, dict) for item in content):
                self._sub(parent, tag, text=self._xml_value(content))
            else:
                for item in content:
                    self._build_xml_content(parent, tag, item)
        else:
            self._sub(parent, tag, text=self._xml_value(content))

    def _build_ros2_control(self, rc: Dict[str, Any]):
        """构建 <ros2_control> 元素。

        [说明] 采用半结构化转换：
        - "name" / "type" 作为 <ros2_control> 的属性；
        - "hardware" 直接递归生成 XML；
        - "joints" 列表特殊处理为 <joint name="..."> 子元素，
          其中每个 joint 的 "command_interfaces" / "state_interfaces" 也被特殊处理，
          使 pyacro 可以用 Pythonic 的字典表达 xacro 中的关节接口。
        """
        attrs = {k: self._xml_value(v) for k, v in rc.items() if k in ("name", "type")}
        root = self._sub(self.root, "ros2_control", **attrs)

        # <hardware> 递归生成
        if "hardware" in rc:
            hw = self._sub(root, "hardware")
            self._build_xml_from_dict(hw, rc["hardware"])

        # <joint> 列表：把 name 提为属性，其余递归
        for joint in rc.get("joints", []):
            j_attrs = {"name": joint["name"]}
            j = self._sub(root, "joint", **j_attrs)
            for ci in joint.get("command_interfaces", []):
                ci_elem = self._sub(j, "command_interface", name=ci["name"])
                for k, v in ci.get("params", {}).items():
                    self._sub(ci_elem, "param", text=self._xml_value(v), name=k)
            for si in joint.get("state_interfaces", []):
                if isinstance(si, str):
                    self._sub(j, "state_interface", name=si)
                else:
                    si_elem = self._sub(j, "state_interface", name=si["name"])
                    for k, v in si.get("params", {}).items():
                        self._sub(si_elem, "param", text=self._xml_value(v), name=k)

    def _build_gazebo(self, gz: Dict[str, Any]):
        """构建 <gazebo> 元素。

        [说明] 新版采用通用递归：
        - "reference" 作为 <gazebo> 的属性；
        - 其余键全部递归生成 XML 子元素，子元素中 "@" 开头键表示属性，
          "#text" 表示文本内容。
        这样 pyacro 可以直接用与 xacro 一一对应的嵌套字典描述传感器、插件等。
        """
        attrs = {}
        if "reference" in gz:
            attrs["reference"] = gz["reference"]
        g = self._sub(self.root, "gazebo", **attrs)
        for tag, content in gz.items():
            if tag == "reference":
                continue
            self._build_xml_content(g, tag, content)

    # ---------- 组装 & 输出 ----------

    def build(self, pretty: bool = True) -> str:
        """组装完整 URDF XML 字符串"""
        # 1. 全局材质
        for mat in self.robot.materials:
            self._material(self.root, mat)

        # 2. Links
        for link in self.robot.links:
            self._build_link(link)

        # 3. Joints
        for joint in self.robot.joints:
            self._build_joint(joint)

        # 4. Transmissions (旧版 ros_control 兼容)
        for trans in self.robot.transmissions:
            self._build_transmission(trans)

        # 5. ros2_control
        for rc in self.robot.ros2_control:
            self._build_ros2_control(rc)

        # 6. Gazebo
        for gz in self.robot.gazebo:
            self._build_gazebo(gz)

        if pretty:
            self._indent(self.root)

        return '<?xml version="1.0"?>\n' + self.ET.tostring(self.root, encoding="unicode")

    def _indent(self, elem, level=0):
        """美化 XML 缩进 (兼容 Python 3.9+ 无 indent() 的情况)"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent(child, level + 1)
            last_child = elem[-1]
            if not last_child.tail or not last_child.tail.strip():
                last_child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


# ============================================================
# JSON 加载 & 验证
# ============================================================


class URDFLoader:
    """从 JSON 字典/文件加载为 Robot 数据模型"""

    REQUIRED_LINK_KEYS = {"name"}
    REQUIRED_JOINT_KEYS = {"name", "type", "parent", "child"}
    JOINT_TYPES = {"revolute", "continuous", "prismatic", "fixed", "floating", "planar"}

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.errors: List[str] = []

    def validate(self) -> bool:
        """基础结构验证，返回是否通过"""
        self.errors.clear()

        if "name" not in self.data:
            self.errors.append("缺少顶层字段: name (机器人名称)")

        # 验证 links
        links = self.data.get("links", [])
        if not links:
            self.errors.append("links 列表为空，至少需要定义一个 link")
        link_names = set()
        for idx, link_dict in enumerate(links):
            missing = self.REQUIRED_LINK_KEYS - set(link_dict.keys())
            if missing:
                self.errors.append(f"links[{idx}] 缺少必填字段: {missing}")
            if "name" in link_dict:
                if link_dict["name"] in link_names:
                    self.errors.append(f"重复的 link 名称: {link_dict['name']}")
                link_names.add(link_dict["name"])

        # 验证 joints
        joint_names = set()
        for idx, j in enumerate(self.data.get("joints", [])):
            missing = self.REQUIRED_JOINT_KEYS - set(j.keys())
            if missing:
                self.errors.append(f"joints[{idx}] 缺少必填字段: {missing}")
            if j.get("type") not in self.JOINT_TYPES:
                self.errors.append(f"joint '{j.get('name', '?')}' 类型无效: {j.get('type')}，应为 {self.JOINT_TYPES}")
            if j.get("parent") not in link_names:
                j_name = j.get("name", "?")
                self.errors.append(f"joint '{j_name}' 的 parent '{j.get('parent')}' 未定义")
            if j.get("child") not in link_names:
                j_name = j.get("name", "?")
                self.errors.append(f"joint '{j_name}' 的 child '{j.get('child')}' 未定义")
            if "name" in j:
                joint_names.add(j["name"])

        # 检查 root link (不被任何 joint 作为 child 的 link)
        child_links = {j.get("child") for j in self.data.get("joints", [])}
        roots = link_names - child_links
        if len(roots) == 0:
            self.errors.append("未找到 root link (所有 link 都被作为 child 引用)")
        elif len(roots) > 1:
            self.errors.append(f"发现多个 root link: {roots} (URDF 要求单根树)")

        # 验证 gazebo 块
        # [修改说明] 新版不再维护插件/传感器注册表，只做基础引用校验：
        #           - reference 必须指向已定义的 link；
        #           - sensor/plugin 若使用通用 "@name" 属性则检查其存在性。
        for idx, g in enumerate(self.data.get("gazebo", [])):
            ref = g.get("reference")
            if ref is not None and ref not in link_names:
                self.errors.append(f"gazebo[{idx}] reference '{ref}' 未在 links 中定义")
            sensor = g.get("sensor")
            if sensor and "@name" not in sensor and "name" not in sensor:
                self.errors.append(f"gazebo[{idx}].sensor 缺少 name 属性")
            plugin = g.get("plugin")
            if plugin:
                has_type = "@type" in plugin or "type" in plugin
                has_filename = "@filename" in plugin or "filename" in plugin
                has_name = "@name" in plugin or "name" in plugin
                if not has_type and not (has_filename and has_name):
                    self.errors.append(f"gazebo[{idx}].plugin 必须指定 type 或同时指定 filename+name")

        # 验证 ros2_control
        for idx, rc in enumerate(self.data.get("ros2_control", [])):
            if "name" not in rc:
                self.errors.append(f"ros2_control[{idx}] 缺少 name")
            if "type" not in rc:
                self.errors.append(f"ros2_control[{idx}] 缺少 type")
            if "hardware" not in rc:
                self.errors.append(f"ros2_control[{idx}] 缺少 hardware")
            elif "plugin" not in rc.get("hardware", {}):
                self.errors.append(f"ros2_control[{idx}].hardware 缺少 plugin")
            for jdx, j in enumerate(rc.get("joints", [])):
                if "name" not in j:
                    self.errors.append(f"ros2_control[{idx}].joints[{jdx}] 缺少 name")
                elif j["name"] not in joint_names:
                    j_name = j["name"]
                    self.errors.append(f"ros2_control[{idx}].joints[{jdx}] 引用未定义关节 '{j_name}'")

        return len(self.errors) == 0

    def load(self) -> Robot:
        """加载为 Robot 对象"""
        d = self.data
        return Robot(
            name=d["name"],
            links=[Link.from_dict(link_data) for link_data in d.get("links", [])],
            joints=[Joint.from_dict(j) for j in d.get("joints", [])],
            materials=[Material.from_dict(m) for m in d.get("materials", [])],
            transmissions=[Transmission.from_dict(t) for t in d.get("transmissions", [])],
            # [修改说明] 新版不再使用 Gazebo/Ros2Control dataclass，直接保留字典，
            #           由 URDFBuilder 通用/半结构化转换生成 XML。
            gazebo=d.get("gazebo", []),
            ros2_control=d.get("ros2_control", []),
        )


# ============================================================
# 主转换函数 & CLI
# ============================================================


def convert(
    json_input: Union[str, Path, Dict],
    output: Optional[Union[str, Path]] = None,
    validate: bool = True,
    pretty: bool = True,
) -> str:
    """
    JSON → URDF 主转换入口

    Args:
        json_input: JSON 文件路径、Path 对象或字典
        output: 输出 URDF 文件路径 (None 则仅返回字符串)
        validate: 是否进行结构验证
        pretty: 是否格式化缩进

    Returns:
        URDF XML 字符串
    """
    # 加载数据
    if isinstance(json_input, (str, Path)):
        path = Path(json_input)
        if not path.exists():
            raise FileNotFoundError(f"JSON 文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json_input

    # 验证
    loader = URDFLoader(data)
    if validate:
        if not loader.validate():
            raise ValueError("JSON 验证失败:\n" + "\n".join(f"  - {e}" for e in loader.errors))

    # 构建
    robot = loader.load()
    builder = URDFBuilder(robot)
    urdf = builder.build(pretty=pretty)

    # 输出
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(urdf, encoding="utf-8")
        print(f"[✓] URDF 已保存: {out_path.absolute()}")

    return urdf


def main():
    parser = argparse.ArgumentParser(
        description="JSON → URDF XML 转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s robot.json -o robot.urdf
  %(prog)s robot.json -o robot.urdf --no-validate
  %(prog)s robot.json                    # 仅输出到 stdout
        """,
    )
    parser.add_argument("input", help="输入 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出 URDF 文件路径")
    parser.add_argument("--no-validate", action="store_true", help="跳过结构验证 (不推荐)")
    parser.add_argument("--no-pretty", action="store_true", help="输出紧凑 XML (无缩进)")
    args = parser.parse_args()

    try:
        urdf = convert(
            json_input=args.input,
            output=args.output,
            validate=not args.no_validate,
            pretty=not args.no_pretty,
        )
        if not args.output:
            print(urdf)
    except Exception as e:
        print(f"[✗] 错误: {e}", file=sys.stderr)
        sys.exit(1)


# ============================================================
# JSON Schema 说明 (文档)
# ============================================================
SCHEMA_DOC = """
================================================================================
JSON 格式规范
================================================================================

顶层结构:
{
  "name": "robot_name",           // 必填: 机器人名称
  "materials": [...],             // 可选: 全局材质定义
  "links": [...],                 // 必填: 连杆列表
  "joints": [...],                // 可选: 关节列表
  "transmissions": [...],         // 可选: 旧版传动机构 (兼容 ros_control)
  "gazebo": [...],                // 可选: Gazebo 仿真属性/插件
  "ros2_control": [...]           // 可选: 现代 ros2_control 标签
}

--- materials ---
{
  "name": "blue",
  "color": [0.0, 0.0, 0.8, 1.0],   // rgba, 范围 0~1
  "texture": "path/to/texture.png"   // 可选
}

--- links ---
{
  "name": "base_link",
  "visual": {
    "origin": {"xyz": [0,0,0], "rpy": [0,0,0]},
    "geometry": {"type": "box", "size": [1,1,1]},
    "material": "blue"               // 可填材质名(引用)或内联材质对象
  },
  "collision": { ... },              // 同 visual 结构，但无 material
  "inertial": {
    "mass": 1.0,
    "origin": {"xyz": [0,0,0], "rpy": [0,0,0]},
    "inertia": [ixx, ixy, ixz, iyy, iyz, izz]
  }
}

geometry 类型:
  - box:      {"type": "box", "size": [x,y,z]}
  - cylinder: {"type": "cylinder", "radius": r, "length": l}
  - sphere:   {"type": "sphere", "radius": r}
  - mesh:     {"type": "mesh", "filename": "path.dae", "scale": [1,1,1]}

--- joints ---
{
  "name": "joint1",
  // type: revolute | continuous | prismatic | fixed | floating | planar
  "type": "revolute",
  "parent": "base_link",
  "child": "link1",
  "origin": {"xyz": [0,0,0], "rpy": [0,0,0]},
  // axis: 旋转/平移轴 (continuous/revolute/prismatic 必填)
  "axis": [0, 0, 1],
  "limits": {"lower": -3.14, "upper": 3.14, "effort": 10, "velocity": 1},
  "dynamics": {"damping": 0.1, "friction": 0.0},
  "mimic": {"joint": "other_joint", "multiplier": 1.0, "offset": 0.0},
  "safety_controller": {
    "soft_lower_limit": -3.0,
    "soft_upper_limit": 3.0,
    "k_position": 100,
    "k_velocity": 10
  }
}

--- transmissions (旧版 ros_control 兼容) ---
{
  "name": "trans1",
  "type": "transmission_interface/SimpleTransmission",
  "joint": "joint1",
  "actuator": "motor1",
  "mechanical_reduction": 1.0
}

--- gazebo ---

通用约定：
  - "reference" 会被提取为 <gazebo reference="..."> 的属性；
  - 子元素中键以 "@" 开头表示 XML 属性，"#text" 表示文本内容；
  - 其余键递归生成 XML 子元素。

// 1) Harmonic 激光雷达传感器 (对应 gazebo_sensor_plugin.xacro)
{
  "reference": "laser_link",
  "sensor": {
    "@name": "laserscan",
    "@type": "gpu_lidar",
    "always_on": true,
    "visualize": true,
    "update_rate": 5,
    "pose": "0 0 0 0 0 0",
    "topic": "scan",
    "frame_id": "laser_link",
    "gz_frame_id": "laser_link",
    "lidar": {
      "scan": {
        "horizontal": {
          "samples": 360,
          "resolution": 1.0,
          "min_angle": 0.0,
          "max_angle": 6.28
        }
      },
      "range": {"min": 0.12, "max": 8.0, "resolution": 0.015},
      "noise": {"type": "gaussian", "mean": 0.0, "stddev": 0.01}
    }
  }
}

// 2) Harmonic 原生差速插件 (对应 gazebo_control_plugin.xacro)
{
  "plugin": {
    "@filename": "gz-sim-diff-drive-system",
    "@name": "gz::sim::systems::DiffDrive",
    "topic": "cmd_vel",
    "odom_topic": "odom",
    "tf_topic": "/tf",
    "left_joint": "left_wheel_joint",
    "right_joint": "right_wheel_joint",
    "wheel_separation": 0.2,
    "wheel_radius": 0.032,
    "frame_id": "odom",
    "child_frame_id": "base_footprint",
    "odom_publish_frequency": 30
  }
}

// 3) gz_ros2_control 插件 (配合 ros2_control 使用)
{
  "plugin": {
    "@filename": "gz_ros2_control-system",
    "@name": "gz_ros2_control::GazeboSimROS2ControlPlugin",
    "parameters": "$(find fishbot_description)/config/ros2_controller/fishbot_ros2_controller.yaml"
  }
}

--- ros2_control ---
{
  "name": "FishBotGazeboSystem",
  "type": "system",
  "hardware": {
    "plugin": "gz_ros2_control/GazeboSimSystem"
  },
  "joints": [
    {
      "name": "left_wheel_joint",
      "command_interfaces": [
        {"name": "velocity", "params": {"min": -1, "max": 1}},
        {"name": "effort", "params": {"min": -0.1, "max": 0.1}}
      ],
      "state_interfaces": ["position", "velocity", "effort"]
    }
  ]
}

[注意] gazebo 原生差速插件与 ros2_control 会争夺轮子关节，
      二者不可同时启用。切换方式见 fishbot.urdf.xacro 与 launch 文件注释。

================================================================================
"""


if __name__ == "__main__":
    main()
