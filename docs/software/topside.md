---
title: Topside Software
---

# Topside Software — Surface Control Unit

The topside laptop serves as the primary operator station and heavy-compute offload node. All CPU-intensive workloads — AI inference, telemetry visualization, and offline measurement — execute here to avoid loading the companion computer.

---

## Software Stack

| Component | Language / Framework | Purpose |
|---|---|---|
| **QGroundControl** | C++ (prebuilt) | Pilot interface, telemetry, parameter tuning |
| **ROS Master** | ROS 1 / Python | Central node coordination and topic routing |
| **YOLOv8 Inference** | Python / Ultralytics | Real-time crab detection from MJPEG stream |
| **HTML/JS Dashboard** | Vanilla HTML, CSS, JS | Multi-camera MJPEG feed viewer |
| **Reverse Mode (vJoy)** | Python | Virtual joystick axis remapping |
| **pull_bag.sh** | Bash | SCP retrieval of RealSense `.bag` files |

---

## QGroundControl Integration

**QGroundControl (QGC)** is the primary pilot interface. It connects to the Cube Orange+ flight controller via MAVLink, routed through `mavlink-router` on the Jetson.

- **Telemetry display:** Real-time attitude, depth, heading, battery voltage
- **Parameter tuning:** PID gains, motor direction, failsafe thresholds
- **Joystick mapping:** Physical gamepad axes → MAVLink RC override channels
- **Flight modes:** Manual, Stabilize, Depth Hold

[INSERT DETAILS HERE: QGC version used, specific parameter file name, joystick model and button mapping]

---

## YOLOv8 Vision Pipeline

The topside runs **YOLOv8** (Ultralytics) for competition-specific object detection, specifically crab identification.

### Architecture

1. The Jetson exposes each USB camera as an HTTP MJPEG endpoint via `ustreamer`.
2. The topside YOLOv8 script pulls a single designated camera stream over HTTP.
3. Inference executes on the topside CPU/GPU — **not** on the Jetson.
4. Detection results are overlaid on the video feed in real time.

### Design Rationale

Running inference topside rather than on the Jetson eliminates GPU contention on the companion computer. The Jetson's sole video responsibility is MJPEG passthrough, and inference latency is absorbed by the topside's higher compute budget.

- **Model Variant:** YOLOv8n (nano)  
- **Training Dataset:** ~150 labeled images (2 classes: european green crab, distractor)  
- **Validation Performance:** mAP@0.5 = 99.5%, Precision = 85.6%, Recall = 100%  
- **Inference Performance:** Measured at 15 FPS model throughput, with inference latency averaging 10–20 ms per frame and total end-to-end system latency ranging from 50–75 ms from capture to rendered detection overlay.

---

## Reverse Mode — Virtual Joystick (vJoy)

**Reverse Mode** is a Python script that intercepts joystick input and programmatically swaps control axes. This is critical for manipulator tasks where the ROV faces the operator, inverting the pilot's spatial reference frame.

### Behavior

| Axis | Normal Mode | Reverse Mode |
|---|---|---|
| Left stick X | Yaw left/right | Yaw **inverted** |
| Left stick Y | Forward/backward | Forward/backward **inverted** |
| Right stick X | Lateral left/right | Lateral **inverted** |
| Right stick Y | Throttle up/down | Unchanged |

### Implementation

- Uses **vJoy** (virtual joystick driver) to create a virtual HID device.
- The script reads physical joystick input, applies axis transformations, and writes to the virtual device.
- QGroundControl binds to the virtual joystick, receiving pre-transformed input.
- Mode toggle is bound to a single button press for instant switching during a mission run.

[INSERT DETAILS HERE: Specific joystick button used for toggle, vJoy driver version, any additional axis scaling factors]

---

## Camera Dashboard

A **vanilla HTML/JS/CSS** web page served locally on the topside laptop. Displays MJPEG streams from all 6 cameras simultaneously.

### Features

- **Grid layout** of 6 camera feeds, each pulling from a `ustreamer` HTTP endpoint on the Jetson.
- **No framework dependencies** — pure `<img>` tags with MJPEG `src` URLs for minimal overhead.
- **Camera labels** for operator orientation (e.g., "Forward", "Down", "Manipulator").

**Stream Resolution:** 640×480  
**Grid Layout:** 6 feeds in one window (3×2)

---

## RealSense Distance Measurement — `pull_bag.sh`

The Intel **RealSense D435i** depth camera records `.bag` files locally on the Jetson's NVMe SSD via `rs-record`. Post-mission, the topside retrieves these files for offline processing.

### Workflow

1. **Recording:** `rs-record` runs as a `systemd` service on the Jetson, capturing depth + RGB frames to `.bag` format on the NVMe SSD.
2. **Transfer:** `pull_bag.sh` executes `scp` over the Ethernet tether to pull `.bag` files to the topside laptop.
3. **Processing:** A Python script opens the `.bag` file, extracts aligned depth frames, and computes **real-world Euclidean distances** between operator-selected points.

### Design Rationale

Live-streaming depth data over the tether would consume significant bandwidth and introduce latency into distance calculations. Recording locally and processing offline provides:

- **Full-resolution depth data** (no compression artifacts)
- **Repeatable measurements** (replay the `.bag` file multiple times)
- **Zero tether bandwidth cost** during the mission run

The Intel RealSense D435i records RGB video along with depth data for every pixel in the frame. The camera computes 3D spatial coordinates (X, Y, Z), obtaining the Z value using its infrared (IR) sensor and stereo cameras, where Z represents the distance from the camera to the observed object. This allows the system to determine the real-world distance between any two operator-selected points in the scene.