from pymavlink import mavutil

master = mavutil.mavlink_connection('COM7', baud=115200) # mavlink routerd [('udp:192.168.137.1:14550')]

print("Waiting for heartbeat...")
master.wait_heartbeat()
print("Connected.")

while True:
    msg = master.recv_match(type=['STATUSTEXT', 'HEARTBEAT'], blocking=True)
    if not msg:
        continue

    if msg.get_type() == 'STATUSTEXT':
        print(f"STATUSTEXT: {msg.text}")

    if msg.get_type() == 'HEARTBEAT':
        armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
        print(f"Heartbeat: armed={armed}")
