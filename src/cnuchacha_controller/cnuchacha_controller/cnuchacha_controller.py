#!/usr/bin/env python3

import random, math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class CnuChachaController(Node):
    def __init__(self):
        super().__init__('cnuchacha_controller')

        # Create Publisher: ------------------------------------------------------------------------------------------------
        # Publishing to /forward_position_controller/commands topic with Float64MultiArray message type
        self.publisher_ = self.create_publisher(
            msg_type=Float64MultiArray,
            topic='/forward_position_controller/commands',
            qos_profile=10
        )
        self.get_logger().info('CNUCHACHA Controller has been started')

        # Create timer for periodic publishing ----------------------------------------------------------------------
        self.timer = self.create_timer(0.1, self.update_joint_states)

        # Set inint states and target state -------------------------------------------------------------------------
        self.command = Float64MultiArray()

        # Initial positions
        self.initial_positions = [0.0, 0.0]
        self.current_positions = self.initial_positions.copy()

        # Target positions
        self.target_positions = [random.uniform(-math.pi, math.pi) for _ in self.initial_positions]

        # Set mission_completed flag
        self.mission_completed = False


    def update_joint_states(self):
        """
        $ ros2 interface proto std_msgs/msg/Float64MultiArray
        "layout:
        dim: []
        data_offset: 0
        data: []
        "
        """
        # ----------------------------------------------------------------------------------------------------
        # Update current positions

        # If moving towards target, increment current positions slightly towards the target
        if not self.mission_completed:
            for i in range(len(self.current_positions)):
                step = (self.target_positions[i] - self.current_positions[i]) * 0.1
                self.current_positions[i] += step if abs(step) > 0.001 else 0

                # Check if the target or initial position is sufficiently reached
                if abs(self.current_positions[i] - self.target_positions[i]) < 0.05:
                    self.mission_completed = True
                    self.get_logger().info('Target reached, moving back to initial positions')
        # Once target is reached or nearly reached, move back to initial positions
        else:
            self.current_positions = self.initial_positions.copy()
            self.target_positions = [random.uniform(-math.pi, math.pi) for _ in self.initial_positions]
            self.mission_completed = False
            self.get_logger().info('Initial positions reset, new target set')
        # ----------------------------------------------------------------------------------------------------

        # Update joint states with current positions
        self.command.data = self.current_positions

        # Publish joint states to /forward_position_controller/commands topic
        self.publisher_.publish(self.command)

        # Log joint states (debug level)
        self.get_logger().info(f'Publishing : {self.command.data}')


def main(args=None):
    rclpy.init(args=args)
    command_node = CnuChachaController()
    rclpy.spin(command_node)
    command_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
