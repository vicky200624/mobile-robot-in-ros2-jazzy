import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    robot_name = 'differential_drive_robot'
    package_name = 'mobile_robot'
    xacro_path = os.path.join(
        get_package_share_directory(package_name),
        'model',
        'robot.xacro'
    )

    # Parse XACRO to URDF
    doc = xacro.process_file(xacro_path)
    robot_description_config = doc.toxml()

    # Gazebo Sim launch (ros_gz_sim)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ]),
        launch_arguments={
            'gz_args': '-r -v 4 empty.sdf'
        }.items()
    )

    # Publish robot description
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_config,
            'use_sim_time': True
        }],
        output='screen'
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', robot_name, '-topic', '/robot_description'],
        output='screen'
    )

    # ROS-GZ bridge parameters (optional)
    bridge_params = os.path.join(
        get_package_share_directory(package_name),
        'parameters',
        'bridge_parameters.yaml'
    )

    ros_gz_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}'],
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity,
        ros_gz_bridge_node
    ])