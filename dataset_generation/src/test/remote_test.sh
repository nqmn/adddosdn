#!/bin/bash

# Set up logging
exec > >(tee -a /home/user/dataset/test_run/test_remote.log) 2>&1

# Print environment information
echo "=== Environment Information ==="
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "Current user: $(whoami)"
echo "Working directory: $(pwd)"
echo "Python version: $(python3 --version 2>&1)"
echo "Pip version: $(pip3 --version 2>&1)"
echo "============================="

# Install required dependencies
echo "Installing required dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev
sudo pip3 install --upgrade pip
sudo pip3 install mininet ryu scapy pandas

# Change to test directory
TEST_DIR="/home/user/dataset/test_run"
cd "$TEST_DIR" || { echo "Failed to change to test directory"; exit 1; }

# Check for required files
echo "Checking for required files..."
REQUIRED_FILES=("test_flow.py" "test_config.json" "main.py" "controller/ryu_controller_app.py" "topology.py")

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file not found: $file"
        exit 1
    fi
    echo "Found required file: $file"
done

# Run the test
echo "Starting test execution..."
sudo python3 test_flow.py

# Check results
if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
    exit 0
else
    echo "Test failed!"
    exit 1
fi
