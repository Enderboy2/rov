import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import ast  # for safely parsing lists from strings

class JoystickListener(Node):
    def __init__(self):
        super().__init__('joystick_listener')
        self.subscription = self.create_subscription(
            String,
            'joystick_data',
            self.listener_callback,
            10)
        self.subscription
        self.get_logger().info('Joystick Listener has started.')

    def listener_callback(self, msg):
        try:
            # Split string into axes and buttons
            axes_str, buttons_str = msg.data.split('Buttons:')
            axes_list = axes_str.replace('Axes:', '').strip()
            buttons_list = buttons_str.strip()

            # Safely convert string representations to Python lists
            axes = ast.literal_eval(axes_list)
            buttons = ast.literal_eval(buttons_list)

            self.get_logger().info(
                f'Received -> Axes: {axes} | Buttons: {buttons}'
            )

            # --- Example Logic Hook ---
            # Use axes[0], axes[1], buttons[0], etc. for robot control

        except Exception as e:
            self.get_logger().error(f'Error parsing data: {e}')

def main(args=None):
    rclpy.init(args=args)
    listener = JoystickListener()
    try:
        rclpy.spin(listener)
    except KeyboardInterrupt:
        pass
    finally:
        listener.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
