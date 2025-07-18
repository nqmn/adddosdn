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
import threading
from pathlib import Path
import shutil
from scapy.all import rdpcap
from src.gen_benign_traffic import run_benign_traffic
import requests # New: For making HTTP requests to the Ryu controller
import pandas as pd # New: For data manipulation and CSV writing
from datetime import datetime # New: For timestamping flow data
import json # New: For reading config.json
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

# Import standardized logging
from src.utils.logger import get_main_logger, ConsoleOutput, initialize_logging, print_dataset_summary
from src.utils.timeline_analysis import analyze_dataset_timeline, print_detailed_timeline_report

# Suppress Scapy warnings


from src.utils.process_pcap_to_csv import process_pcap_to_csv
from src.utils.enhanced_pcap_processing import (
    validate_and_fix_pcap_timestamps,
    enhanced_process_pcap_to_csv,
    improve_capture_reliability,
    verify_pcap_integrity,
    analyze_pcap_for_tcp_issues,
    analyze_inter_packet_arrival_time
)
from src.utils.process_pcap_to_csv import _get_label_for_timestamp # New: For labeling flow data

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

# --- Configuration ---
BASE_DIR = Path(__file__).parent.resolve()
SRC_DIR = BASE_DIR / "src"
ATTACKS_DIR = SRC_DIR / "attacks"
UTILS_DIR = SRC_DIR / "utils"
OUTPUT_DIR = BASE_DIR / "main_output"
PCAP_FILE_NORMAL = OUTPUT_DIR / "normal.pcap"
PCAP_FILE_SYN_FLOOD = OUTPUT_DIR / "syn_flood.pcap"
PCAP_FILE_UDP_FLOOD = OUTPUT_DIR / "udp_flood.pcap"
PCAP_FILE_ICMP_FLOOD = OUTPUT_DIR / "icmp_flood.pcap"
PCAP_FILE_AD_SYN = OUTPUT_DIR / "ad_syn.pcap"
PCAP_FILE_AD_UDP = OUTPUT_DIR / "ad_udp.pcap"
PCAP_FILE_AD_SLOW = OUTPUT_DIR / "ad_slow.pcap"
PCAP_FILE_H6_SLOW_READ = OUTPUT_DIR / "h6_slow_read.pcap" # New: PCAP for h6 during slow read attack
OUTPUT_CSV_FILE = OUTPUT_DIR / "packet_features.csv"

OUTPUT_FLOW_CSV_FILE = OUTPUT_DIR / "flow_features.csv" # New: Flow-level dataset output
RYU_CONTROLLER_APP = SRC_DIR / "controller" / "ryu_controller_app.py" # Assuming this is the app

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False # Prevent messages from being passed to the root logger

# Ensure output directory exists before setting up file handlers
OUTPUT_DIR.mkdir(exist_ok=True)

# File handler
file_handler = logging.FileHandler(OUTPUT_DIR / 'main.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Configure a dedicated logger for attack details
attack_logger = logging.getLogger('attack_logger')
attack_logger.setLevel(logging.DEBUG)
attack_logger.propagate = False # Prevent messages from being passed to the root logger

# File handler for attack.log
attack_log_file_handler = logging.FileHandler(OUTPUT_DIR / 'attack.log')
attack_log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
attack_logger.addHandler(attack_log_file_handler)

# Console handler for attack_logger with custom filter
class AttackConsoleFilter(logging.Filter):
    def filter(self, record):
        # Hide slowhttptest termination messages from console
        message = record.getMessage()
        if any(phrase in message for phrase in [
            "did not terminate gracefully, forcing termination",
            "slowhttptest process exited with non-zero code: -15"
        ]):
            return False
        return True

attack_console_handler = logging.StreamHandler()
attack_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
attack_console_handler.setLevel(logging.WARNING)
attack_console_handler.addFilter(AttackConsoleFilter())
attack_logger.addHandler(attack_console_handler)

# Suppress debug messages from requests/urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)

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

    required_tools = ["ryu-manager", "mn", "tshark", "slowhttptest"]
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
    
        logger.info(f"Ryu controller started with PID: {process.pid}. See {ryu_log_file.relative_to(BASE_DIR)} for logs.")
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
    root_logger.setLevel(logging.INFO)
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

def start_capture(net, outfile, host=None):
    """Start improved tcpdump on a host with better timestamp handling."""
    return improve_capture_reliability(net, outfile, host=host)



def parse_flow_match_actions(match_str, actions_str):
    """
    Parses the match and actions strings from Ryu flow stats to extract specific fields.
    """
    in_port = None
    eth_src = None
    eth_dst = None
    out_port = None

    # Parse match string
    match_pattern = re.compile(r"'in_port': (\d+).*'eth_src': '([0-9a-fA-F:]+)'.*'eth_dst': '([0-9a-fA-F:]+)'")
    match_match = match_pattern.search(match_str)
    if match_match:
        in_port = int(match_match.group(1))
        eth_src = match_match.group(2)
        eth_dst = match_match.group(3)

    # Parse actions string
    actions_pattern = re.compile(r"port=(\d+)")
    actions_match = actions_pattern.search(actions_str)
    if actions_match:
        out_port = int(actions_match.group(1))

    return in_port, eth_src, eth_dst, out_port

def update_flow_timeline(flow_label_timeline, label, start_time=None):
    """
    Update the flow label timeline with current phase information.
    This creates a real-time timeline that matches actual execution.
    """
    if start_time is None:
        start_time = time.time()
    
    # End previous phase if exists
    if flow_label_timeline and 'end_time' not in flow_label_timeline[-1]:
        flow_label_timeline[-1]['end_time'] = start_time
    
    # Start new phase
    flow_label_timeline.append({
        'start_time': start_time,
        'label': label
    })
    logger.info(f"Timeline updated: {label} phase started at {start_time}")

def collect_flow_stats(duration, output_file, flow_label_timeline, stop_event=None, controller_ip='127.0.0.1', controller_port=8080):
    """
    Collects flow statistics from the Ryu controller's REST API periodically
    and saves them to a CSV file.
    """
    logger.info(f"Starting flow statistics collection for {duration} seconds...")
    flow_data = []
    start_time = time.time()
    api_url = f"http://{controller_ip}:{controller_port}/flows"

    while time.time() - start_time < duration:
        # Check if we should stop early
        if stop_event and stop_event.is_set():
            logger.info("Flow collection received stop signal, ending gracefully.")
            break
            
        try:
            response = requests.get(api_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            flows = response.json()
            
            timestamp = datetime.now().timestamp() # Use timestamp for labeling
            for flow in flows:
                in_port, eth_src, eth_dst, out_port = parse_flow_match_actions(flow.get('match', ''), flow.get('actions', ''))

                # Determine labels based on the current timestamp
                label_multi = _get_label_for_timestamp(timestamp, flow_label_timeline)
                label_binary = 1 if label_multi != 'normal' else 0

                flow_entry = {
                    'timestamp': timestamp,
                    'switch_id': flow.get('switch_id'),
                    'table_id': flow.get('table_id'),
                    'cookie': flow.get('cookie'),
                    'priority': flow.get('priority'),
                    'in_port': in_port,
                    'eth_src': eth_src,
                    'eth_dst': eth_dst,
                    'out_port': out_port,
                    'packet_count': flow.get('packet_count'),
                    'byte_count': flow.get('byte_count'),
                    'duration_sec': flow.get('duration_sec'),
                    'duration_nsec': flow.get('duration_nsec'),
                    'avg_pkt_size': 0,
                    'pkt_rate': 0,
                    'byte_rate': 0,
                    'Label_multi': label_multi,
                    'Label_binary': label_binary
                }
                
                duration_sec = flow.get('duration_sec', 0)
                duration_nsec = flow.get('duration_nsec', 0)
                packet_count = flow.get('packet_count', 0)
                byte_count = flow.get('byte_count', 0)

                total_duration = duration_sec + (duration_nsec / 1_000_000_000)

                if packet_count > 0:
                    flow_entry['avg_pkt_size'] = byte_count / packet_count
                if total_duration > 0:
                    flow_entry['pkt_rate'] = packet_count / total_duration
                    flow_entry['byte_rate'] = byte_count / total_duration
                
                flow_data.append(flow_entry)
            time.sleep(1) # Collect every second
        except requests.exceptions.RequestException as e:
            # Check if we should stop early
            if stop_event and stop_event.is_set():
                logger.info("Flow collection received stop signal during error handling, ending gracefully.")
                break
            logger.error(f"Error collecting flow stats: {e}")
            time.sleep(5) # Wait longer on error before retrying
    
    # Close the final timeline entry
    if flow_label_timeline and 'end_time' not in flow_label_timeline[-1]:
        flow_label_timeline[-1]['end_time'] = time.time()
        logger.info("Flow timeline collection completed.")
    
    if flow_data:
        df = pd.DataFrame(flow_data)
        # Define the desired order of columns
        ordered_columns = [
            'timestamp', 'switch_id', 'table_id', 'cookie', 'priority',
            'in_port', 'eth_src', 'eth_dst', 'out_port',
            'packet_count', 'byte_count', 'duration_sec', 'duration_nsec',
            'avg_pkt_size', 'pkt_rate', 'byte_rate',
            'Label_multi', 'Label_binary'
        ]
        # Reindex the DataFrame to ensure the columns are in the desired order
        df = df.reindex(columns=ordered_columns)
        df.to_csv(output_file, index=False)
        logger.info(f"Flow statistics saved to {output_file.relative_to(BASE_DIR)}")
    else:
        logger.warning("No flow data collected.")

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

def run_traffic_scenario(net, flow_label_timeline, scenario_durations, total_scenario_duration, config_file_path=None):
    """Orchestrate the traffic generation phases."""
    if not net:
        logger.error("Mininet network object is not valid. Aborting traffic scenario.")
        return

    logger.info("Starting traffic generation scenario...")
    
    # Track timing for each phase
    phase_timings = {}
    scenario_start_time = time.time()

    capture_procs = {} # Dictionary to hold all capture processes
    flow_collector_thread = None # Thread for collecting flow stats
    flow_stop_event = threading.Event() # Event to signal flow collection to stop

    try:
        # --- Phase 1: Initialization ---
        phase_start = time.time()
        logger.info(f"Phase 1: Initialization ({scenario_durations['initialization']}s)...")
        time.sleep(scenario_durations['initialization'])
        phase_timings['initialization'] = time.time() - phase_start

        # Start flow collection in a separate thread - SYNCHRONIZED with packet collection
        flow_collector_thread = threading.Thread(
            target=collect_flow_stats,
            args=(total_scenario_duration, OUTPUT_FLOW_CSV_FILE, flow_label_timeline, flow_stop_event)
        )
        flow_collector_thread.daemon = False # Don't allow main thread to exit before this thread finishes
        flow_collector_thread.start()
        logger.info("Flow statistics collection started in background.")

        # --- Phase 2: Normal Traffic ---
        phase_start = time.time()
        logger.info(f"Phase 2: Normal Traffic ({scenario_durations['normal_traffic']}s)...")
        update_flow_timeline(flow_label_timeline, 'normal')  # Update timeline dynamically
        capture_procs['normal'] = start_capture(net, PCAP_FILE_NORMAL)
        time.sleep(2) # Give capture a moment to start
        run_benign_traffic(net, scenario_durations['normal_traffic'], OUTPUT_DIR, HOST_IPS)
        stop_capture(capture_procs['normal'])
        phase_timings['normal_traffic'] = time.time() - phase_start

        # --- Phase 3.1: Enhanced Traditional DDoS Attacks ---
        logger.info("Phase 3.1: Enhanced Traditional DDoS Attacks...")
        h1, h2, h4, h6 = net.get('h1', 'h2', 'h4', 'h6')

        phase_start = time.time()
        attack_logger.info(f"Attack: Enhanced SYN Flood ({scenario_durations['syn_flood']}s) | h1 -> h6")
        update_flow_timeline(flow_label_timeline, 'syn_flood')  # Update timeline dynamically
        capture_procs['syn_flood'] = start_capture(net, PCAP_FILE_SYN_FLOOD)
        time.sleep(2)
        attack_proc_syn = run_syn_flood(h1, HOST_IPS['h6'], duration=scenario_durations['syn_flood'])
        attack_proc_syn.wait() # Wait for the process to terminate
        stop_capture(capture_procs['syn_flood'])
        phase_timings['syn_flood'] = time.time() - phase_start
        attack_logger.info("Attack: Enhanced SYN Flood completed.")

        phase_start = time.time()
        attack_logger.info(f"Attack: Enhanced UDP Flood ({scenario_durations['udp_flood']}s) | h2 -> h4")
        update_flow_timeline(flow_label_timeline, 'udp_flood')  # Update timeline dynamically
        capture_procs['udp_flood'] = start_capture(net, PCAP_FILE_UDP_FLOOD)
        time.sleep(5)
        attack_proc_udp = run_udp_flood(h2, HOST_IPS['h4'], duration=scenario_durations['udp_flood'])
        attack_proc_udp.wait() # Wait for the process to terminate
        stop_capture(capture_procs['udp_flood'])
        phase_timings['udp_flood'] = time.time() - phase_start
        attack_logger.info("Attack: Enhanced UDP Flood completed.")

        phase_start = time.time()
        attack_logger.info(f"Attack: Enhanced ICMP Flood ({scenario_durations['icmp_flood']}s) | h2 -> h4")
        update_flow_timeline(flow_label_timeline, 'icmp_flood')  # Update timeline dynamically
        capture_procs['icmp_flood'] = start_capture(net, PCAP_FILE_ICMP_FLOOD)
        time.sleep(2)
        attack_proc_icmp = run_icmp_flood(h2, HOST_IPS['h4'], duration=scenario_durations['icmp_flood'])
        attack_proc_icmp.wait() # Wait for the process to terminate
        stop_capture(capture_procs['icmp_flood'])
        phase_timings['icmp_flood'] = time.time() - phase_start
        attack_logger.info("Attack: Enhanced ICMP Flood completed.")

        # --- Phase 3.2: Adversarial DDoS Attacks ---
        logger.info("Phase 3.2: Adversarial DDoS Attacks...")

        phase_start = time.time()
        attack_logger.info(f"Attack: Adversarial TCP State Exhaustion ({scenario_durations['ad_syn']}s) | h2 -> h6")
        update_flow_timeline(flow_label_timeline, 'ad_syn')  # Update timeline dynamically
        capture_procs['ad_syn'] = start_capture(net, PCAP_FILE_AD_SYN)
        time.sleep(2)
        run_adv_ddos(h2, HOST_IPS['h6'], duration=scenario_durations['ad_syn'], attack_variant="ad_syn")
        stop_capture(capture_procs['ad_syn'])
        phase_timings['ad_syn'] = time.time() - phase_start

        phase_start = time.time()
        attack_logger.info(f"Attack: Adversarial Application Layer ({scenario_durations['ad_udp']}s) | h2 -> h6")
        update_flow_timeline(flow_label_timeline, 'ad_udp')  # Update timeline dynamically
        capture_procs['ad_udp'] = start_capture(net, PCAP_FILE_AD_UDP)
        time.sleep(2)
        run_adv_ddos(h2, HOST_IPS['h6'], duration=scenario_durations['ad_udp'], attack_variant="ad_udp")
        stop_capture(capture_procs['ad_udp'])
        phase_timings['ad_udp'] = time.time() - phase_start

        phase_start = time.time()
        attack_logger.info(f"Attack: Adversarial Slow Read ({scenario_durations['ad_slow']}s) | h2 -> h6")
        update_flow_timeline(flow_label_timeline, 'ad_slow')  # Update timeline dynamically
        # Start capture on h6 specifically for slow read attack
        h6 = net.get('h6')
        capture_procs['h6_slow_read'] = start_capture(net, PCAP_FILE_H6_SLOW_READ, host=h6)
        capture_procs['ad_slow'] = start_capture(net, PCAP_FILE_AD_SLOW)
        time.sleep(2)
        
        # No HTTP server needed - slowhttptest generates adversarial patterns regardless
        # The h6_slow_read.pcap will capture all traffic on h6 during the attack
        logger.info("Proceeding with adversarial slow attack (no HTTP server required)")
        logger.info("Attack traffic will be captured via h6_slow_read.pcap and ad_slow.pcap")
        
        http_server_proc = None  # Keep variable for cleanup compatibility

        attack_proc_ad_slow = run_adv_ddos(h2, HOST_IPS['h6'], duration=scenario_durations['ad_slow'], attack_variant="slow_read", output_dir=OUTPUT_DIR)
        stop_capture(capture_procs['ad_slow'])
        stop_capture(capture_procs['h6_slow_read']) # Stop h6 specific capture
        phase_timings['ad_slow'] = time.time() - phase_start
        attack_logger.info("Attack: Adversarial Slow Read completed.")

        # Analyze h6 PCAP for TCP issues
        if PCAP_FILE_H6_SLOW_READ.exists():
            logger.info(f"Analyzing {PCAP_FILE_H6_SLOW_READ.relative_to(BASE_DIR)} for TCP issues...")
            tcp_analysis_results = analyze_pcap_for_tcp_issues(PCAP_FILE_H6_SLOW_READ)
            logger.info(f"TCP Analysis on h6 PCAP: RST Count = {tcp_analysis_results.get('rst_count', 0)}, Retransmission Count = {tcp_analysis_results.get('retransmission_count', 0)}")

            # Analyze inter-packet arrival times
            ipt_analysis_results = analyze_inter_packet_arrival_time(PCAP_FILE_H6_SLOW_READ)
            if ipt_analysis_results and not ipt_analysis_results.get('error'):
                logger.info(f"Inter-Packet Arrival Time (h6 PCAP): Mean = {ipt_analysis_results['mean']:.4f}s, Median = {ipt_analysis_results['median']:.4f}s, Std Dev = {ipt_analysis_results['std_dev']:.4f}s")
            else:
                logger.warning(f"Inter-Packet Arrival Time analysis failed for h6 PCAP: {ipt_analysis_results.get('error', 'Unknown error')}")
        else:
            logger.warning(f"h6 slow read PCAP file not found: {PCAP_FILE_H6_SLOW_READ.relative_to(BASE_DIR)}. Skipping TCP issue and inter-packet arrival time analysis.")
        
        # No HTTP server cleanup needed (none was started)
        logger.info("No HTTP server cleanup required.")

        # --- Phase 4: Cooldown ---
        phase_start = time.time()
        logger.info(f"Phase 4: Cooldown ({scenario_durations['cooldown']}s)...")
        update_flow_timeline(flow_label_timeline, 'normal')  # Update timeline dynamically
        time.sleep(scenario_durations['cooldown'])
        phase_timings['cooldown'] = time.time() - phase_start

    except Exception as e:
        logger.error(f"An error occurred during traffic scenario: {e}", exc_info=True)
    finally:
        # Ensure all captures are stopped in case of an error
        for proc_name, proc in capture_procs.items():
            if proc and proc.poll() is None: # Check if process is still running
                logger.warning(f"Capture process for {proc_name} was still running. Stopping it.")
                stop_capture(proc)
        
        # Stop flow collection thread gracefully
        if flow_collector_thread and flow_collector_thread.is_alive():
            logger.info("Signaling flow collection thread to stop...")
            flow_stop_event.set()
            logger.info("Waiting for flow collection thread to finish...")
            flow_collector_thread.join(timeout=30)
            if flow_collector_thread.is_alive():
                logger.warning("Flow collection thread did not finish within timeout")
            else:
                logger.info("Flow collection thread finished successfully")
        # Calculate total scenario time
        total_scenario_time = time.time() - scenario_start_time
        
        # Print comprehensive timing summary
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE TIMING SUMMARY")
        logger.info("=" * 60)
        if config_file_path:
            logger.info(f"Configuration File: {config_file_path}")
            logger.info("")
        logger.info(f"Total Scenario Runtime: {total_scenario_time:.2f} seconds ({total_scenario_time/60:.2f} minutes)")
        logger.info("")
        logger.info("Phase-by-Phase Breakdown:")
        
        # Benign traffic
        if 'normal_traffic' in phase_timings:
            logger.info(f"  Normal Traffic: {phase_timings['normal_traffic']:.2f}s (configured: {scenario_durations.get('normal_traffic', 'N/A')}s)")
        
        # Enhanced Traditional attacks
        logger.info("  Enhanced Traditional Attacks:")
        for attack in ['syn_flood', 'udp_flood', 'icmp_flood']:
            if attack in phase_timings:
                enhanced_name = f"Enhanced {attack.replace('_', ' ').title()}"
                logger.info(f"    {enhanced_name}: {phase_timings[attack]:.2f}s (configured: {scenario_durations.get(attack, 'N/A')}s)")
        
        # Adversarial attacks
        logger.info("  Adversarial Attacks:")
        for attack in ['ad_syn', 'ad_udp', 'ad_slow']:
            if attack in phase_timings:
                attack_name = {'ad_syn': 'TCP State Exhaustion', 'ad_udp': 'Application Layer', 'ad_slow': 'Slow Read'}[attack]
                logger.info(f"    {attack_name}: {phase_timings[attack]:.2f}s (configured: {scenario_durations.get(attack, 'N/A')}s)")
        
        # Other phases
        for phase in ['initialization', 'cooldown']:
            if phase in phase_timings:
                logger.info(f"  {phase.title()}: {phase_timings[phase]:.2f}s (configured: {scenario_durations.get(phase, 'N/A')}s)")
        
        logger.info("=" * 60)
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

def process_single_pcap(pcap_file_path, label_name, output_dir):
    """
    Process a single PCAP file and return the resulting DataFrame.
    This function is designed to be used with multiprocessing.
    """
    import pandas as pd
    from pathlib import Path
    import logging
    
    # Set up logging for this worker process
    worker_logger = logging.getLogger(f'worker_{label_name}')
    worker_logger.setLevel(logging.INFO)
    
    pcap_file = Path(pcap_file_path)
    output_dir = Path(output_dir)
    
    try:
        worker_logger.info(f"Processing {pcap_file.name} with label '{label_name}'...")
        
        if not pcap_file.exists():
            worker_logger.warning(f"PCAP file not found: {pcap_file.name}. Skipping.")
            return None

        # Verify PCAP integrity before processing
        integrity_results = verify_pcap_integrity(pcap_file)
        if not integrity_results['valid']:
            worker_logger.error(f"PCAP integrity check failed for {pcap_file.name}: {integrity_results['error']}")
            worker_logger.warning("Continuing with PCAP processing despite integrity issues...")
        else:
            worker_logger.info(f"PCAP integrity check passed for {pcap_file.name}: {integrity_results['total_packets']} packets")
            if integrity_results['corruption_rate'] > 0:
                worker_logger.warning(f"Timestamp corruption detected in {pcap_file.name}: {integrity_results['corruption_rate']:.2f}%")

        try:
            corrected_packets, stats = validate_and_fix_pcap_timestamps(pcap_file)
            pcap_start_time = stats['baseline_time']
            worker_logger.info(f"Using baseline timestamp for labeling {pcap_file.name}: {pcap_start_time}")
        except Exception as e:
            worker_logger.error(f"Could not process PCAP timestamps for {pcap_file}: {e}. Skipping labeling for this file.")
            return None

        # Create a simple label timeline for the current PCAP file
        label_timeline = [{
            'start_time': pcap_start_time,
            'end_time': pcap_start_time + 3600, # 1 hour, should be enough
            'label': label_name
        }]
        
        temp_csv_file = output_dir / f"temp_{label_name}.csv"
        enhanced_process_pcap_to_csv(
            str(pcap_file), 
            str(temp_csv_file), 
            label_timeline,
            validate_timestamps=True
        )
        
        if temp_csv_file.exists():
            df = pd.read_csv(temp_csv_file)
            temp_csv_file.unlink() # Delete temporary CSV
            worker_logger.info(f"Successfully processed {pcap_file.name}: {len(df)} records")
            return df
        else:
            worker_logger.warning(f"No CSV generated for {pcap_file.name}.")
            return None
            
    except Exception as e:
        worker_logger.error(f"Error processing {pcap_file.name}: {e}")
        return None

def process_pcaps_parallel(pcap_files_to_process, output_dir, max_workers=6):
    """
    Process multiple PCAP files in parallel using multiprocessing.
    """
    logger.info(f"Starting parallel PCAP processing with {max_workers} workers...")
    
    all_labeled_dfs = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_pcap = {}
        for pcap_file, label_name in pcap_files_to_process:
            future = executor.submit(process_single_pcap, str(pcap_file), label_name, str(output_dir))
            future_to_pcap[future] = (pcap_file, label_name)
        
        # Collect results as they complete
        for future in future_to_pcap:
            pcap_file, label_name = future_to_pcap[future]
            try:
                df = future.result()
                if df is not None:
                    all_labeled_dfs.append(df)
                    logger.info(f"✓ Completed processing {pcap_file.name} ({len(df)} records)")
                else:
                    logger.warning(f"✗ Failed to process {pcap_file.name}")
            except Exception as e:
                logger.error(f"✗ Error processing {pcap_file.name}: {e}")
    
    logger.info(f"Parallel PCAP processing completed. Processed {len(all_labeled_dfs)} files successfully.")
    return all_labeled_dfs

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
    parser.add_argument(
        'config_file', 
        nargs='?', 
        default='config.json',
        help='Path to configuration JSON file (default: config.json)'
    )
    parser.add_argument('--cores', type=int, default=min(4, cpu_count()), 
                       help=f'Number of CPU cores to use for PCAP processing (default: {min(4, cpu_count())}, max: {cpu_count()})')
    args = parser.parse_args()
    
    # Track overall execution time
    main_start_time = time.time()

    # Initialize standardized logging
    initialize_logging(OUTPUT_DIR, console_level=logging.INFO)
    logger = get_main_logger(OUTPUT_DIR)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Print standardized header
    ConsoleOutput.print_header("AdDDoSDN Dataset Generation Framework")

    # Clean up any previous Mininet instances
    logger.info("Cleaning up any previous Mininet instances...")
    subprocess.run(["mn", "-c"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info("Mininet cleanup complete.")

    verify_tools()

    # Load durations from config file (provided via command line or default config.json)
    config_file_path = Path(args.config_file)
    if not config_file_path.is_absolute():
        config_file_path = BASE_DIR / config_file_path
    
    if not config_file_path.exists():
        logger.error(f"Config file not found: {config_file_path}")
        sys.exit(1)
    
    logger.info(f"Using configuration file: {config_file_path}")
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    
    scenario_durations = config.get("scenario_durations", {})
    
    # Extract durations with default values
    initialization_duration = scenario_durations.get("initialization", 5)
    normal_traffic_duration = scenario_durations.get("normal_traffic", 5)
    syn_flood_duration = scenario_durations.get("syn_flood", 5)
    udp_flood_duration = scenario_durations.get("udp_flood", 5)
    icmp_flood_duration = scenario_durations.get("icmp_flood", 5)
    ad_syn_duration = scenario_durations.get("ad_syn", 5)
    ad_udp_duration = scenario_durations.get("ad_udp", 5)
    ad_slow_duration = scenario_durations.get("ad_slow", 5)
    cooldown_duration = scenario_durations.get("cooldown", 10) # Cooldown is 10s for flow collection

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

        # Get scenario start time after Mininet setup
        scenario_start_time = time.time()

        # Initialize dynamic timeline tracking - will be updated in real-time
        flow_label_timeline = []
        
        # Calculate generous duration for flow collection accounting for execution delays
        config_duration = normal_traffic_duration + syn_flood_duration + udp_flood_duration + icmp_flood_duration + \
                         ad_syn_duration + ad_udp_duration + ad_slow_duration + cooldown_duration
        # Add significant buffer for actual execution delays (startups, network delays, etc.)
        total_scenario_duration = config_duration + 120  # Config duration + 120s buffer

        # 3. Run Scenario
        run_traffic_scenario(mininet_network, flow_label_timeline, scenario_durations, total_scenario_duration, config_file_path)

        logger.info("PCAP generation complete.")

        # List of PCAP files and their corresponding labels
        pcap_files_to_process = [
            (PCAP_FILE_NORMAL, 'normal'),
            (PCAP_FILE_SYN_FLOOD, 'syn_flood'),
            (PCAP_FILE_UDP_FLOOD, 'udp_flood'),
            (PCAP_FILE_ICMP_FLOOD, 'icmp_flood'),
            (PCAP_FILE_AD_SYN, 'ad_syn'),
            (PCAP_FILE_AD_UDP, 'ad_udp'),
            (PCAP_FILE_AD_SLOW, 'ad_slow'),
            (PCAP_FILE_H6_SLOW_READ, 'h6_slow_read'),
        ]

        # Validate cores argument
        max_workers = min(max(1, args.cores), cpu_count())
        if args.cores > cpu_count():
            logger.warning(f"Requested {args.cores} cores, but only {cpu_count()} available. Using {max_workers} cores.")
        
        logger.info(f"Processing {len(pcap_files_to_process)} PCAP files using {max_workers} CPU cores...")
        
        # Process PCAPs in parallel with timing
        pcap_start_time = time.time()
        all_labeled_dfs = process_pcaps_parallel(pcap_files_to_process, OUTPUT_DIR, max_workers)
        pcap_processing_time = time.time() - pcap_start_time
        
        logger.info(f"Parallel PCAP processing completed in {pcap_processing_time:.2f} seconds ({pcap_processing_time/60:.2f} minutes)")

        if all_labeled_dfs:
            final_df = pd.concat(all_labeled_dfs, ignore_index=True)
            final_df.to_csv(OUTPUT_CSV_FILE, index=False)
            logger.info(f"Combined labeled CSV generated at: {OUTPUT_CSV_FILE.relative_to(BASE_DIR)}")
            # 5. Verify labels in CSV (can be adapted for combined CSV if needed, or individual verification)
            # For now, we'll just check if the file exists
            if OUTPUT_CSV_FILE.exists():
                logger.info("Final combined CSV created successfully.")
                try:
                    packet_df = pd.read_csv(OUTPUT_CSV_FILE)
                    if 'Label_multi' in packet_df.columns:
                        packet_counts = packet_df['Label_multi'].value_counts()
                        logger.info("\n--- Packet Feature Counts by Class ---")
                        for label, count in packet_counts.items():
                            logger.info(f"  {label}: {count} packets")
                    else:
                        logger.warning("Label_multi column not found in packet_features.csv.")
                except Exception as e:
                    logger.error(f"Error reading or processing packet_features.csv: {e}")
            else:
                logger.error("Failed to create final combined CSV.")
        else:
            logger.error("No labeled dataframes were generated. Final CSV will not be created.")

        # Check if flow data was collected
        if OUTPUT_FLOW_CSV_FILE.exists():
            logger.info(f"Flow-level dataset generated at: {OUTPUT_FLOW_CSV_FILE.relative_to(BASE_DIR)}")
            try:
                flow_df = pd.read_csv(OUTPUT_FLOW_CSV_FILE)
                if 'Label_multi' in flow_df.columns:
                    flow_counts = flow_df['Label_multi'].value_counts()
                    logger.info("\n--- Flow Feature Counts by Class ---")
                    for label, count in flow_counts.items():
                        logger.info(f"  {label}: {count} flows")
                else:
                    logger.warning("Label_multi column not found in flow_features.csv.")
            except Exception as e:
                logger.error(f"Error reading or processing flow_features.csv: {e}")
        else:
            logger.warning("No flow-level dataset was generated.")
            
        # Generate and display dataset summary
        logger.info("Generating dataset summary...")
        print_dataset_summary(OUTPUT_DIR, logger)
        
        # Run timeline analysis
        if OUTPUT_CSV_FILE.exists() and OUTPUT_FLOW_CSV_FILE.exists():
            logger.info("Running timeline analysis...")
            timeline_results = analyze_dataset_timeline(OUTPUT_CSV_FILE, OUTPUT_FLOW_CSV_FILE, logger)
            
            # Print detailed timeline report if requested or if there are issues
            if timeline_results['score'] < 70:
                print_detailed_timeline_report(timeline_results, logger)
            
            # Store results for final summary
            timeline_score = timeline_results['score']
            timeline_status = timeline_results['status']
        else:
            logger.warning("Skipping timeline analysis - missing CSV files")
            timeline_score = 0
            timeline_status = "FILES_MISSING"
        
        # Final overall timing summary
        total_execution_time = time.time() - main_start_time
        logger.info("=" * 60)
        logger.info("FINAL EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Execution Time: {total_execution_time:.2f} seconds ({total_execution_time/60:.2f} minutes | {total_execution_time/3600:.2f} hours)")
        logger.info(f"Dataset Generation Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Add timeline analysis results to summary
        if 'timeline_score' in locals():
            logger.info(f"Timeline Alignment Score: {timeline_score:.1f}%")
            if timeline_score >= 90:
                logger.info("✅ Timeline Quality: EXCELLENT")
            elif timeline_score >= 70:
                logger.info("✅ Timeline Quality: GOOD")
            elif timeline_score >= 50:
                logger.info("⚠️  Timeline Quality: FAIR - Consider adjustments")
            else:
                logger.info("❌ Timeline Quality: POOR - Requires attention")
        
        logger.info("=" * 60)

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
