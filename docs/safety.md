---
title: Safety
---

# Safety Procedures

Safety is a core judging criterion in the MATE ROV competition. All procedures documented here are enforced during every pool run, practice session, and competition deployment.

---

## Pre-Dive Checklist

| # | Check | Verified By |
|---|---|---|
| 1 | All enclosure seals inspected — no visible O-ring damage or debris | [INSERT DETAILS HERE] |
| 2 | Tether connections secure at both ROV and topside ends | [INSERT DETAILS HERE] |
| 3 | Power supply fuse correctly rated and installed | [INSERT DETAILS HERE] |
| 4 | ESCs initialized — no audible alarm tones | [INSERT DETAILS HERE] |
| 5 | Cube Orange+ booted — QGC telemetry link established | [INSERT DETAILS HERE] |
| 6 | Jetson Orin Nano booted — SSH accessible from topside | [INSERT DETAILS HERE] |
| 7 | All 6 camera feeds visible on dashboard | [INSERT DETAILS HERE] |
| 8 | Motor test completed via QGC — all 8 thrusters spin correct direction | [INSERT DETAILS HERE] |
| 9 | Depth hold mode tested (dry) — barometer responding | [INSERT DETAILS HERE] |
| 10 | Kill switch functional — verified by arming then immediately killing | [INSERT DETAILS HERE] |
| 11 | Tether slack managed — no loops or kinks | [INSERT DETAILS HERE] |
| 12 | Pool area clear of obstructions and personnel in water | [INSERT DETAILS HERE] |

[INSERT DETAILS HERE: Any additional team-specific safety checks]

---

## Emergency Procedures

### Loss of Communication

[INSERT DETAILS HERE: Procedure when MAVLink link drops — does the ROV auto-disarm? Does the pilot surface the vehicle manually? Timeout thresholds]

### Water Ingress

[INSERT DETAILS HERE: Visual indicators of water ingress (e.g., condensation on camera, erratic IMU readings), immediate response protocol, power cutoff procedure]

### Electrical Fault

[INSERT DETAILS HERE: Overcurrent behavior, fuse blow procedure, manual kill switch location and operation]

### Entanglement

[INSERT DETAILS HERE: Tether entanglement response — pilot procedure, tether management role responsibilities]

---

## Lockout / Tagout (LOTO)

Prior to any physical maintenance or inspection of the ROV, the power supply must be fully disconnected and verified de-energized by the designated electrical lead. The main XT-60 input connector is physically unplugged from the power distribution board, and all team members are notified before any work begins. No maintenance is permitted on the vehicle while it remains connected to the surface power supply.

---

## Personal Protective Equipment (PPE)

Personal protective equipment such as goggles, gloves, closed-toe shoes, and additional situational PPE is mandatory when required. Equipment is handled only under the guidance of trained personnel, and all operations follow established safety checklists, job safety analyses, and emergency procedures.

---

## Safety Features — Design Integration

| Feature | Implementation |
|---|---|
| **Software kill switch** | Disarm function in QGroundControl using the MAVLink protocol. Emergency disarm mapped to PS4 joystick on the topside laptop. MAVLink Router on the NVIDIA Jetson Orin Nano Super forwards commands to the Cube Orange, which immediately cuts all thruster outputs upon disarm. Verified before each deployment by arming and immediately disarming to confirm motor shutdown. |
| **Hardware kill switch** | The fuse system acts as the hardware kill switch — cuts power from the entire system automatically on overcurrent or fault. |
| **Fuse protection** | 25A Clear Fuse at the start of the tether (main power input). 10A at each motor (×8) to protect individual thrusters from overcurrent. |
| **Leak detection** | [INSERT DETAILS HERE: Leak sensor model, alarm behavior] |
| **Positive buoyancy** | In case of power interruption, the ROV floats to the surface on its own as it is positively buoyant. |
| **Thruster guards** | Our U2 thrusters are equipped with full circular gaurd rings with radial struts, blocking small objects and or fingers. |

