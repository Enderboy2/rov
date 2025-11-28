import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class JoystickListener(Node):
    def __init__(self):
        super().__init__('joystick_listener')
        # Create a subscriber to the topic 'joystick_data'
        self.subscription = self.create_subscription(
            String,
            'joystick_data',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.get_logger().info('Joystick Listener has started.')

    def listener_callback(self, msg):
        try:
            # Your message format is: "Motion, Speed, State2, State3, State4, State5"
            # Example: "F, 50, 0, 1, 0, 0"
            
            # 1. Split the string by comma
            data = msg.data.split(',')
            
            # 2. Clean up whitespace and extract variables
            motion = data[0].strip()
            speed = int(data[1].strip())
            btn_2 = int(data[2].strip())
            btn_3 = int(data[3].strip())
            btn_4 = int(data[4].strip())
            btn_5 = int(data[5].strip())

            # 3. Log the parsed data (This is where you will add motor control logic later)
            self.get_logger().info(
                f'Received -> Motion: {motion} | Speed: {speed} | Buttons: [{btn_2}, {btn_3}, {btn_4}, {btn_5}]'
            )

            # --- Example Logic Hook ---
            # if motion == "F":
            #     move_robot_forward(speed)
            
        except ValueError as e:
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
