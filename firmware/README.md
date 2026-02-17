#  Firmware (Cube Orange+)

This directory acts as our backup for the flight controller. **DO NOT** upload the entire ArduSub C++ source code tree here.

### Directory Breakdown
* `/frame_matrix/` - Custom motor mixing C++ patches (e.g., `AP_Motors6DOF.cpp`) handling our specific 8-thruster vector math.
* `/qgc_params/` - Date-stamped backups of our QGroundControl configurations. If the Cube floods or burns out, we can flash a new one and restore our exact setup in 60 seconds.