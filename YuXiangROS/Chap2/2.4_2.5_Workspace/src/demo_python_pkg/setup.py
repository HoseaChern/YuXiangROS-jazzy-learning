from setuptools import find_packages, setup

package_name = "demo_python_pkg"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="changli",
    maintainer_email="chx_050913@163.com",
    description="TODO: Package description",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "python_node = demo_python_pkg.python_node:main",
            "person_node = demo_python_pkg.person_node:main",
            "writer_node = demo_python_pkg.writer_node:main",
            "learn_thread = demo_python_pkg.learn_thread:main",
        ],
    },  # 在这里添加更多节点
)
