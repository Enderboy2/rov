---
title: Home
---

# Overflow Robotics — Encore

**Team:** Overflow Robotics  
**Vehicle:** Encore  
**Competition:** MATE ROV — Ranger Class  

---

## Technical Documentation

This site contains the complete engineering documentation for **Encore**, our Ranger-class remotely operated vehicle. The documentation covers the full system architecture, software stack, custom firmware, mechanical design, electrical systems, and operational safety procedures.

### Documentation Map

| Section | Contents |
|---|---|
| **System Architecture** | 3-Tier distributed split-processing architecture, SID, data flow |
| **Software** | Topside control unit, companion computer, vision pipeline, pilot tooling |
| **Firmware** | Cube Orange+ ArduSub modifications, custom motor mixing matrix |
| **Mechanical** | Frame design, thruster layout, manipulator systems, buoyancy |
| **Electrical** | Power distribution, tether design, ESC wiring, sensor integration |
| **Safety** | Pre-dive checklists, lockout procedures, emergency protocols |
| **Future Improvements** | Planned R&D for subsequent competition seasons |

---

## Architecture at a Glance

Encore operates on a **3-Tier Distributed Split-Processing Architecture** connected via an Ethernet tether:

- **Tier 1 — Topside (Surface Control Unit):** Heavy compute offloading — AI inference, pilot controls, telemetry visualization.
- **Tier 2 — Companion Computer (Jetson Orin Nano):** Headless on-vehicle compute — video streaming, depth recording, MAVLink routing.
- **Tier 3 — Firmware (Cube Orange+):** Hard real-time 400 Hz PID stabilization, custom 8-thruster omnidirectional motor mixing.

``

---

## Quick Links

- **Source Repository:** [github.com/Enderboy2/rov](https://github.com/Enderboy2/rov)
- **Competition:** [MATE ROV Competition](https://materovcompetition.org/)
