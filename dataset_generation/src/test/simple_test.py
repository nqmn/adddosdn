#!/usr/bin/env python3
import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_test.log')
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if the required environment is set up correctly"""
    logger.info("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        logger.error("Python 3.6 or higher is required")
        return False
    
    # Check required directories
    required_dirs = [
        '.',
        'attacks',
        'controller'
    ]
    
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            logger.error(f"Required directory not found: {dir_path}")
            return False
    
    # Check required files
    required_files = [
        'main.py',
        'config.json',
        'topology.py',
        'controller/ryu_controller_app.py',
        'attacks/gen_syn_flood.py',
        'attacks/gen_udp_flood.py',
        'attacks/gen_advanced_adversarial_ddos_attacks.py'
    ]
    
    for file_path in required_files:
        if not os.path.isfile(file_path):
            logger.error(f"Required file not found: {file_path}")
            return False
    
    logger.info("Environment check passed")
    return True

def create_test_config():
    """Create a test configuration file"""
    test_config = {
        "mininet_topology": "topology.py",
        "ryu_app": "controller/ryu_controller_app.py",
        "controller_port": 6633,
        "api_port": 8080,
        "traffic_types": {
            "normal": {
                "duration": 10,  # 10 seconds of normal traffic
                "scapy_commands": [
                    {
                        "host": "h3",
                        "command": "sendp(Ether()/IP(dst='10.0.0.5')/TCP(dport=80, flags='S'), loop=1, inter=0.5, verbose=0)",
                        "count": 5
                    }
                ]
            },
            "attacks": [
                {
                    "type": "syn_flood",
                    "duration": 10,  # 10 seconds of attack
                    "attacker": "h1",
                    "victim": "h6",
                    "script_name": "gen_syn_flood.py"
                }
            ]
        },
        "offline_collection": {
            "pcap_file": "test_traffic.pcap",
            "output_file": "test_features.csv"
        },
        "online_collection": {
            "output_file": "test_flow_features.csv",
            "poll_interval": 2
        },
        "label_timeline_file": "test_timeline.csv"
    }
    
    with open('test_config.json', 'w') as f:
        json.dump(test_config, f, indent=4)
    
    logger.info("Created test configuration file: test_config.json")
    return True

def main():
    logger.info("Starting simple test...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Please fix the issues and try again.")
        return 1
    
    # Create test config
    if not create_test_config():
        logger.error("Failed to create test configuration")
        return 1
    
    logger.info("Test setup complete. You can now run the test with:")
    logger.info("sudo python3 main.py test_config.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
