---
title: Power Distribution
---

# Electrical — Power Distribution

[INSERT DETAILS HERE: Complete this section with the following information]

---

## Power Budget

| Load | Voltage | Max Current | Power |
|---|---|---|---|
| **Thrusters (×8)** | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **Jetson Orin Nano** | 5V DC (via regulator) | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **Cube Orange+** | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **Cameras (×6)** | 5V USB | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **RealSense D435i** | 5V USB 3.0 | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **Servos / Manipulators** | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **LEDs / Lighting** | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **Total System** | — | — | [INSERT DETAILS HERE] |

---

## Power Supply

[INSERT DETAILS HERE: Topside power supply model, voltage, fuse rating, voltage regulator(s) on ROV, any DC-DC converters]

| Parameter | Value |
|---|---|
| **Supply Voltage** | [INSERT DETAILS HERE: e.g., 48V DC from topside] |
| **Max Current (fused)** | [INSERT DETAILS HERE] |
| **Fuse Type & Rating** | [INSERT DETAILS HERE] |
| **Voltage Regulation (ROV-side)** | [INSERT DETAILS HERE] |

---

## ESC Configuration

| Parameter | Value |
|---|---|
| **ESC Model** | [INSERT DETAILS HERE] |
| **ESC Count** | 8 |
| **PWM Input Range** | [INSERT DETAILS HERE: e.g., 1100–1900 µs] |
| **Neutral PWM** | 1500 µs |
| **Protocol** | Standard PWM from Cube Orange+ |

---

## Wiring Diagram

[INSERT DETAILS HERE: High-level wiring diagram or schematic description — power distribution from supply through fuse, to ESCs, to Jetson regulator, to Cube Orange+ power module]

``

---

## Grounding & Isolation

[INSERT DETAILS HERE: Grounding strategy, any galvanic isolation between topside and ROV-side power, waterproofing of electrical connections]
