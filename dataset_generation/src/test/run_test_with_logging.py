#!/usr/bin/env python3
import os
import sys
import logging
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_execution.log')
    ]
)
logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None):
    """Run a shell command and return the output and return code."""
    logger.info(f"Running command: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Command output:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"Command errors:\n{result.stderr}")
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Error output:\n{e.stderr}")
        return e.returncode, e.stdout, e.stderr

def main():
    logger.info("Starting test execution with detailed logging...")
    
    # Check if we're running as root (required for Mininet)
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Please run with sudo.")
        return 1
    
    # Check if test_config.json exists
    if not os.path.isfile('test_config.json'):
        logger.error("test_config.json not found. Please run simple_test.py first.")
        return 1
    
    # Start Ryu controller in the background
    logger.info("Starting Ryu controller...")
    ryu_cmd = "ryu-manager --verbose controller/ryu_controller_app.py"
    ryu_process = subprocess.Popen(
        ryu_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give Ryu some time to start
    logger.info("Waiting for Ryu controller to start...")
    time.sleep(10)
    
    # Run the main script with test config
    logger.info("Starting dataset generation...")
    return_code, stdout, stderr = run_command("python3 main.py test_config.json")
    
    # Terminate Ryu controller
    logger.info("Terminating Ryu controller...")
    ryu_process.terminate()
    
    if return_code == 0:
        logger.info("Test completed successfully!")
        
        # Check for output files
        output_files = [
            'test_traffic.pcap',
            'test_features.csv',
            'test_flow_features.csv',
            'test_timeline.csv'
        ]
        
        for file in output_files:
            if os.path.isfile(file):
                logger.info(f"Output file found: {file} (size: {os.path.getsize(file)} bytes)")
            else:
                logger.warning(f"Output file not found: {file}")
    else:
        logger.error(f"Test failed with exit code {return_code}")
        logger.error(f"Error output:\n{stderr}")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
