import time
import pygame
from pymavlink import mavutil


master = mavutil.mavlink_connection('COM7', baud=115200) # mavlink routerd [('udp:192.168.137.1:14550')]


# Wait for heartbeat 
print("Waiting for CubePilot heartbeat...")
master.wait_heartbeat()
print("Connected to CubePilot!")
# arming the vehicul instantly
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,      # confirmation
    1,      # ARM
    0, 0, 0, 0, 0, 0
)

while True:
    msg = master.recv_match(type='HEARTBEAT', blocking=True)
    armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
    if armed:
        print("🔥 VEHICLE ARMED!")
        break
    else:
        print("Still disarmed...")
        time.sleep(0.5)
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    exit()

js = pygame.joystick.Joystick(0)
js.init()
print("Joystick detected:", js.get_name())

# scale it from 1,-1 to 1000,-1000
def scale_axis(value):
    return int(value * 1000)

def send_manual_control():
    pygame.event.pump() 
    x  = scale_axis(js.get_axis(0) )   # Roll  
    y  = scale_axis(js.get_axis(1))    # Pitch 
    z  = scale_axis(js.get_axis(2))     # Throttle
    r  = scale_axis(js.get_axis(3))     # Yaw

    # buttons to bitmask
    for i in range(js.get_numbuttons()):
        if js.get_button(i):
            buttons |= 1 << i
    buttons |= 1 << 3

    # Send MANUAL_CONTROL
    master.mav.manual_control_send(
        master.target_system,  # target system
        x,                     # roll
        y,                     # pitch
        z,                     # throttle
        r,                     # yaw
        buttons                # bitmask for buttons
    )
    print(master.target_system)
    print(f"Sent: R={x} P={y} T={z} Y={r} Buttons={bin(buttons)}")


while True:
    buttons = js.get_

    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,      # confirmation
        1,      # ARM
        0, 0, 0, 0, 0, 0
    )

try:
    while True:
        send_manual_control()
        time.sleep(0.05)  # 20 Hz

except KeyboardInterrupt:
    print("Exiting...")
    pygame.quit()
