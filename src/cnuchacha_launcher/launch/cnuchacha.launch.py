from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit


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
                [FindPackageShare("cnuchacha_launcher"), "urdf", "cnuchacha.urdf.xacro"]
            ),
        ]
    )
    # Create a "robot_description" parameter with the generated robot description (xacro)
    robot_description = {"robot_description": robot_description_content}

    # 2. Set the robot_state_publisher_node ----------------------------------------------------------------
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",                    # output log to screen ('screen', 'log' or 'both')
        parameters=[
            robot_description,              # pass URDF descriptions as parameter
            {'use_sim_time': True}          # use simulation time
        ],
    )

    # 3. Set RVIZ node -----------------------------------------------------------------------------------
    # Get the path to the RVIZ config file
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("cnuchacha_description"), "rviz", "cnuchacha.rviz"]
    )
    # Create a RVIZ node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",                    # output log to screen ('screen', 'log' or 'both')
        arguments=[
            "-d", rviz_config_file          # command line arguments: rviz config file path
        ],
    )

    # 4. Set gazebo -----------------------------------------------------------------------------------------
    # Create a Gazebo node using IncludeLaunchDescription
    #    IncludeLaunchDescription: indlude another launch file in the current launch file
    gazebo_node = IncludeLaunchDescription(
        # Specify the Python launch file to include
        PythonLaunchDescriptionSource([
            # Construct the path to gazebo.launch.py
            PathJoinSubstitution([
                # Get the path to gazebo_ros package
                FindPackageShare("gazebo_ros"),
                # Navigate to the launch directory
                "launch",
                # Specify the launch file name
                "gazebo.launch.py"])
        ]),
        # Set launch arguments - disable verbose output
        launch_arguments={"verbose": "false"}.items(),
    )

    # 5. Spawn a robot in gazebo --------------------------------------------------------------------------
    robot_spawner = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "robot_description",          # topic name
            "-entity", "cnuchacha_system_position"     # entity name
        ],
        output="screen",                            # output log to screen ('screen', 'log' or 'both')
        parameters=[
            {'use_sim_time': True}                  # use simulation time
        ],
    )

    # 6. Spawn joint_state_broadcater in controller_manager  --------------------------------------------------------------------
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",                      # controller name
            "--controller-manager", "/controller_manager"   # controller manager name
        ],
        parameters=[
            {'use_sim_time': True}                          # use simulation time
        ],
    )

    # 7. Spawn forward position controller in controller_manager ----------------------------------------------------------------
    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "forward_position_controller",                  # controller name
            "--controller-manager", "/controller_manager"   # controller manager name
        ],
        parameters=[
            {'use_sim_time': True}                          # use simulation time
        ],
    )

    # Ensure controllers start after the robot is spawned
    spawn_controllers_after_gazebo = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_spawner,
            on_exit=[joint_state_broadcaster_spawner, robot_controller_spawner],
        )
    )

    # 8. Set all nodes --------------------------------------------------------------------------------------
    nodes = [
        robot_state_publisher_node,
        rviz_node,
        gazebo_node,
        robot_spawner,
        spawn_controllers_after_gazebo,
    ]

    return LaunchDescription(nodes)
