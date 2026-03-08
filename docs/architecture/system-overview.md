---
title: System Architecture
---

# System Architecture — 3-Tier Distributed Split-Processing

Encore employs a **3-Tier Distributed Split-Processing Architecture** over an Ethernet tether. Each tier is purpose-scoped to prevent CPU bottlenecking and minimize tether latency. No single node performs both real-time control and heavy compute.

---

## Design Rationale

Traditional ROV architectures consolidate compute on a single companion computer. This creates two failure modes:

- **CPU contention:** AI inference (YOLOv8) competes with video encoding and MAVLink routing for CPU cycles, introducing non-deterministic latency into the control loop.
- **Tether bandwidth saturation:** Encoding and transmitting multiple high-resolution camera feeds alongside telemetry data saturates a single uplink.

The split-processing model eliminates both by distributing workloads across three tiers with strict responsibility boundaries.

---

## Tier Breakdown

### Tier 1 — Topside (Surface Control Unit)

**Hardware:** Surface laptop (x86_64)  
**OS:** Ubuntu / Windows (dual-boot capable)  
**Role:** Heavy compute offloading, pilot interface, mission control

| Service | Function |
|---|---|
| **QGroundControl** | Primary pilot interface, telemetry display, parameter tuning |
| **ROS Master** | Central ROS node coordination |
| **YOLOv8 Inference** | Crab detection from HTTP MJPEG stream pulled from Jetson |
| **HTML/JS Dashboard** | Multi-camera MJPEG feed viewer (vanilla, no framework) |
| **Reverse Mode (vJoy)** | Python virtual joystick axis remapping for manipulator tasks |
| **pull_bag.sh** | SCP transfer of RealSense `.bag` files for offline Euclidean distance measurement |

**Network:** Ethernet tether uplink to Jetson Orin Nano.

---

### Tier 2 — Companion Computer

**Hardware:** NVIDIA Jetson Orin Nano  
**Storage:** NVMe SSD (boot drive + data logging)  
**OS:** Ubuntu (headless, no GUI)  
**Role:** On-vehicle video streaming, depth recording, MAVLink relay

| Service | Function |
|---|---|
| **mavlink-router** | MAVLink message relay between Cube Orange+ (serial) and Topside (UDP) |
| **ustreamer (×6)** | Pure MJPEG passthrough for 6 USB cameras — zero CPU transcode |
| **rs-record** | Intel RealSense D435i depth `.bag` recording to NVMe SSD |
| **jetson_cli.sh** | Custom bash CLI wrapper controlling all services via `systemd` |

**Design Decision — MJPEG Passthrough:** The Orin Nano lacks a hardware NVENC encoder. Transcoding 6 camera feeds in software would consume the entire CPU budget. By selecting USB cameras that output native MJPEG and using `ustreamer` in passthrough mode, the Jetson performs **zero video encoding** — raw MJPEG frames are forwarded directly to the tether. This reduces per-stream CPU overhead to near zero and preserves bandwidth.

---

### Tier 3 — Firmware (Flight Controller)

**Hardware:** Cube Orange+ (STM32H7)  
**Firmware:** Custom ArduSub fork (C++)  
**Role:** Hard real-time motor control, sensor fusion, PID stabilization

| Function | Detail |
|---|---|
| **PID Loop Rate** | 400 Hz deterministic cycle |
| **Motor Mixing** | Custom 8-thruster 6-DOF matrix (`AP_Motors6DOF.cpp`) |
| **IMU Fusion** | Onboard accelerometer + gyroscope sensor fusion |
| **Depth Hold** | Barometric pressure-based depth stabilization |
| **MAVLink** | Serial link to Jetson via `mavlink-router` |

---

## System Interconnect Diagram (SID)

``

### Data Flow Summary

Pilot Input (Joystick)
  → QGroundControl (Topside)
    → MAVLink over Ethernet Tether
      → mavlink-router (Jetson)
        → Serial UART → Cube Orange+
          → PID Loop → PWM → ESCs → Thrusters

Camera Feeds (6× USB)
  → ustreamer MJPEG passthrough (Jetson)
    → HTTP over Ethernet Tether
      → HTML/JS Dashboard (Topside)

RealSense D435i Depth
  → rs-record → .bag file (Jetson NVMe SSD)
    → pull_bag.sh SCP → Topside
      → Offline Euclidean distance calculation

YOLOv8 AI Inference
  → HTTP pull of MJPEG stream from Jetson
    → YOLOv8 model (Topside GPU/CPU)
      → Crab detection overlay

---

## Network Topology

| Link | Protocol | Medium |
|---|---|---|
| Topside ↔ Jetson | Ethernet (TCP/UDP) | Cat5e/Cat6 tether |
| Jetson ↔ Cube Orange+ | MAVLink (serial) | UART |
| Cameras ↔ Jetson | USB 2.0/3.0 | Internal USB hub |
| RealSense ↔ Jetson | USB 3.0 | Direct connect |

---

## Latency Budget

| Path | Expected Latency |
|---|---|
| Joystick → Thruster PWM | < 50 ms (MAVLink + PID cycle) |
| Camera → Dashboard display | < 150 ms (MJPEG passthrough, no transcode) |
| RealSense recording | 0 ms network (local NVMe write) |
| `.bag` file retrieval | Non-real-time (SCP batch transfer post-mission) |
