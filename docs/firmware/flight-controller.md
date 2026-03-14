---
title: Flight Controller
---

# Firmware — Cube Orange+ Flight Controller

The flight controller is a **Cube Orange+** (STM32H7 dual-core Cortex-M7) running a custom fork of **ArduSub**. Modifications are limited to the motor mixing matrix and frame definition — the core ArduSub PID stabilization, sensor fusion, and MAVLink stack remain upstream.

---

## Hardware

| Parameter | Value |
|---|---|
| **Controller** | CubePilot Cube Orange+ |
| **MCU** | STM32H757 (dual-core Cortex-M7, 480 MHz) |
| **IMU** | Triple-redundant (ICM-42688, ICM-20948, ICM-20602) |
| **Barometer** | Dual MS5611 |
| **Firmware** | ArduSub (custom fork) |
| **PID Loop Rate** | 400 Hz |
| **PWM Outputs** | 8 channels → ESCs → Thrusters |
| **Serial** | UART to Jetson Orin Nano (MAVLink) |

``

---

## Firmware Modifications

### Scope of Changes

Only one source file is modified from upstream ArduSub:

- **`AP_Motors6DOF.cpp`** — Motor mixing matrix definition

All other ArduSub subsystems (EKF, PID controllers, MAVLink handlers, failsafes) run unmodified upstream code. This minimizes maintenance burden when rebasing against new ArduSub releases.

### Custom Frame Definition — `SUB_FRAME_CUSTOM`

The stock ArduSub frame types (`BlueROV1`, `BlueROV2`, `VECTORED_6DOF`, etc.) do not support our 8-thruster omnidirectional geometry. A new frame entry `SUB_FRAME_CUSTOM` (internally named `SUB_FRAME_ENCORE`) was added to the `setup_motors()` switch block with a fully custom 6-DOF mixing matrix.

See **[Motor Mixing Matrix](motor-mixing.md)** for the complete matrix definition, column semantics, and tuning rationale.

---

## PID Stabilization

The Cube Orange+ runs a **400 Hz** deterministic PID loop for attitude stabilization. Inputs from the topside joystick (via MAVLink RC override) are blended with IMU sensor fusion outputs to produce per-motor thrust commands.

### Control Loop Flow

```
Joystick Input (MAVLink RC Override)
  ↓
Desired Attitude / Thrust Vector
  ↓
EKF Sensor Fusion (IMU + Barometer)
  ↓
PID Error Calculation (400 Hz)
  ↓
Motor Mixing Matrix (AP_Motors6DOF)
  ↓
Per-Motor Thrust → PWM Conversion
  ↓
ESC PWM Output (8 channels)
  ↓
Thrusters
```

### Stabilization Modes

| Mode | Behavior |
|---|---|
| **Manual** | Raw joystick → thrust, no stabilization |
| **Stabilize** | Attitude hold on roll/pitch, manual yaw/throttle |
| **Depth Hold** | Stabilize + barometric depth lock |


---

## Parameter Backup Strategy

QGroundControl parameter files are version-controlled in `firmware/qgc_params/` with date-stamped filenames. Recovery procedure:

1. Flash stock ArduSub to a replacement Cube Orange+.
2. Load the latest `.params` file via QGC **Parameters → Load From File**.
3. Upload the custom `AP_Motors6DOF.cpp` firmware build.
4. Verify motor directions via QGC **Motor Test**.

**Target recovery time:** < 60 seconds from bare hardware to flight-ready configuration.

### ArduSub Version and Build Details
