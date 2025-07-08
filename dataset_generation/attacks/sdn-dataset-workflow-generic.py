#!/usr/bin/env python
"""
Complete SDN Dataset Generation Workflow Script
This script automates generation, capture, processing, labeling, merging,
flow-stats collection, and documentation of network traffic data in an SDN environment.
"""
import os
import time
import subprocess
import argparse
import random
import psutil
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import pandas as pd
import requests
import json
from scapy.all import IP, TCP, ICMP, UDP, Raw, RandShort, send, fragment

# 1. SDN Topology Configuration
def create_topology(controller_ip='127.0.0.1', controller_port=6633):
    """Create a customizable SDN topology with 3 switches and 6 hosts"""
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)
    c0 = net.addController('c0', controller=RemoteController,
                          ip=controller_ip, port=controller_port)
    s1, s2, s3 = [net.addSwitch(name) for name in ('s1', 's2', 's3')]
    hosts = [net.addHost(f'h{i}', ip=f'10.0.0.{i}') for i in range(1, 7)]

    # Links
    net.addLink(hosts[0], s1)
    net.addLink(hosts[1], s1)
    net.addLink(hosts[2], s2)
    net.addLink(hosts[3], s2)
    net.addLink(hosts[4], s3)
    net.addLink(hosts[5], s3)
    net.addLink(s1, s2)
    net.addLink(s2, s3)

    # Start network
    net.build()
    c0.start()
    for sw in (s1, s2, s3):
        sw.start([c0])
        sw.cmd(f"ovs-vsctl set bridge {sw.name} stp-enable=true")
    info('*** Network is running\n')
    return net

# 2. Packet Capture Setup
def setup_packet_capture(interface, output_dir, filename_prefix, duration):
    """Set up tcpdump to capture traffic into a PCAP file for a duration"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pcap_file = os.path.join(output_dir, f"{filename_prefix}_{timestamp}.pcap")
    cmd = f"tcpdump -i {interface} -w {pcap_file} -G {duration} -W 1 &"
    process = subprocess.Popen(cmd, shell=True)
    info(f"*** Started packet capture on {interface}, saving to {pcap_file}\n")
    return process, pcap_file

# 3. Traffic Generation Functions
def generate_normal_traffic(net, duration=60):
    """Generate normal background traffic"""
    info('*** Generating normal background traffic\n')
    hosts = net.hosts
    end_time = time.time() + duration
    while time.time() < end_time:
        src = random.choice(hosts)
        dst = random.choice([h for h in hosts if h != src])
        if random.random() < 0.7:
            src.cmd(f"ping -c 1 {dst.IP()} &")
        else:
            dst.cmd('iperf -s -t 5 &')
            time.sleep(0.2)
            src.cmd(f"iperf -c {dst.IP()} -t 3 &")
        time.sleep(random.uniform(0.1, 1))
    info('*** Finished generating normal background traffic\n')

# 4. Predefined Attack Traffic
def generate_attack_traffic(net, attack_type, duration=30):
    """Generate specific attack traffic"""
    info(f"*** Generating {attack_type} attack traffic\n")
    attacker, victim = net.hosts[0], net.hosts[-1]
    if attack_type == "tcp_syn_flood":
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, TCP, RandShort, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')"
            f"/TCP(dport=80, sport=RandShort(), flags='S'), verbose=0)"
            f" for _ in range(1000)]\nEOF &"
        )
    elif attack_type == "icmp_flood":
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, ICMP, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')/ICMP(), verbose=0)"
            f" for _ in range(500)]\nEOF &"
        )
    elif attack_type == "udp_flood":
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, UDP, RandShort, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')/UDP(dport=53, sport=RandShort()), verbose=0)"
            f" for _ in range(800)]\nEOF &"
        )
    elif attack_type == "http_flood":
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, TCP, Raw, RandShort, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')"
            "/TCP(dport=80, sport=RandShort(), flags='S')/Raw(b'GET / HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n'), verbose=0)"
            f" for _ in range(600)]\nEOF &"
        )
    time.sleep(duration)
    info(f"*** Finished generating {attack_type} attack traffic\n")

# 5. Custom Attack Variants
def send_packet_randomized(src_ip, dst_ip, proto, num_packets):
    """Send packets with randomized inter-packet delays"""
    for _ in range(num_packets):
        delay = random.uniform(0.01, 0.1)
        packet = IP(src=src_ip, dst=dst_ip) / proto()
        send(packet, verbose=0)
        time.sleep(delay)


def send_mimic_traffic(src_ip, dst_ip, num_packets):
    """Mimic legitimate HTTP request bursts"""
    for _ in range(num_packets):
        packet = (
            IP(src=src_ip, dst=dst_ip)
            / TCP(dport=80, sport=RandShort(), flags='S', seq=1000, window=8192)
            / Raw(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        )
        send(packet, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def send_evasive_traffic(src_ip, dst_ip, num_packets):
    """Send fragmented UDP traffic with random TTLs/window sizes"""
    for _ in range(num_packets):
        ttl_value = random.randint(64, 128)
        window_size = random.randint(8192, 65535)
        packet = (
            IP(src=src_ip, dst=dst_ip, ttl=ttl_value)
            / TCP(dport=80, sport=RandShort(), flags='S', seq=1000, window=window_size)
        )
        send(packet, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def send_hybrid_attack(src_ip, dst_ip, num_flood=500, num_ping=100):
    """Combination of ICMP ping and TCP SYN flood"""
    for _ in range(num_ping):
        pkt = IP(src=src_ip, dst=dst_ip) / ICMP()
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.1, 1))
    for _ in range(num_flood):
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(dport=80, sport=RandShort(), flags='S', seq=1000)
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def adaptive_attack(src_ip, dst_ip, base_flood_rate, max_flood_rate):
    """Adjust flood rate dynamically based on CPU usage"""
    cpu_usage = psutil.cpu_percent(interval=1)
    flood_rate = min(base_flood_rate * 2, max_flood_rate) if cpu_usage > 80 else base_flood_rate
    for _ in range(flood_rate):
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(dport=80, sport=RandShort(), flags='S', seq=1000)
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def run_all():
    """Execute all custom attacks sequentially"""
    src, dst = '10.0.0.1', '10.0.0.2'
    num_flood_packets, num_normal_ping = 1000, 100
    send_hybrid_attack(src, dst, num_flood_packets, num_normal_ping)
    send_evasive_traffic(src, dst, num_flood_packets)
    send_packet_randomized(src, dst, TCP, num_flood_packets)
    send_mimic_traffic(src, dst, num_flood_packets)
    adaptive_attack(src, dst, base_flood_rate=500, max_flood_rate=2000)



# 7. Data Labeling & Annotation
def label_dataset(csv_file, attack_info):
    info(f"*** Labeling dataset {csv_file}\n")
    df = pd.read_csv(csv_file)
    df['label'] = 'normal'
    for entry in attack_info:
        mask = (df['timestamp'] >= entry['start_time']) & (df['timestamp'] <= entry['end_time'])
        df.loc[mask, 'label'] = entry['type']
    labeled_file = csv_file.replace('.csv', '_labeled.csv')
    df.to_csv(labeled_file, index=False)
    info(f"*** Labeled file at {labeled_file}\n")
    return labeled_file

# 8. Dataset Merging & Final Processing
def merge_datasets(csv_files, output_file):
    info('*** Merging datasets\n')
    dfs = [pd.read_csv(f) for f in csv_files]
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv(output_file, index=False)
    info(f"*** Merged dataset at {output_file}\n")
    return output_file


def finalize_dataset(dataset_file, output_file):
    info('*** Finalizing dataset\n')
    df = pd.read_csv(dataset_file)
    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)
    atk_cnt = df[df['label']!='normal'].shape[0]
    norm_cnt = df[df['label']=='normal'].shape[0]
    if norm_cnt > 2 * atk_cnt:
        norm_df = df[df['label']=='normal'].sample(2 * atk_cnt)
        atk_df = df[df['label']!='normal']
        df = pd.concat([norm_df, atk_df])
    df.to_csv(output_file, index=False)
    info(f"*** Final dataset at {output_file}\n")
    return output_file

# 9. Flow Collection from SDN Controller
def collect_sdn_flow_stats(controller_ip, controller_port, output_file):
    info('*** Collecting SDN flow stats\n')
    url = f"http://{controller_ip}:8080/stats/flow/1"
    try:
        resp = requests.get(url)
        data = resp.json()
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        info(f"*** Flow stats saved to {output_file}\n")
        return output_file
    except Exception as e:
        info(f"*** Error collecting flow stats: {e}\n")
        return None

# 10. Dataset Documentation
def generate_dataset_documentation(dataset_file, metadata, output_file):
    info('*** Generating documentation\n')
    df = pd.read_csv(dataset_file)
    with open(output_file, 'w') as f:
        f.write("# SDN Dataset Documentation\n\n")
        f.write("## Dataset Information\n\n")
        f.write(f"- **Generation Date:** {metadata['date']}\n")
        f.write(f"- **Controller:** {metadata['controller']}\n")
        f.write(f"- **Topology:** {metadata['topology']}\n")
        f.write(f"- **Total Flows:** {len(df)}\n\n")
        f.write("## Class Distribution\n\n")
        for lbl, cnt in df['label'].value_counts().items():
            pct = cnt / len(df) * 100
            f.write(f"- **{lbl}:** {cnt} ({pct:.2f}%)\n")
        f.write("\n## Feature List\n\n")
        for col in df.columns:
            f.write(f"- **{col}**\n")
        f.write("\n## Attack Types\n\n")
        f.write("- **tcp_syn_flood:** TCP SYN flood on port 80\n")
        f.write("- **icmp_flood:** ICMP echo flood\n")
        f.write("- **udp_flood:** UDP flood on port 53\n")
        f.write("- **http_flood:** HTTP GET flood\n")
    info(f"*** Documentation at {output_file}\n")
    return output_file

# 11. Main Orchestration Function
def generate_sdn_dataset(output_dir, controller_ip='127.0.0.1', controller_port=6633):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(output_dir, f"sdn_dataset_{timestamp}")
    pcap_dir = os.path.join(run_dir, 'pcap')
    csv_dir = os.path.join(run_dir, 'csv')
    os.makedirs(pcap_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    setLogLevel('info')
    net = create_topology(controller_ip, controller_port)
    attack_info, csv_files = [], []
    try:
        # Normal traffic
