import rclpy
from rclpy.node import Node
from std_msgs.msg import String
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
        self.states=[0]* joystick.get_numbuttons()
        self.pub = self.create_publisher(String, 'joystick_data', 10)
        self.timer = self.create_timer(0.1, self.update)

    def update(self):
        pygame.event.pump()
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]

        for e in pygame.event.get():
            if e.type == pygame.JOYBUTTONDOWN:
                self.states[e.button] = 1 - self.states[e.button]

        msg = String()
        msg.data = f"Axes: {axes}, Buttons: {self.states}"

        self.pub.publish(msg)
        print(msg.data)

def main(args=None):
    rclpy.init(args=args)
    joy = Joystick()
    rclpy.spin(joy)
    joy.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
