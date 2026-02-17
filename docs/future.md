---
title: Future Improvements
---

# Future Improvements

Planned research and development for subsequent competition seasons and long-term platform evolution.

---

## Software

### On-Vehicle AI Inference

The current architecture offloads YOLOv8 inference to the topside laptop. Future iterations will evaluate running inference directly on the Jetson Orin Nano's 1024-core Ampere GPU using TensorRT-optimized models, reducing detection latency by eliminating the tether round-trip for video frames.

**Prerequisite:** Resolve the NVENC encoder gap — either by sourcing cameras that output H.264 natively or by upgrading to a Jetson Orin NX with hardware encode support.

### ROS 2 Migration

The current stack uses ROS 1 for node coordination. Migrating to **ROS 2 (Humble/Iron)** provides:

- **DDS-based transport** — eliminates the single-point-of-failure ROS Master node
- **Real-time executor** — deterministic callback scheduling for time-critical sensor processing
- **Lifecycle nodes** — structured startup/shutdown for cleaner service management

### Autonomous Transect Capabilities

[INSERT DETAILS HERE: Planned waypoint-following or line-following autonomous modes, sensor requirements, integration with ArduSub mission planning]

---

## Firmware

### Dynamic Motor Mixing

The current mixing matrix uses static factors tuned empirically. Future work will investigate **runtime-adjustable mixing** — loading factor matrices from the SD card or via MAVLink parameters rather than requiring a firmware recompile.

### Thruster Health Monitoring

[INSERT DETAILS HERE: Planned current-sensing per ESC for real-time thruster health diagnostics, automatic degraded-mode reconfiguration if a motor fails]

---

## Mechanical

### Modular Frame System

[INSERT DETAILS HERE: Plans for a modular rail or slot-based frame allowing rapid reconfiguration of thruster positions and payload mounting between missions]

### Improved Depth Rating

[INSERT DETAILS HERE: Target depth rating for future competitions, enclosure redesign plans, pressure testing targets]

---

## Electrical

### Power-over-Ethernet (PoE) Tether

[INSERT DETAILS HERE: Feasibility study for consolidating power and data onto a single PoE cable, reducing tether diameter and drag]

### Battery-Backed Topside UPS

[INSERT DETAILS HERE: Uninterruptible power supply for the topside laptop to prevent data loss during power interruptions at competition venues]

---

## Competition Strategy

[INSERT DETAILS HERE: Lessons learned from current season, planned changes to pilot training, task prioritization strategy, time management improvements]
