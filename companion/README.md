# Companion (Jetson Orin Nano)

This directory contains the headless, command-line (CLI) tools that run on the ROV's internal computer. 

### Directory Breakdown
* `/start/` - The master CLI wrapper scripts used to manually toggle video streams and routing.
* `/realsense/` - Automation scripts for `rs-record` to log depth data locally to the Jetson's NVMe SSD.
