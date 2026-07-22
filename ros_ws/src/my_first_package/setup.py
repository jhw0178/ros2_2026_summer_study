from setuptools import find_packages, setup
from glob import glob # glob 모듈을 사용하기 위해 추가
import os # os 모듈을 사용하기 위해 추가

package_name = 'my_first_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join('launch', '*.launch.py'))), #추가된 부분
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
            "simple_pub = my_first_package.simple_pub:main",
            "simple1_pub = my_first_package.simple1_pub:main",
            "message_pub = my_first_package.message_pub:main",
            "message1_pub = my_first_package.message1_pub:main",
            "message_sub = my_first_package.message_sub:main",
            "header_pub = my_first_package.header_pub:main",
            "my_turtle = my_first_package.my_turtle:main",
            "my_turtle1 = my_first_package.my_turtle1:main",
        ],
    },
)
