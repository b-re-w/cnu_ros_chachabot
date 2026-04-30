cmake_minimum_required(VERSION 3.5)
project(cnuchacha_launcher)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    config
    launch
    urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
