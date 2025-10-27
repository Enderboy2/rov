# Use the official NVIDIA Isaac ROS base image for development on x86_64 (your laptop)
# NOTE: For the Jetson, you will use a different ARM-based image like dustynv/ros:humble-isaac-l4t-r35.4.1
FROM nvcr.io/nvidia/isaac-ros-dev-x86_64:2.1.0

# Set up the working environment
WORKDIR /root/ros2_ws

# Install essential system dependencies and the RealSense SDK
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    vim \
    # Add any other system tools you need here
    # Install Intel RealSense SDK
    && mkdir -p /etc/apt/keyrings \
    && curl -sSf https://librealsense.intel.com/Debian/intel-librealsense.key | tee /etc/apt/keyrings/intel-librealsense.key > /dev/null \
    && echo "deb [signed-by=/etc/apt/keyrings/intel-librealsense.key] https://librealsense.intel.com/Debian/apt-key stable main" | tee /etc/apt/sources.list.d/intel-librealsense.list \
    && apt-get update \
    && apt-get install -y librealsense2-dkms librealsense2-utils librealsense2-dev \
    # Clean up apt cache to keep the image small
    && rm -rf /var/lib/apt/lists/*

# Copy your ROS 2 source code into the workspace's 'src' directory
COPY ./src ./src

# Source ROS 2 and build the workspace
# This ensures all your custom packages are built and ready to use
RUN . /opt/ros/humble/setup.bash && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# Set up the entrypoint to automatically source the workspace
# This way, any new terminal will have access to your ROS packages
CMD ["/bin/bash", "-c", "source /root/ros2_ws/install/setup.bash && /bin/bash"]
