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

All services are managed via `systemd` and controlled through `jetson_cli.sh`, a custom bash CLI wrapper.

### Service Inventory

| Service | Binary | Function | systemd Unit |
|---|---|---|---|
| **mavlink-router** | `mavlink-routerd` | MAVLink relay: Cube Orange+ (serial) ↔ Topside (UDP) | `mavlink-router.service` |
| **ustreamer ×6** | `ustreamer` | MJPEG passthrough for 6 USB cameras | `ustreamer-cam{1..6}.service` |
| **rs-record** | `rs-record` | RealSense D435i depth recording to NVMe | `rs-record.service` |

[INSERT DETAILS HERE: Exact systemd unit file names if different from above, any additional services running]

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
  --port 808{N} \
  --format MJPEG \
  --resolution [INSERT DETAILS HERE: resolution] \
  --desired-fps [INSERT DETAILS HERE: FPS]
```

[INSERT DETAILS HERE: USB camera model/make, actual /dev/video device assignments, any udev rules for persistent naming]

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

## jetson_cli.sh — Service Management CLI

A custom bash wrapper providing a unified interface to start, stop, and monitor all Jetson services.

### Usage

```bash
# Start all camera streams
./jetson_cli.sh cameras start

# Stop a specific camera
./jetson_cli.sh camera 3 stop

# Start MAVLink routing
./jetson_cli.sh mavlink start

# Start RealSense recording
./jetson_cli.sh realsense start

# Check status of all services
./jetson_cli.sh status
```

[INSERT DETAILS HERE: Actual CLI syntax if different from above, any additional subcommands, error handling behavior]

### Design Rationale

Wrapping `systemctl` commands behind a purpose-built CLI reduces operator error during time-critical pool runs. A single command replaces multiple `sudo systemctl start/stop/status` invocations and enforces correct service startup order.
