#!/usr/bin/env python3
"""
Comprehensive test and dataset generation framework for the AdDDoSDN project.

This script orchestrates the entire dataset generation process locally on an
Ubuntu machine, from environment verification to data processing, based on the
specifications in docs/scenario.md.
"""
import io
import sys
import re
import os
import signal
import time
import logging
import argparse
import subprocess
from pathlib import Path
import shutil
from scapy.all import rdpcap, Ether, IP, TCP, UDP, Raw, RandShort, sendp

# Suppress Scapy warnings
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from src.utils.process_pcap_to_csv import process_pcap_to_csv
from src.utils.enhanced_pcap_processing import (
    validate_and_fix_pcap_timestamps,
    enhanced_process_pcap_to_csv,
    improve_capture_reliability,
    verify_pcap_integrity
)

# Mininet imports
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

# Add attacks directory to Python path
sys.path.append(str(Path(__file__).parent.resolve() / "src" / "attacks"))
from gen_syn_flood import run_attack as run_syn_flood
from gen_udp_flood import run_attack as run_udp_flood
from gen_icmp_flood import run_attack as run_icmp_flood
# Assuming a similar structure for the advanced attacks script
from gen_advanced_adversarial_ddos_attacks import run_attack as run_adv_ddos

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False # Prevent messages from being passed to the root logger

# File handler
file_handler = logging.FileHandler('test.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# --- Configuration ---
BASE_DIR = Path(__file__).parent.resolve()
SRC_DIR = BASE_DIR / "src"
ATTACKS_DIR = SRC_DIR / "attacks"
UTILS_DIR = SRC_DIR / "utils"
OUTPUT_DIR = BASE_DIR / "output"
PCAP_FILE = OUTPUT_DIR / "capture.pcap"
OUTPUT_CSV_FILE = OUTPUT_DIR / "packet_features.csv"
OUTPUT_LABELED_CSV_FILE = OUTPUT_DIR / "labeled_packet_features.csv"
RYU_CONTROLLER_APP = SRC_DIR / "controller" / "ryu_controller_app.py" # Assuming this is the app

# Host IPs from scenario.md
HOST_IPS = {
    "h1": "10.0.0.1", "h2": "10.0.0.2", "h3": "10.0.0.3",
    "h4": "10.0.0.4", "h5": "10.0.0.5", "h6": "10.0.0.6"
}

def verify_tools():
    """Verify that all required command-line tools are installed."""
    logger.info("Verifying required tools...")
    # Log tshark version
    try:
        tshark_output = subprocess.check_output(["tshark", "--version"], universal_newlines=True, stderr=subprocess.STDOUT)
        version_line = tshark_output.split('\n')[0] if tshark_output else 'unknown'
        logger.info(f"TShark version: {version_line}")
    except Exception as e:
        logger.error(f"Could not get TShark version: {e}")
        logger.error("Please install Wireshark/tshark package.")
        sys.exit(1)

    required_tools = ["ryu-manager", "mn", "tshark"]
    for tool in required_tools:
        if not shutil.which(tool):
            logger.error(f"Tool not found: '{tool}'. Please install it manually.")
            if tool == 'tshark':
                logger.error("On Ubuntu/Debian: sudo apt-get install tshark")
                logger.error("On CentOS/RHEL: sudo yum install wireshark")
            sys.exit(1)
            sys.exit(1)
    logger.info("All required tools are available.")

def start_controller():
    """Start the Ryu SDN controller as a background process."""
    if not RYU_CONTROLLER_APP.exists():
        logger.error(f"Ryu controller application not found at: {RYU_CONTROLLER_APP}")
        sys.exit(1)
        
    logger.info("Starting Ryu SDN controller...")
    ryu_log_file = OUTPUT_DIR / "ryu.log"
    ryu_cmd = [
        "ryu-manager",
        str(RYU_CONTROLLER_APP)
    ]
    
    with open(ryu_log_file, 'wb') as log_out:
        process = subprocess.Popen(ryu_cmd, stdout=log_out, stderr=log_out)
    
    logger.info(f"Ryu controller started with PID: {process.pid}. See {ryu_log_file} for logs.")
    return process

def check_controller_health(port=6653, timeout=30):
    """Check if the controller is listening on its port."""
    logger.info(f"Checking for controller on port {port} (timeout: {timeout}s)...")
    for _ in range(timeout):
        try:
            # Use ss (from iproute2) as it is more modern than netstat
            result = subprocess.run(["ss", "-ltn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
            if f":{port}" in result.stdout:
                logger.info("Controller is up and listening.")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # Fallback to netstat if ss is not available
            try:
                result = subprocess.run(["netstat", "-ltn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
                if f":{port}" in result.stdout:
                    logger.info("Controller is up and listening.")
                    return True
            except Exception:
                logger.warning("Could not check controller port. Assuming it will be ready.", exc_info=True)
                return True # Fail open if we can't even check
        time.sleep(1)
    logger.error(f"Controller did not become available on port {port} within {timeout} seconds.")
    return False

class ScenarioTopo(Topo):
    """Custom topology for the dataset generation scenario."""
    def build(self, **_opts):
        # Add 1 switch
        s1 = self.addSwitch("s1", cls=OVSKernelSwitch, protocols="OpenFlow13")

        # Add 6 hosts
        for i in range(1, 7):
            h = self.addHost(f"h{i}", ip=HOST_IPS[f"h{i}"] + "/24")
            self.addLink(h, s1)

def setup_mininet(controller_ip='127.0.0.1', controller_port=6653):
    """Create and start the Mininet network based on ScenarioTopo."""
    logger.info("Setting up Mininet topology...")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure Mininet logging to file
    mininet_log_file = OUTPUT_DIR / "mininet.log"
    
    # Clear existing handlers
    mininet_logger = logging.getLogger('mininet')
    mininet_logger.propagate = False
    mininet_logger.handlers = []
    
    # Set up file handler
    file_handler = logging.FileHandler(mininet_log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    mininet_logger.addHandler(file_handler)
    mininet_logger.addHandler(console_handler)
    mininet_logger.setLevel(logging.DEBUG)
    
    # Also set the root logger to ensure all mininet logs are captured
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    
    # Log Mininet version for debugging
    try:
        mn_version = subprocess.check_output(["mn", "--version"], universal_newlines=True).strip()
        logger.info(f"Mininet version: {mn_version}")
    except Exception as e:
        logger.warning(f"Could not get Mininet version: {e}")

    # Create a Mininet instance
    topo = ScenarioTopo()
    net = Mininet(
        topo=topo,
        controller=None, # We will add the remote controller manually
        switch=OVSKernelSwitch,
        autoSetMacs=True,
        autoStaticArp=True,
        build=False,
        cleanup=True
    )

    # Add the remote Ryu controller
    logger.info(f"Connecting to remote controller at {controller_ip}:{controller_port}")
    controller = RemoteController(
        'c0',
        ip=controller_ip,
        port=controller_port
    )
    net.addController(controller)

    # Build and start the network
    net.build()
    net.start()

    logger.info("Mininet network started successfully.")
    return net

def run_mininet_pingall_test(net):
    """Run Mininet's pingall test to verify basic connectivity."""
    logger.info("Running Mininet pingall test...")
    # Capture stdout to avoid cluttering the console, but still log the result
    time.sleep(5) # Give the controller some time to set up flows
    # Temporarily redirect stdout to suppress Mininet's verbose pingall output
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    # Temporarily set Mininet log level to suppress verbose output
    original_mininet_log_level = logging.getLogger('mininet.log').level
    logging.getLogger('mininet.log').setLevel(logging.ERROR)

    try:
        result = net.pingAll()
    finally:
        sys.stdout = original_stdout # Restore stdout
        logging.getLogger('mininet.log').setLevel(original_mininet_log_level) # Restore Mininet log level

    if result == 0.0: # 0.0 means 0% packet loss, which is success
        logger.info(f"Mininet pingall test completed successfully. Packet loss: {result}%")
    else:
        logger.error(f"Mininet pingall test failed. Packet loss: {result}%")

def start_capture(net, outfile):
    """Start improved tcpdump on a host with better timestamp handling."""
    return improve_capture_reliability(net, outfile)

def run_benign_traffic(net, duration):
    logger.info(f"Starting benign traffic for {duration} seconds...")
    h3 = net.get('h3')
    h5 = net.get('h5')
    h3_ip = HOST_IPS["h3"]
    h5_ip = HOST_IPS["h5"]
    h3_intf = h3.intfNames()[0] # Get the interface name of h3
    end_time = time.time() + duration
    
    traffic_count = 0
    while time.time() < end_time:
        # ICMP traffic (using Mininet's ping command)
        h3.cmd(f'ping -c 1 {h5_ip} > /dev/null')
        h5.cmd(f'ping -c 1 {h3_ip} > /dev/null')

        # Scapy commands to be executed within h3's namespace
        scapy_base_cmd = "from scapy.all import Ether, IP, TCP, UDP, Raw, RandShort, sendp;"

        # TCP traffic (h3 to h5, port 12345)
        tcp_scapy_cmd = f"tcp_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=12345, flags=\"PA\")/Raw(load=\"TCP benign traffic {traffic_count}\"); sendp(tcp_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{tcp_scapy_cmd}"')

        # UDP traffic (h3 to h5, port 12346)
        udp_scapy_cmd = f"udp_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/UDP(sport=RandShort(), dport=12346)/Raw(load=\"UDP benign traffic {traffic_count}\"); sendp(udp_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{udp_scapy_cmd}"')

        # Telnet traffic (h3 to h5, port 23)
        telnet_scapy_cmd = f"telnet_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=23, flags=\"PA\")/Raw(load=\"Telnet benign traffic {traffic_count}\"); sendp(telnet_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{telnet_scapy_cmd}"')

        # SSH traffic (h3 to h5, port 22)
        ssh_scapy_cmd = f"ssh_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=22, flags=\"PA\")/Raw(load=\"SSH benign traffic {traffic_count}\"); sendp(ssh_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{ssh_scapy_cmd}"')

        # FTP traffic (h3 to h5, port 21)
        ftp_scapy_cmd = f"ftp_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=21, flags=\"PA\")/Raw(load=\"FTP benign traffic {traffic_count}\"); sendp(ftp_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{ftp_scapy_cmd}"')

        # HTTP traffic (h3 to h5, port 80)
        http_scapy_cmd = f"http_packet = Ether()/IP(src='{h3_ip}', dst='{h5_ip}')/TCP(sport=RandShort(), dport=80, flags=\"PA\")/Raw(load=b'GET / HTTP/1.1\nHost: {h5_ip}\nUser-Agent: ScapyBenignTraffic\nConnection: close\n\n'); sendp(http_packet, iface='{h3_intf}', verbose=0)"
        h3.cmd(f'python3 -c "{scapy_base_cmd}{http_scapy_cmd}"')
        
        traffic_count += 1
        time.sleep(1) # Send traffic every second
    
    logger.info("Benign traffic finished.")
    # No netcat processes to kill

def stop_capture(process):
    """Stop the tcpdump process."""
    logger.info(f"Stopping packet capture (PID: {process.pid})...")
    try:
        process.send_signal(signal.SIGINT)
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        logger.warning(f"tcpdump (PID: {process.pid}) did not terminate gracefully. Forcing kill.")
        process.kill()
    logger.info("Packet capture stopped.")

def run_traffic_scenario(net):
    """Orchestrate the traffic generation phases."""
    if not net:
        logger.error("Mininet network object is not valid. Aborting traffic scenario.")
        return

    logger.info("Starting traffic generation scenario...")
    capture_proc = start_capture(net, PCAP_FILE)
    
    # Give capture a moment to start
    time.sleep(2)

    try:
        # --- Phase 1: Initialization (5s) ---
        logger.info("Phase 1: Initialization (5s)...")
        time.sleep(5)

        # --- Phase 2: Normal Traffic (5s) ---
        logger.info("Phase 2: Normal Traffic (5s)...")
        run_benign_traffic(net, 5)

        # --- Phase 3.1: Traditional DDoS Attacks ---
        logger.info("Phase 3.1: Traditional DDoS Attacks (15s total)...")
        h1, h2, h4, h6 = net.get('h1', 'h2', 'h4', 'h6')

        logger.info("Attack: SYN Flood (5s) | h1 -> h6")
        run_syn_flood(h1, HOST_IPS['h6'], duration=5)
        
        logger.info("Attack: UDP Flood (5s) | h2 -> h4")
        run_udp_flood(h2, HOST_IPS['h4'], duration=5)

        logger.info("Attack: ICMP Flood (5s) | h2 -> h4")
        run_icmp_flood(h2, HOST_IPS['h4'], duration=5)

        # --- Phase 3.2: Adversarial DDoS Attacks (15s total) ---
        logger.info("Phase 3.2: Adversarial DDoS Attacks (15s total)...")

        logger.info("Attack: Adversarial TCP State Exhaustion (5s) | h2 -> h6")
        run_adv_ddos(h2, HOST_IPS['h6'], duration=5, attack_variant="ad_syn")

        logger.info("Attack: Adversarial Application Layer (5s) | h2 -> h6")
        run_adv_ddos(h2, HOST_IPS['h6'], duration=5, attack_variant="ad_udp")

        logger.info("Attack: Adversarial Multi-Vector (5s) | h2 -> h6")
        run_adv_ddos(h2, HOST_IPS['h6'], duration=5, attack_variant="multivector")

        # --- Phase 4: Cooldown (5s) ---
        logger.info("Phase 4: Cooldown (5s)...")
        time.sleep(5)

    finally:
        stop_capture(capture_proc)
        logger.info("Traffic generation scenario finished.")


def cleanup(controller_proc, mininet_running):
    """Clean up all running processes and network configurations."""
    logger.info("Cleaning up resources...")
    if controller_proc:
        logger.info(f"Terminating Ryu controller (PID: {controller_proc.pid})...")
        controller_proc.terminate()
        controller_proc.wait()

    # Clean up Mininet
    logger.info("Cleaning up Mininet environment...")
    cleanup_cmd = ["mn", "-c"]
    subprocess.run(cleanup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info("Cleanup complete.")

def cleanup(controller_proc, mininet_running):
    """Clean up all running processes and network configurations."""
    logger.info("Cleaning up resources...")
    if controller_proc:
        logger.info(f"Terminating Ryu controller (PID: {controller_proc.pid})...")
        controller_proc.terminate()
        controller_proc.wait()

    # Clean up Mininet
    logger.info("Cleaning up Mininet environment...")
    cleanup_cmd = ["mn", "-c"]
    subprocess.run(cleanup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info("Cleanup complete.")

def verify_labels_in_csv(csv_file_path, label_timeline):
    """
    Verifies the presence and validity of labels in the generated CSV file.
    """
    logger.info(f"Verifying labels in {csv_file_path}...")
    try:
        import pandas as pd
        df = pd.read_csv(csv_file_path)

        if df.empty:
            logger.error("CSV file is empty. No labels to verify.")
            return False

        # Expected labels from the timeline
        expected_multi_labels = set(entry['label'] for entry in label_timeline)
        expected_multi_labels.discard('normal') # Normal is handled separately for binary check

        # Actual labels in the CSV
        actual_multi_labels = set(df['Label_multi'].unique())

        # Check if all expected attack labels are present
        missing_labels = expected_multi_labels - actual_multi_labels
        if missing_labels:
            logger.error(f"Missing expected attack labels in CSV: {missing_labels}")
            return False
        else:
            logger.info("All expected attack labels are present in CSV.")

        # Verify Label_binary consistency
        # All attack labels should have Label_binary = 1
        attack_labels_in_df = [label for label in actual_multi_labels if label != 'normal']
        for label in attack_labels_in_df:
            if not (df[df['Label_multi'] == label]['Label_binary'] == 1).all():
                logger.error(f"Inconsistent Label_binary for attack label '{label}'. Expected 1.")
                return False

        # All normal labels should have Label_binary = 0
        if 'normal' in actual_multi_labels:
            if not (df[df['Label_multi'] == 'normal']['Label_binary'] == 0).all():
                logger.error("Inconsistent Label_binary for 'normal' label. Expected 0.")
                return False

        logger.info("Label_binary consistency check passed.")
        logger.info("CSV label verification complete and successful.")
        return True

    except FileNotFoundError:
        logger.error(f"CSV file not found at {csv_file_path}")
        return False
    except Exception as e:
        logger.error(f"Error during CSV label verification: {e}", exc_info=True)
        return False

def main():
    """Main entry point for the pcap generation framework."""
    parser = argparse.ArgumentParser(description="AdDDoSDN PCAP Generation Framework")
    # Add any arguments if needed, e.g., --duration-multiplier
    args = parser.parse_args()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Clean up any previous Mininet instances
    logger.info("Cleaning up any previous Mininet instances...")
    subprocess.run(["mn", "-c"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info("Mininet cleanup complete.")

    verify_tools()

    controller_process = None
    mininet_network = None
    
    try:
        # 1. Start Controller
        controller_process = start_controller()
        if not check_controller_health():
            raise RuntimeError("Controller health check failed. Aborting.")

        # Test /hello endpoint
        logger.info("Testing /hello endpoint...")
        try:
            import requests
            response = requests.get("http://localhost:8080/hello")
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            if response.json() == {"message": "Hello from Ryu Controller!"}:
                logger.info("Test /hello endpoint: PASSED")
            else:
                logger.error(f"Test /hello endpoint: FAILED - Unexpected response: {response.json()}")
                raise RuntimeError("Hello endpoint test failed.")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Test /hello endpoint: FAILED - Could not connect to controller API: {e}")
            raise RuntimeError("Hello endpoint test failed due to connection error.")
        except Exception as e:
            logger.error(f"Test /hello endpoint: FAILED - An unexpected error occurred: {e}")
            raise RuntimeError("Hello endpoint test failed.")

        # 2. Setup Mininet
        mininet_network = setup_mininet()

        # Run pingall test
        run_mininet_pingall_test(mininet_network)

        # 3. Run Scenario
        scenario_start_time = time.time()
        run_traffic_scenario(mininet_network)

        logger.info("PCAP generation complete.")
        logger.info(f"Output file located at: {PCAP_FILE}")

        # Verify PCAP integrity before processing
        integrity_results = verify_pcap_integrity(PCAP_FILE)
        if not integrity_results['valid']:
            logger.error(f"PCAP integrity check failed: {integrity_results['error']}")
            # Continue with processing but log the warning
            logger.warning("Continuing with PCAP processing despite integrity issues...")
        else:
            logger.info(f"PCAP integrity check passed: {integrity_results['total_packets']} packets")
            if integrity_results['corruption_rate'] > 0:
                logger.warning(f"Timestamp corruption detected: {integrity_results['corruption_rate']:.2f}%")

        # Get the timestamp of the first packet in the PCAP for timeline synchronization
        try:
            # Use the enhanced timestamp validation
            corrected_packets, stats = validate_and_fix_pcap_timestamps(PCAP_FILE)
            
            if stats['corrupted_packets'] > 0:
                logger.warning(f"Fixed {stats['corrupted_packets']} corrupted timestamps")
            
            # Use the first valid timestamp
            pcap_start_time = stats['baseline_time']
            logger.info(f"Using baseline timestamp for labeling: {pcap_start_time}")
            
        except Exception as e:
            logger.error(f"Could not process PCAP timestamps: {e}. Using scenario_start_time for labeling.")
            pcap_start_time = scenario_start_time

        # 4. Process PCAP to CSV and add labels with enhanced processing
        logger.info("Processing PCAP to CSV and adding labels...")
        
        # Define the label timeline (same as before)
        current_time_offset = 0
        label_timeline = []

        # Phase 1: Initialization (5s)
        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'normal'
        })
        current_time_offset += 5

        # Phase 2: Normal Traffic (5s)
        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'normal'
        })
        current_time_offset += 5

        # Phase 3.1: Traditional DDoS Attacks (15s total)
        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'syn_flood'
        })
        current_time_offset += 5

        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'udp_flood'
        })
        current_time_offset += 5

        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'icmp_flood'
        })
        current_time_offset += 5

        # Phase 3.2: Adversarial DDoS Attacks (15s total)
        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'ad_syn'
        })
        current_time_offset += 5

        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'ad_udp'
        })
        current_time_offset += 5

        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'multivector'
        })
        current_time_offset += 5

        # Phase 4: Cooldown (5s)
        label_timeline.append({
            'start_time': pcap_start_time + current_time_offset,
            'end_time': pcap_start_time + current_time_offset + 5,
            'label': 'normal'
        })

        # Use enhanced processing with timestamp validation
        enhanced_process_pcap_to_csv(
            str(PCAP_FILE), 
            str(OUTPUT_LABELED_CSV_FILE), 
            label_timeline,
            validate_timestamps=True
        )
        
        logger.info(f"Labeled CSV generated at: {OUTPUT_LABELED_CSV_FILE}")

        # 5. Verify labels in CSV
        verify_labels_in_csv(OUTPUT_LABELED_CSV_FILE, label_timeline)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # 6. Cleanup
        cleanup(controller_process, mininet_network is not None)

if __name__ == "__main__":
    # Check for root privileges, required by Mininet
    if os.geteuid() != 0:
        logger.error("This script must be run as root for Mininet.")
        sys.exit(1)
    main()

def verify_labels_in_csv(csv_file_path, label_timeline):
    """
    Verifies the presence and validity of labels in the generated CSV file.
    """
    logger.info(f"Verifying labels in {csv_file_path}...")
    try:
        import pandas as pd
        df = pd.read_csv(csv_file_path)

        if df.empty:
            logger.error("CSV file is empty. No labels to verify.")
            return False

        # Expected labels from the timeline
        expected_multi_labels = set(entry['label'] for entry in label_timeline)
        expected_multi_labels.discard('normal') # Normal is handled separately for binary check

        # Actual labels in the CSV
        actual_multi_labels = set(df['Label_multi'].unique())

        # Check if all expected attack labels are present
        missing_labels = expected_multi_labels - actual_multi_labels
        if missing_labels:
            logger.error(f"Missing expected attack labels in CSV: {missing_labels}")
            return False
        else:
            logger.info("All expected attack labels are present in CSV.")

        # Verify Label_binary consistency
        # All attack labels should have Label_binary = 1
        attack_labels_in_df = [label for label in actual_multi_labels if label != 'normal']
        for label in attack_labels_in_df:
            if not (df[df['Label_multi'] == label]['Label_binary'] == 1).all():
                logger.error(f"Inconsistent Label_binary for attack label '{label}'. Expected 1.")
                return False

        # All normal labels should have Label_binary = 0
        if 'normal' in actual_multi_labels:
            if not (df[df['Label_multi'] == 'normal']['Label_binary'] == 0).all():
                logger.error("Inconsistent Label_binary for 'normal' label. Expected 0.")
                return False

        logger.info("Label_binary consistency check passed.")
        logger.info("CSV label verification complete and successful.")
        return True

    except FileNotFoundError:
        logger.error(f"CSV file not found at {csv_file_path}")
        return False
    except Exception as e:
        logger.error(f"Error during CSV label verification: {e}", exc_info=True)
        return False