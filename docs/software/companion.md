---
title: Companion Computer
---

# Companion Computer — Jetson Orin Nano

The companion computer is an **NVIDIA Jetson Orin Nano** mounted inside the ROV enclosure, running fully headless Ubuntu booted from an NVMe SSD. Its role is strictly limited to three functions: MAVLink relay, video passthrough, and depth recording. No AI inference or heavy compute runs on this node.

---

## Hardware Specifications

| Parameter | Value |
|---|---|
| **Board** | NVIDIA Jetson Orin Nano Developer Kit |
| **CPU** | 6-core Arm Cortex-A78AE |
| **GPU** | 1024-core NVIDIA Ampere (unused for video) |
| **RAM** | 8 GB LPDDR5 |
| **Boot Drive** | NVMe SSD (also used for `.bag` data logging) |
| **OS** | Ubuntu (headless, no desktop environment) |
| **Network** | Gigabit Ethernet via tether to topside |

---

## Service Architecture

All services are managed and controlled through stream_cli.py, a custom Python CLI.

### Service Inventory

| Service | Binary | Function |
|---|---|---|
| **mavlink-router** | `mavlink-routerd` | MAVLink relay: Cube Orange+ (serial) ↔ Topside (UDP) |
| **ustreamer ×6** | `ustreamer` | MJPEG passthrough for 6 USB cameras |

---

## Video Pipeline — ustreamer MJPEG Passthrough

### Problem

The Orin Nano **lacks a hardware NVENC video encoder**. Software-encoding 6 simultaneous camera feeds (e.g., H.264 via `ffmpeg`) would consume the entire CPU budget and introduce encoding latency.

### Solution

All 6 USB cameras are selected to output **native MJPEG** directly from their onboard ISPs. `ustreamer` operates in **passthrough mode** — it reads raw MJPEG frames from the camera's V4L2 device and serves them over HTTP without any transcoding.

### Per-Stream Resource Cost

| Metric | Value |
|---|---|
| **CPU per stream** | < 1% (no transcode) |
| **Bandwidth per stream** | [INSERT DETAILS HERE: Measured bandwidth per stream at operating resolution] |
| **Total bandwidth (6 streams)** | [INSERT DETAILS HERE: Aggregate measured bandwidth] |
| **Latency contribution** | ~1 frame (capture-to-HTTP, no encode buffer) |

### ustreamer Configuration

Each camera instance runs with parameters:

```bash
ustreamer \
  --device /dev/video{N} \
  --host 0.0.0.0 \
  --port 800{N} \
  --format mjpeg \
  --resolution 640x480 \
  --desired-fps 15
  --allow-origin=*
```

[INSERT DETAILS HERE: USB camera model/make] Resolution 640x480 by default , configurable per camera at launch via: start cam <port> <res> FPS: 15

Devices are autodiscovered at startup using v4l2-ctl --list-devices.Regular USB cameras use the 
first /dev/videoX node, Intel RealSense uses the fifth.

---

## MAVLink Routing — mavlink-router

`mavlink-router` bridges the Cube Orange+ flight controller (connected via serial UART) to the topside laptop (connected via Ethernet UDP).

### Configuration

```ini
[UartEndpoint flight_controller]
Device = /dev/ttyACM0
Baud = 115200

[UdpEndpoint topside]
Mode = Normal
Address = [TOPSIDE_IP]
Port = 14550
```

[INSERT DETAILS HERE: Actual serial device path, baud rate, topside IP address, any additional MAVLink endpoints]

### Design Rationale

Running `mavlink-router` on the Jetson rather than a dedicated microcontroller provides:

- **Software-configurable routing** — add/remove endpoints without hardware changes
- **Message filtering** — can selectively forward/drop MAVLink message types
- **Logging** — optional MAVLink `.tlog` capture for post-mission analysis

---

## RealSense Recording — rs-record

The **Intel RealSense D435i** connects directly to the Jetson via USB 3.0. The `rs-record` utility captures synchronized RGB + depth frames into `.bag` files on the NVMe SSD.

- **Storage target:** Local NVMe SSD (same drive as OS boot)
- **Retrieval:** Post-mission via `pull_bag.sh` (SCP from topside)
- **Format:** ROS `.bag` — compatible with `rosbag play` and `pyrealsense2` offline processing

**Recording resolution:** 1920 × 1080 (RGB, 30 FPS); 1280 × 720 (stereo depth, 90 FPS).  
**Typical file size per minute of recording:** ~400 MB – 5 GB, depending on resolution and frame rate.

---

## stream_cli.py — Service Management CLI

A custom Python CLI providing a unified interface to start, stop, and monitor all Jetson camera streams and MAVLink routing.

### Usage

```bash
# Start all camera streams
start all

# Start a specific camera
start cam 8000

# Start a specific camera with custom resolution
start cam 8000 1280x720

# Stop a specific camera
stop cam 8000

# Restart a specific camera
restart cam 8000

# Start MAVLink routing
start mavlink

# Check status of all services
list

# Re-discover cameras
refresh

# Exit and stop everything
exit
```

Error handling: if a stream fails to start, status shows 
error in the table. Ctrl+C triggers clean shutdown of 
all streams and MAVLink. Camera ports start at 8000 and 
increment by 1 per camera.

### Design Rationale

Wrapping `systemctl` commands behind a purpose-built CLI reduces operator error during time-critical pool runs. A single command replaces multiple `sudo systemctl start/stop/status` invocations and enforces correct service startup order.
