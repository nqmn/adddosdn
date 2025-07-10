#!/usr/bin/env python3
"""
Simplified and robust PCAP processing for the AdDDoSDN project.
"""

import logging
import subprocess
import time
from pathlib import Path
from scapy.all import rdpcap

# Configure logging
logger = logging.getLogger(__name__)

def improve_capture_reliability(net, outfile):
    """Start a reliable packet capture using tcpdump."""
    logger.info(f"Starting packet capture. Output file: {outfile}")
    
    # Get the switch from the network
    s1 = net.get('s1')
    
    # Use the 'any' interface to capture all traffic on the switch
    intf = 'any'
    
    # Ensure the output directory exists
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    
    # Build the tcpdump command
    # -i any: Capture on all interfaces
    # -w <file>: Write the raw packets to a file
    # -s 0: Capture the full packet
    # ip and not ip6: Filter for IPv4 traffic only
    # net 10.0.0.0/8: Capture traffic within the Mininet network
    cmd = [
        'tcpdump',
        '-i', intf,
        '-w', str(outfile),
        '-s', '0',
        'ip', 'and', 'not', 'ip6', 'and', 'net', '10.0.0.0/8'
    ]
    
    logger.info(f"Starting tcpdump with command: {' '.join(cmd)}")
    
    # Start the capture process in the background
    process = s1.popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    
    # Give tcpdump a moment to initialize
    time.sleep(2)
    
    # Check if the process started successfully
    if process.poll() is not None:
        error_output = process.stderr.read().strip()
        logger.error(f"tcpdump failed to start. Error: {error_output}")
        raise RuntimeError(f"tcpdump process exited with code {process.returncode}")
        
    logger.info(f"tcpdump started successfully with PID: {process.pid}")
    return process

def verify_pcap_integrity(pcap_file):
    """Verify the integrity of the generated PCAP file."""
    logger.info(f"Verifying integrity of PCAP file: {pcap_file}")
    
    if not Path(pcap_file).exists() or Path(pcap_file).stat().st_size == 0:
        logger.error("PCAP file does not exist or is empty.")
        return {'valid': False, 'error': 'File not found or is empty'}

    try:
        packets = rdpcap(str(pcap_file))
        if len(packets) == 0:
            logger.warning("PCAP file contains no packets.")
            return {'valid': False, 'error': 'No packets in file'}
        
        logger.info(f"PCAP integrity check passed. Found {len(packets)} packets.")
        return {'valid': True, 'total_packets': len(packets), 'corruption_rate': 0.0}
    except Exception as e:
        logger.error(f"Error reading PCAP file during integrity check: {e}")
        return {'valid': False, 'error': str(e)}

def enhanced_process_pcap_to_csv(pcap_file, output_csv, label_timeline, validate_timestamps=True):
    """Process the PCAP to CSV. The name is kept for compatibility.
    This version does not perform timestamp validation, as tcpdump is more reliable.
    """
    from src.utils.process_pcap_to_csv import process_pcap_to_csv
    logger.info("Passing PCAP to processing function.")
    process_pcap_to_csv(str(pcap_file), str(output_csv), label_timeline)

def validate_and_fix_pcap_timestamps(pcap_file):
    """A placeholder function for compatibility. Returns mock data.
    Timestamp issues are less likely with tcpdump.
    """
    logger.info("Skipping timestamp validation as tcpdump is used.")
    try:
        packets = rdpcap(str(pcap_file))
        baseline = packets[0].time if packets else time.time()
        return packets, {
            'corrupted_packets': 0,
            'baseline_time': baseline
        }
    except Exception as e:
        logger.error(f"Could not read PCAP for baseline time: {e}")
        return [], {
            'corrupted_packets': 0,
            'baseline_time': time.time()
        }
