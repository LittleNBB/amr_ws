import os
import xacro
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    package_name = 'bot_description'
    
    # 1. 获取路径
    pkg_share = get_package_share_directory(package_name)
    gazebo_ros_share = get_package_share_directory('ros_gz_sim')
    
    # 2. 解析 Xacro
    xacro_file = os.path.join(pkg_share, 'urdf', 'bot_base.xacro')
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # 3. 启动 Gazebo 模拟器 (加载一个空世界)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(), # -r 表示启动即运行
    )

    # 4. 在 Gazebo 中生成机器人实体
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'my_bot', '-string', robot_description_raw],
        output='screen',
    )

    # 5. 【关键】建立桥梁 (Bridge)
    # 让 ROS 2 的 /cmd_vel 控制 Gazebo 里的机器人
    # 让 Gazebo 的 /odom 传回给 ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_entity,
        bridge
    ])
