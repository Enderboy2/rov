---
title: Motor Mixing Matrix
---

# Motor Mixing Matrix — Custom 8-Thruster 6-DOF

The motor mixing matrix defines how high-level pilot commands (roll, pitch, yaw, throttle, forward, lateral) are decomposed into individual thrust commands for each of the 8 motors. This is the core of Encore's omnidirectional maneuverability.

---

## Matrix Definition

Defined in `AP_Motors6DOF.cpp` under `SUB_FRAME_CUSTOM` (frame string: `SUB_FRAME_ENCORE`):

| Motor | Position | Roll | Pitch | Yaw | Throttle | Forward | Lateral |
|---|---|---|---|---|---|---|---|
| **MOT_1** | Front-Right-Top | +0.071 | +0.2625 | −0.3335 | +0.525 | +0.7875 | +0.454 |
| **MOT_2** | Front-Left-Top | −0.071 | +0.2625 | +0.3335 | +0.525 | +0.7875 | −0.454 |
| **MOT_3** | Rear-Right-Top | +0.071 | −0.2625 | +0.3335 | +0.525 | +0.7875 | +0.454 |
| **MOT_4** | Rear-Left-Top | −0.071 | −0.2625 | −0.3335 | +0.525 | +0.7875 | −0.454 |
| **MOT_5** | Front-Right-Bottom | −0.071 | −0.2625 | −0.3335 | −0.525 | +0.7875 | +0.454 |
| **MOT_6** | Front-Left-Bottom | +0.071 | −0.2625 | +0.3335 | −0.525 | +0.7875 | −0.454 |
| **MOT_7** | Rear-Right-Bottom | −0.071 | +0.2625 | +0.3335 | −0.525 | +0.7875 | +0.454 |
| **MOT_8** | Rear-Left-Bottom | +0.071 | +0.2625 | −0.3335 | −0.525 | +0.7875 | −0.454 |

---

## Column Semantics

Each column in the `add_motor_raw_6dof()` call maps to a degree of freedom:

```cpp
add_motor_raw_6dof(
    motor_num,      // Motor index (1-8)
    roll_fac,       // Roll torque contribution (+/- 1.0)
    pitch_fac,      // Pitch torque contribution (+/- 1.0)
    yaw_fac,        // Yaw torque contribution (+/- 1.0)
    throttle_fac,   // Vertical thrust contribution (+/- 1.0)
    forward_fac,    // Forward/backward thrust contribution (+/- 1.0)
    lat_fac,        // Lateral (strafe) thrust contribution (+/- 1.0)
    testing_order   // Motor test sequence index
);
```

---

## Design Rationale

### Why a Custom Matrix?

Stock ArduSub frame types assume planar thruster arrangements (e.g., BlueROV2's 6-thruster vectored layout). Encore's frame uses **8 thrusters in a 3D omnidirectional configuration** — 4 top-mounted and 4 bottom-mounted at opposing cant angles. No stock frame type supports this geometry.

### Thruster Geometry

``

The 8 thrusters are arranged in **vertically mirrored pairs** — each top motor has a corresponding bottom motor at the same X/Y position but with inverted throttle polarity. This geometry provides:

- **Full 6-DOF control:** Independent authority over roll, pitch, yaw, heave, surge, and sway
- **Symmetric thrust envelope:** Equal thrust capability in all directions
- **Redundant vertical control:** Loss of any single vertical motor is partially compensated by its pair

### Factor Tuning

- **Roll factors (±0.071):** Intentionally low magnitude. The thruster moment arms for roll are short (thrusters are close to the roll axis), so small factors prevent roll overshoot.
- **Pitch factors (±0.2625):** Moderate magnitude reflecting the longer fore/aft moment arm relative to the pitch axis.
- **Yaw factors (±0.3335):** Tuned to balance yaw authority against cross-coupling into roll/pitch.
- **Throttle factors (±0.525):** Top motors positive, bottom motors negative. Opposing signs create net vertical thrust; equal magnitudes ensure zero vertical bias at neutral throttle.
- **Forward factors (+0.7875):** All motors contribute equally to forward thrust. The high magnitude reflects the canted thruster geometry's effective forward projection.
- **Lateral factors (±0.454):** Left/right motors have opposing signs. Magnitude tuned to account for the lateral force projection angle of the canted thrusters.

---

## Stabilization Path

The mixing matrix integrates into two stabilization functions:

### `output_armed_stabilizing()` (Default Path)

Standard linear superposition:

```
thrust[i] = roll × roll_factor[i]
           + pitch × pitch_factor[i]
           + yaw × yaw_factor[i]
           + throttle × throttle_factor[i]
           + forward × forward_factor[i]
           + lateral × lateral_factor[i]
```

Final output is clamped to `[-1.0, +1.0]` and multiplied by motor direction.

### `output_armed_stabilizing_vectored_6dof()` (6-DOF Normalized Path)

Separates the mixing into two independently-normalized groups to prevent saturation:

- **RPT group (Roll + Pitch + Throttle):** Attitude stabilization axes
- **YFL group (Yaw + Forward + Lateral):** Translation axes

Each group is normalized independently before summation:

```
thrust[i] = (rpt[i] / rpt_max) + (yfl[i] / yfl_max)
```

This prevents a maxed-out forward command from starving the attitude stabilization loop of motor headroom.

---

## Thrust-to-PWM Conversion

```cpp
int16_t calc_thrust_to_pwm(float thrust_in) {
    int16_t range_up = pwm_max - 1500;
    int16_t range_down = 1500 - pwm_min;
    return 1500 + thrust_in * (thrust_in > 0 ? range_up : range_down);
}
```

- **Neutral:** 1500 µs (zero thrust)
- **Full forward:** `pwm_max` µs
- **Full reverse:** `pwm_min` µs
- **Asymmetric scaling:** Accounts for ESCs with different forward/reverse deadbands

**ESC Model:** Blue Robotics Basic ESC (BESC30-R3)  
**Voltage Range:** 7-26 V (2S-6S LiPo)  
**Maximum Current:** 30 A  
**PWM Range:**  
* Minimum: 1100 µs  
* Neutral: 1500 µs  
* Maximum: 1900 µs  
**Signal Input Voltage:** 3.3-5 V  
**PWM Update Rate:** up to 400 Hz  
**Directionality:** Bidirectional (center is zero thrust)  

**Thruster Model:** APISQUEEN U2 Mini  
**Operating Voltage:** 12-16 V  
**Maximum Power:** 130 W  
**Maximum Current:** ~8 A  
**Maximum Thrust:** ~1.3 kgf  
**Thrust Curve:** Nonlinear (approximately quadratic)   
**Physical Size:** 95.8 x 77 mm  
