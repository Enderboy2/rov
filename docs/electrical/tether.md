---
title: Tether
---

# Electrical — Tether Design

The tether is the single physical link between the topside control station and the ROV. It carries both Ethernet data and DC power.

---

## Tether Specifications

| Parameter | Value |
|---|---|
| **Length** | [INSERT DETAILS HERE] |
| **Cable Type** | [INSERT DETAILS HERE: e.g., Cat5e, Cat6, custom composite] |
| **Conductors** | [INSERT DETAILS HERE: Number and gauge of power conductors] |
| **Data Pairs** | [INSERT DETAILS HERE: Ethernet pair count] |
| **Outer Diameter** | [INSERT DETAILS HERE] |
| **Buoyancy** | [INSERT DETAILS HERE: Positive, negative, or neutral] |
| **Strain Relief** | [INSERT DETAILS HERE: Method at both ROV and topside ends] |

---

## Design Rationale

[INSERT DETAILS HERE: Why this tether construction was chosen — trade-offs between diameter (drag), conductor count (power capacity), flexibility, and cost. Any custom fabrication vs. off-the-shelf cable]

---

## Connectors

| End | Connector Type | Waterproof Rating |
|---|---|---|
| **ROV-side** | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |
| **Topside-side** | [INSERT DETAILS HERE] | [INSERT DETAILS HERE] |

``

---

## Bandwidth Budget

| Traffic | Protocol | Estimated Bandwidth |
|---|---|---|
| **6× Camera MJPEG** | HTTP | [INSERT DETAILS HERE] |
| **MAVLink Telemetry** | UDP | ~50 kbps |
| **RealSense (not live)** | N/A (local recording) | 0 (tether) |
| **YOLOv8 stream pull** | HTTP | Shared with camera feed |
| **Total** | — | [INSERT DETAILS HERE] |

The tether carries standard Ethernet — theoretical throughput of 100 Mbps (Cat5e) or 1 Gbps (Cat6). Actual utilization is dominated by the MJPEG camera streams.
