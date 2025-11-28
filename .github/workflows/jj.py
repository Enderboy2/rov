import rclpy
from rclpy.node import Node
from sensor_msgs import Joy
import pygame

pygame.init()
pygame.joystick.init()
joy_c = pygame.joystick.get_count()
if joy_c == 0:
    print("no joystick")
    quit()
joystick = pygame.joystick.Joystick(0)
joystick.init()

class Joystick(Node):
    def __init__(self):
        super().__init__('joystick_node')
        self.axis_values = [0,0]
        self.threshold = 0.5
        self.states = [0]*12
        self.motion = "N"
        self.speed = 0
        self.pub = self.create_publisher(String, 'joystick_data', 10)
        self.timer = self.create_timer(0.1, self.update)

    def update(self):
        pygame.event.pump()
        self.axis_values[0] = joystick.get_axis(0)
        self.axis_values[1] = joystick.get_axis(1)

        if self.axis_values[1] < -self.threshold:
            self.motion = "F"
        elif self.axis_values[1] > self.threshold:
            self.motion = "B"
        elif self.axis_values[0] < -self.threshold:
            self.motion = "L"
        elif self.axis_values[0] > self.threshold:
            self.motion = "R"
        else:
            self.motion = "N"

        self.speed = int((joystick.get_axis(3) * -1 + 1) * 50)

        for e in pygame.event.get():
            if e.type == pygame.JOYBUTTONDOWN:
                self.states[e.button] = 1 - self.states[e.button]

        self.message = f"{self.motion}, {self.speed}, {self.states[2]}, {self.states[3]}, {self.states[4]}, {self.states[5]}"

        msg.data = self.message
        self.pub.publish(msg)
        print(self.message)

def main(args=None):
    rclpy.init(args=args)
    joy = Joystick()
    rclpy.spin(joy)
    joy.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

