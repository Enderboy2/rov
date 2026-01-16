import pyvjoy
import time

j = pyvjoy.VJoyDevice(1)
center = 32768/2
def send_axes(roll, pitch, throttle, yaw):
    j.set_axis(pyvjoy.HID_USAGE_X,  int(center + roll))
    j.set_axis(pyvjoy.HID_USAGE_Y,  int(center + pitch))
    j.set_axis(pyvjoy.HID_USAGE_Z,  int(center + throttle))
    j.set_axis(pyvjoy.HID_USAGE_RZ, int(center + yaw))

while True:
    # Example: move right + forward
    values = list(map(float,input().split()))
    print(values)
    send_axes(
        roll=values[0] * center, # lateral in negative
        pitch=values[1] * center, # forward
        throttle=values[2] * center, # yaw in negative values
        yaw=values[3] * center#
    )
    time.sleep(0.05)