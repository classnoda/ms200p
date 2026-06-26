import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ms200p'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='noda',
    maintainer_email='classnoda@gmail.com',
    description='ROS2 driver for MS200P LiDAR',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ms200p_node = ms200p.node:main'
        ],
    },
)
