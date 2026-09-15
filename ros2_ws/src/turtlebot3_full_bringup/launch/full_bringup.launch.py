import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from ament_index_python.packages import get_package_share_directory
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Eigenes Package finden
    package_dir = get_package_share_directory(
        "turtlebot3_full_bringup"
    )

    # Pfade zu World, Map, Nav2-Config und RViz
    world_file = os.path.join(
        package_dir,
        "worlds",
        "playground.world"
    )

    map_file = os.path.join(
        package_dir,
        "maps",
        "playground_map_hq.yaml"
    )

    nav2_params = os.path.join(
        package_dir,
        "config",
        "init_nav2_params.yaml"
    )

    rviz_config = os.path.join(
        package_dir,
        "rviz",
        "rviz.rviz"
    )

    # TurtleBot3 Gazebo Package finden
    turtlebot3_gazebo = FindPackageShare(
        "turtlebot3_gazebo"
    ).find("turtlebot3_gazebo")

    # Bestehende TurtleBot3 Launch-Dateien
    robot_state_launch = os.path.join(
        turtlebot3_gazebo,
        "launch",
        "robot_state_publisher.launch.py"
    )

    spawn_robot_launch = os.path.join(
        turtlebot3_gazebo,
        "launch",
        "spawn_turtlebot3.launch.py"
    )

    # Startposition des Roboters
    x_pose = LaunchConfiguration(
        "x_pose",
        default="-2.0"
    )

    y_pose = LaunchConfiguration(
        "y_pose",
        default="-0.5"
    )

    # Robot State Publisher starten
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            robot_state_launch
        )
    )

    # TurtleBot3 in Gazebo einfügen
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            spawn_robot_launch
        ),
        launch_arguments={
            "x_pose": x_pose,
            "y_pose": y_pose
        }.items()
    )

    # Nav2 Package finden
    nav2_bringup_dir = get_package_share_directory(
        "nav2_bringup"
    )

    # Nav2 starten
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup_dir,
                "launch",
                "bringup_launch.py"
            )
        ),
        launch_arguments={
            "map": map_file,
            "params_file": nav2_params,
            "use_sim_time": "true"
        }.items()
    )

    return LaunchDescription([

        # Gazebo mit eigener World starten
        ExecuteProcess(
            cmd=[
                "gazebo",
                "--verbose",
                world_file,
                "-s",
                "libgazebo_ros_factory.so"
            ],
            output="screen"
        ),

        # Roboterzustände veröffentlichen
        robot_state_publisher,

        # TurtleBot3 in Gazebo platzieren
        spawn_robot,

        # Nav2 starten
        nav2_launch,

        # RViz starten
        ExecuteProcess(
            cmd=[
                "rviz2",
                "-d",
                rviz_config
            ],
            output="screen"
        )
    ])