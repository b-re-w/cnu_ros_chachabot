#!/usr/bin/env python3

import random, math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class CnuChachaController(Node):
    def __init__(self):
        super().__init__('cnuchacha_controller')

        # Create Publisher
        self.publisher_ = self.create_publisher(
            msg_type=Float64MultiArray,
            topic='/forward_position_controller/commands',
            qos_profile=10
        )
        self.get_logger().info('CNUCHACHA Controller has been started')

        # Create timer for periodic publishing
        self.timer = self.create_timer(0.1, self.update_joint_states)

        self.command = Float64MultiArray()

        # joint1, joint2 설정
        self.initial_positions = [0.0, 0.0]
        self.current_positions = self.initial_positions.copy()
        self.target_positions = [random.uniform(-math.pi, math.pi) for _ in self.initial_positions]
        self.mission_completed = False

        # 넙죽이 회전 설정
        self.nupjuki_pos = 0.0
        self.nupjuki_target = 1.57  # 90도
        self.nupjuki_direction = 1  # 1: 오른쪽, -1: 왼쪽
        self.nupjuki_speed = 0.2   # 회전 속도


    def update_joint_states(self):
        # joint1, joint2 로직
        if not self.mission_completed:
            for i in range(len(self.current_positions)):
                step = (self.target_positions[i] - self.current_positions[i]) * 0.1
                self.current_positions[i] += step if abs(step) > 0.001 else 0

                if abs(self.current_positions[i] - self.target_positions[i]) < 0.05:
                    self.mission_completed = True
                    self.get_logger().info('Target reached, moving back to initial positions')
        else:
            self.current_positions = self.initial_positions.copy()
            self.target_positions = [random.uniform(-math.pi, math.pi) for _ in self.initial_positions]
            self.mission_completed = False
            self.get_logger().info('Initial positions reset, new target set')

        # 넙죽이 회전 로직
        self.nupjuki_pos += self.nupjuki_speed * self.nupjuki_direction

        if self.nupjuki_pos >= self.nupjuki_target:
            self.nupjuki_pos = self.nupjuki_target
            self.nupjuki_direction = -1
            self.get_logger().info('Nupjuki: 오른쪽 끝, 반대 방향으로')
        elif self.nupjuki_pos <= -self.nupjuki_target:
            self.nupjuki_pos = -self.nupjuki_target
            self.nupjuki_direction = 1
            self.get_logger().info('Nupjuki: 왼쪽 끝, 반대 방향으로')

        # joint1, joint2, nupjuki 합쳐서 publish
        self.command.data = self.current_positions + [self.nupjuki_pos]
        self.publisher_.publish(self.command)
        self.get_logger().info(f'Publishing : {self.command.data}')


def main(args=None):
    rclpy.init(args=args)
    command_node = CnuChachaController()
    rclpy.spin(command_node)
    command_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
