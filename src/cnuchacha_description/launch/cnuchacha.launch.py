from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 1. Set the robot description (xacro) ----------------------------------------------------------------
    # Create 'command' to generate the robot description (xacro)
    robot_description_content = Command(
        [
            # Get the path to the xacro executable
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            # Add a space between the executable and the file path
            " ",
            # Get the path to the URDF xacro file in the package
            PathJoinSubstitution(
                [FindPackageShare("cnuchacha_description"), "urdf", "cnuchacha_description.urdf.xacro"]
            ),
        ]
    )
    # Create a "robot_description" parameter with the generated robot description (xacro)
    robot_description = {"robot_description": robot_description_content}

    # 2. Set the robot_state_publisher_node ----------------------------------------------------------------
    cnuchacha_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name='cnuchacha_state_publisher',
        output="screen",                    # output log to screen ('screen', 'log' or 'both')
        parameters=[robot_description],     # pass URDF descriptions as parameter
    )

    # 3. Set joint_state_publisher_node ----------------------------------------------------------------
    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name='joint_state_publisher_gui',
        output="screen",                    # output log to screen ('screen', 'log' or 'both')
        parameters=[robot_description],     # pass URDF descriptions as parameter
    )

    # 4. Set RVIZs node -----------------------------------------------------------------------------------
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("cnuchacha_description"), "rviz", "cnuchacha.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",                    # output log to screen ('screen', 'log' or 'both')
        arguments=["-d", rviz_config_file], # command line arguments: rviz config file path
    )

    # 5. Set all nodes --------------------------------------------------------------------------------------
    nodes = [
        cnuchacha_state_publisher_node,
        joint_state_publisher_node,
        rviz_node,
    ]

    return LaunchDescription(nodes)
