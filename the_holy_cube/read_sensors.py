from pymavlink import mavutil
import time


master = mavutil.mavlink_connection('udp:192.168.137.1:14550') # usb ('COM7', baud=115200)

master.wait_heartbeat()
print("Connected to system", master.target_system)

# set the frequenncy 
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_EXTRA1,
    50,
    1
)


state = {
    "roll": None,
    "pitch": None,
    "yaw": None,
    "depth": None,
}

while True:
    msg = master.recv_match(blocking=False)
    if not msg:
        time.sleep(0.001)
        continue

    msg_type = msg.get_type()

    # el IMU
    if msg_type == "ATTITUDE":
        state["roll"]  = msg.roll
        state["pitch"] = msg.pitch
        state["yaw"]   = msg.yaw

    # el depth ely ehna me4 mewasalino :(
    elif msg_type == "VFR_HUD":
        state["depth"] = -msg.alt  # positive depth underwater

    if state["roll"] is not None and state["depth"] is not None:
        print(
            f"Roll: {state['roll']:.2f} rad | "
            f"Pitch: {state['pitch']:.2f} rad | "
            f"Yaw: {state['yaw']:.2f} rad | "
            f"Depth: {state['depth']:.2f} m"
        )




