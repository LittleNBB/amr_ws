import os
import xacro
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    package_name = 'bot_description'
    xacro_name = "bot_base.xacro"
    
    # 1. 路径获取
    pkg_share = FindPackageShare(package=package_name).find(package_name)
    xacro_path = os.path.join(pkg_share, 'Xacro', xacro_name)

    # # 2. 读取 URDF 文件内容 (Humble 标准做法)
    # with open(urdf_model_path, 'r') as infp:
    #     robot_description_content = infp.read()

    # 2.使用xacro库处理xacro文件
    
    robot_description_config = xacro.process_file(xacro_path)
    robot_description_content = robot_description_config.toxml()



    # 3. 配置节点
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content, 'publish_frequency': 30.0}]
        )

    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'robot_description': robot_description_content}],
        output = "screen"
        )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node,
        rviz2_node
    ])