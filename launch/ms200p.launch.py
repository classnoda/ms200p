from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ms200p',
            executable='ms200p_node',
            name='ms200p_node',
            output='screen',
            parameters=[{
                'port': '/dev/ttyACM0',
                'baudrate': 230400,
                'frame_id': 'laser',
                'topic': 'scan',
                'range_min': 0.03,
                'range_max': 12.0,
                'angle_resolution_deg': 1.0,
                'inverted': False,
                'publish_tf': True,
                'parent_frame': 'base_link',
            }],
        ),
    ])