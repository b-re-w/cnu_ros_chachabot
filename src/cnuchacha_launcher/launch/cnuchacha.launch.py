from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 1. Set the robot description (xacro) ----------------------------------------------------------------
    robot_description_content = ParameterValue(
        Command(
            [
                PathJoinSubstitution([FindExecutable(name="xacro")]),
                " ",
                PathJoinSubstitution(
                    [FindPackageShare("cnuchacha_launcher"), "urdf", "cnuchacha.urdf.xacro"]
                ),
            ]
        ),
        value_type=str
    )
    robot_description = {"robot_description": robot_description_content}

    # 2. Set the robot_state_publisher_node ----------------------------------------------------------------
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            robot_description,
            {'use_sim_time': True}
        ],
    )

    # 3. Set RVIZ node -----------------------------------------------------------------------------------
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("cnuchacha_description"), "rviz", "cnuchacha.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
    )

    # 4. Set gazebo -----------------------------------------------------------------------------------------
    gazebo_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("gazebo_ros"),
                "launch",
                "gazebo.launch.py"
            ])
        ]),
        launch_arguments={"verbose": "false"}.items(),
    )

    # 5. Spawn a robot in gazebo --------------------------------------------------------------------------
    robot_spawner = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "robot_description",
            "-entity", "cnuchacha_system_position"
        ],
        output="screen",
        parameters=[
            {'use_sim_time': True}
        ],
    )

    # 6. Spawn joint_state_broadcaster in controller_manager  -----------------------------------------------
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager"
        ],
        parameters=[
            {'use_sim_time': True}
        ],
    )

    # 7. Spawn forward position controller in controller_manager --------------------------------------------
    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "forward_position_controller",
            "--controller-manager", "/controller_manager"
        ],
        parameters=[
            {'use_sim_time': True}
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
