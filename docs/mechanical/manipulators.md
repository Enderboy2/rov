---
title: Manipulators & Tooling
---

# Mechanical — Manipulators & Tooling

[INSERT DETAILS HERE: Complete this section with the following information]

---

## Manipulator Design

### Design Rationale

[INSERT DETAILS HERE: Number of manipulators, degrees of freedom per arm, actuation method (servo, hydraulic, pneumatic), gripper type, why this design was selected over alternatives]

### Specifications

| Parameter | Value |
|---|---|
| **Number of Manipulators** | [INSERT DETAILS HERE] |
| **Degrees of Freedom** | [INSERT DETAILS HERE] |
| **Actuation** | [INSERT DETAILS HERE: Servo model, torque rating] |
| **Gripper Type** | [INSERT DETAILS HERE: Parallel jaw, compliant, custom] |
| **Max Grip Force** | [INSERT DETAILS HERE] |
| **Reach** | [INSERT DETAILS HERE] |
| **Control Method** | [INSERT DETAILS HERE: Joystick button mapping, PWM channels] |

``

---

## Tooling Attachments

[INSERT DETAILS HERE: Any additional tools mounted on the ROV — measurement devices, sampling tools, hooks, cutters. Include attachment method and quick-change capability if applicable]

---

## Pilot Interaction

Manipulator control integrates with the **Reverse Mode** virtual joystick system (see [Topside Software](../software/topside.md#reverse-mode-virtual-joystick-vjoy)). When engaged, control axes are swapped to match the pilot's perspective when the ROV faces the operator during close-proximity manipulator tasks.

[INSERT DETAILS HERE: Specific joystick channels mapped to manipulator axes, any speed scaling or fine-control mode]
