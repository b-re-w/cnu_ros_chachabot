#!/usr/bin/env python3

import random
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class CnuChachaJointStatePublisher(Node):
    def __init__(self):
        super().__init__('cnuchacha_joint_state_publisher')

        # Create Publisher: ------------------------------------------------------------------------------------------------
        # Publishing to /joint_states topic with JointState message type
        self.publisher_ = self.create_publisher(
            msg_type=JointState,
            topic='/joint_states',
            qos_profile=10
        )
        self.get_logger().info('CNUCHACHA Joint State Publisher has been started')

        # Create timer for periodic publishing ----------------------------------------------------------------------
        self.timer = self.create_timer(0.1, self.update_joint_states)

        # Set inint states and target state -------------------------------------------------------------------------
        self.joint_states = JointState()

        # initial position
        self.initial_positions = [0.0, 0.0]  # Initial positions
        self.current_positions = self.initial_positions.copy()  # Current positions

        # target position
        self.target_positions = [random.uniform(-1.57, 1.57) for _ in self.initial_positions]  # Random target positions

        # Set mission_completed flag
        self.mission_completed = False


    def update_joint_states(self):
        """
        $ ros2 interface show sensor_msgs/msg/JointState
        "header:
        stamp:
            sec: 0
            nanosec: 0
        name: []
        position: []
        velocity: []
        effort: []
        "
        """
        # Set joint states ------------------------------------------------------------------------------------------------
        self.joint_states.header.stamp = self.get_clock().now().to_msg()
        self.joint_states.name = ['joint1', 'joint2']

        # If moving towards target, increment current positions slightly towards the target
        if not self.mission_completed:
            for i in range(len(self.current_positions)):
                step = (self.target_positions[i] - self.current_positions[i]) * 0.1
                self.current_positions[i] += step if abs(step) > 0.001 else 0

                # Check if the target position is sufficiently reached
                if abs(self.current_positions[i] - self.target_positions[i]) < 0.05:
                    self.mission_completed = True
                    self.get_logger().info('Target reached, moving back to initial positions')

        # Once target is reached, immediately return to initial positions
        else:
            self.current_positions = self.initial_positions.copy()  # Immediate return to initial positions
            self.mission_completed = False
            self.target_positions = [random.uniform(-1.57, 1.57) for _ in self.initial_positions]
            self.get_logger().info('Initial positions reset, new target set')

        # Update joint states with current positions
        self.joint_states.position = self.current_positions

        # Publish joint states to /joint_states topic
        self.publisher_.publish(self.joint_states)

        # Log joint states (debug level)
        self.get_logger().debug(
            f'Published joint states: {[f"{name}: {pos:.2f}" for name, pos in zip(self.joint_states.name, self.joint_states.position)]}'
        )

def main(args=None):
    rclpy.init(args=args)
    joint_state_publisher_node = CnuChachaJointStatePublisher()
    rclpy.spin(joint_state_publisher_node)
    joint_state_publisher_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()