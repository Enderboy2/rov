# Topside (Surface Control Unit)

This directory contains all software executed on the surface laptop during a pool run.

### Directory Breakdown
* `/control/` - Scripts handling QGroundControl integration, Virtual Joystick (vJoy), and custom flight modes (e.g., Reverse Mode).
* `/vision/` - YOLOv8 inference scripts and the RealSense `.bag` file measurement tools.
* `/dashboard/` - The vanilla HTML/JS/CSS frontend for viewing the `ustreamer` MJPEG camera feeds.