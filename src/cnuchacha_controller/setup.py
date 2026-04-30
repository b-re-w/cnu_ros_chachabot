from setuptools import find_packages, setup

package_name = 'cnuchacha_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='etri',
    maintainer_email='etri@todo.todo',
    description='CNUCHACHA robot controller package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cnuchacha_joint_state_publisher = cnuchacha_controller.cnuchacha_joint_state_publisher:main',
            'cnuchacha_controller = cnuchacha_controller.cnuchacha_controller:main',
        ],
    },
)
