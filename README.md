# Overflow Robotics - ROV Software Stack 
[![MATE Class](https://img.shields.io/badge/MATE_Class-Ranger-blue.svg)](https://materovcompetition.org/ranger)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![Hardware](https://img.shields.io/badge/Hardware-Jetson_Orin_Nano_%7C_Cube_Orange%2B-orange.svg)]()

This repository contains the complete software and control infrastructure for the Overflow Robotics MATE ROV. The system utilizes a split-processing architecture, offloading heavy computer vision (YOLO) and 3D reconstruction (Intel RealSense) to a surface control unit, while maintaining hard real-time stabilization and data routing on the ROV.

## System Architecture

Our software stack is divided into three distinct operational domains:

1. **Topside (Surface Control Unit):** Laptop running QGroundControl, YOLOv8 inference, and the primary vanilla HTML/JS video dashboard.
2. **Companion (Jetson Orin Nano):** Runs MJPEG `ustreamer` services for 6x USB cameras, `mavlink-router`, and RealSense `rs-record` data logging.
3. **Firmware (Cube Orange+):** Custom ArduSub build with a modified 6DOF motor mixing matrix to support our 8-thruster omnidirectional frame.

## Repository Structure
* `/topside/` - All Python scripts and HTML dashboards running on the surface laptop.
* `/companion/` - CLI management scripts and systemd services for the Jetson.
* `/firmware/` - Custom C++ matrix patches and `.param` backups for the flight controller.
* `/docs/` - Source files for the team's MkDocs documentation site.

## Getting Started

**1. Clone the repository:**
```bash
git clone https://github.com/Enderboy2/rov.git
cd rov