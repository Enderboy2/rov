import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import ast  # for safely parsing lists from strings
from pymavlink import mavutil
# Mavlink
master = mavutil.mavlink_connection('COM7', baud=115200)
# connect and Arm cube
# Wait for heartbeat (confirm connection)
print("Waiting for CubePilot heartbeat...")
master.wait_heartbeat()
print("Connected to CubePilot!")
# 1 = arm, 0 = disarm
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,      # confirmation
    1,      # ARM
    0, 0, 0, 0, 0, 0
)
def scale_axis(value):
        return int(value * 1000)
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
            # Typical joystick mapping (adjust for your joystick!)
            x  = scale_axis(axes[0] )   # Roll  (-)left (+)right
            y  = scale_axis(axes[1])    # Pitch (-)forward (+)back
            z  = scale_axis(axes[2])     # Throttle
            r  = scale_axis(axes[3])     # Yaw
            for i in range(len(buttons_list)):
                if buttons_list[i]:
                    buttons |= 1 << i
            master.mav.manual_control_send(
            master.target_system,  # target system
            x,                     # roll
            y,                     # pitch
            z,                     # throttle
            r,                     # yaw
            buttons                # bitmask for buttons
            )
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
