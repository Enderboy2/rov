from pymavlink import mavutil

master = mavutil.mavlink_connection('COM7', baud=115200) # mavlink routerd [('udp:192.168.137.1:14550')]

print("Waiting for heartbeat...")
master.wait_heartbeat()
print("Connected.")

while True:
    msg = master.recv_match(blocking=True)
    if msg:
        print(f"Message received: {msg.get_type()}")
