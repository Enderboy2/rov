# Use the community-standard ARM-based image for Jetson
# This is the user-verified tag for L4T R36.4.x (JetPack 6)
FROM dustynv/ros:humble-desktop-l4t-r36.4.0

# Set up the working environment
WORKDIR /root/ros2_ws

# Install essential system dependencies and the RealSense SDK
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    vim \
    # Install Intel RealSense SDK
    && mkdir -p /etc/apt/keyrings \
    && curl -sSf https://librealsense.intel.com/Debian/intel-librealsense.key | tee /etc/apt/keyrings/intel-librealsense.key > /dev/null \
    && echo "deb [signed-by=/etc/apt/keyrings/intel-librealsense.key] https://librealsense.intel.com/Debian/apt-key stable main" | tee /etc/apt/sources.list.d/intel-librealsense.list \
    && apt-get update \
    && apt-get install -y librealsense2-dkms librealsense2-utils librealsense2-dev \
    # Clean up apt cache
    && rm -rf /var/lib/apt/lists/*

# Copy your ROS 2 source code into the workspace's 'src' directory
COPY ./src ./src

# Build the workspace
RUN . /opt/ros/humble/setup.bash && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# Set up the entrypoint to automatically source the workspace
CMD ["/bin/bash", "-c", "source /root/ros2_ws/install/setup.bash && /bin/bash"]
