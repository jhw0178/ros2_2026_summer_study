from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'mini_homework1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jhw0178',
    maintainer_email='jhw0178@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "publisher = mini_homework1.publisher:main",
            "subscriber1 = mini_homework1.subscriber1:main",
            "subscriber2 = mini_homework1.subscriber2:main",
            "time_publisher = mini_homework1.time_publisher:main",
            "time_and_topic1_subscriber = mini_homework1.time_and_topic1_subscriber:main",
        ],
    },
)