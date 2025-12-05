import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from mavros_msgs.msg import OverrideRCIn
from mavros_msgs.srv import CommandBool
import ast

class JoyStringToMavros(Node):
    def __init__(self):
        super().__init__('joy_string_to_mavros')

        self.subscription = self.create_subscription(
            String,
            'joystick_data',
            self.listener_callback,
            10)

        self.publisher = self.create_publisher(
            OverrideRCIn,
            '/mavros/rc/override',
            10)
            
        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')

        self.get_logger().info('Bridge Started: Parsing Fix Applied')

    def listener_callback(self, msg):
        try:
            if 'Buttons:' in msg.data:
                parts = msg.data.split('Buttons:')
                
                # --- FIX: Remove the trailing comma ---
                axes_str = parts[0].replace('Axes:', '').strip()
                if axes_str.endswith(','):
                    axes_str = axes_str[:-1]
                    
                buttons_str = parts[1].strip()
                
                # Parse to lists
                axes = ast.literal_eval(axes_str)
                buttons = ast.literal_eval(buttons_str)
                
                # Handle Tuple case if it still happens (Safety)
                if isinstance(axes, tuple):
                    axes = axes[0]
                
                self.map_and_publish(axes, buttons)

        except Exception as e:
            self.get_logger().error(f"Parsing Error: {e}")

    def map_and_publish(self, axes, buttons):
        rc_msg = OverrideRCIn()
        # Initialize to ignore
        rc_msg.channels = [65535] * 18 

        # --- MAPPING BASED ON YOUR LOGS ---
        # Your log: [-0.41, -0.05, 0.01, 0.01, -1.0, -1.0]
        # This looks like: [LeftX, LeftY, RightX, RightY, L2, R2]
        
        try:
            # ROLL (Right Stick L/R -> Index 2)
            if len(axes) > 2:
                rc_msg.channels[0] = self.map_value(axes[2], 1000, 2000)

            # PITCH (Right Stick U/D -> Index 3)
            # Inverted: Up on stick (-1) = Pitch Forward (1000 or 2000 depending on frame)
            # Usually Pitch Forward = PWM Low (1000) for Plane, PWM High (2000) for Multi-rotor? 
            # Standard: Forward stick -> PWM 1000-1100 (Pitch down/forward)
            # Let's try NON-INVERTED first for Pitch if it feels wrong
            if len(axes) > 3:
                rc_msg.channels[1] = self.map_value(axes[3], 1000, 2000, invert=True) 
            
            # THROTTLE (Left Stick U/D -> Index 1)
            # Inverted: Up on stick (-1) = PWM 2000 (High Throttle)
            if len(axes) > 1:
                rc_msg.channels[2] = self.map_value(axes[1], 1000, 2000, invert=True)

            # YAW (Left Stick L/R -> Index 0)
            if len(axes) > 0:
                rc_msg.channels[3] = self.map_value(axes[0], 1000, 2000)

            # ARMING (Button X -> Index 0 in your list)
            if len(buttons) > 0:
                # Safety: Only arm if throttle is low (PWM < 1100)
                if buttons[0] == 1 and rc_msg.channels[2] < 1100: 
                    self.arm_drone(True)
                # Disarm (Button Circle -> Index 1?)
                elif len(buttons) > 1 and buttons[1] == 1:
                     self.arm_drone(False)

            self.publisher.publish(rc_msg)
            
        except Exception as e:
            pass

    def map_value(self, x, out_min, out_max, invert=False):
        val = float(x)
        if invert:
            val = -val
        return int((val + 1.0) * (out_max - out_min) / 2.0 + out_min)

    def arm_drone(self, arm):
        if self.arming_client.service_is_ready():
            req = CommandBool.Request()
            req.value = arm
            self.arming_client.call_async(req)

def main(args=None):
    rclpy.init(args=args)
    node = JoyStringToMavros()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
