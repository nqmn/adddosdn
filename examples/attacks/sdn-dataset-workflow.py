#!/usr/bin/env python
"""
Complete SDN Dataset Generation Workflow Script
This script automates generation, capture, processing, labeling, merging,
flow-stats collection, and documentation of network traffic data in an SDN environment
using a Ryu controller or a generic remote controller.
"""
import os
import time
import subprocess
import argparse
import random
import psutil
import pandas as pd
import requests
import json
from scapy.all import IP, TCP, ICMP, UDP, Raw, RandShort, send, fragment
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from mininet.link import TCLink

# 0. Helper: Start Ryu Controller
def start_ryu(app_path):
    """Launch Ryu manager with specified application"""
    info(f"*** Starting Ryu controller with app {app_path}\n")
    return subprocess.Popen(["ryu-manager", app_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 1. SDN Topology Configuration
def create_topology(controller_ip, controller_port, ofp_version='OpenFlow13'):
    """Create SDN topology with Ryu or remote controller"""
    setLogLevel('info')
    net = Mininet(controller=RemoteController,
                  link=TCLink,
                  switch=OVSKernelSwitch,
                  autoSetMacs=True)
    c0 = net.addController('c0', controller=RemoteController,
                           ip=controller_ip,
                           port=controller_port)
    # Add switches and hosts
    s1, s2, s3 = [net.addSwitch(name, protocols=ofp_version) for name in ('s1', 's2', 's3')]
    hosts = [net.addHost(f'h{i}', ip=f'10.0.0.{i}') for i in range(1, 7)]
    # Create links
    for a, b in [(hosts[0], s1), (hosts[1], s1), (hosts[2], s2), (hosts[3], s2),
                 (hosts[4], s3), (hosts[5], s3), (s1, s2), (s2, s3)]:
        net.addLink(a, b)
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
    """Start tcpdump capture for a fixed duration"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pcap_file = os.path.join(output_dir, f"{filename_prefix}_{timestamp}.pcap")
    cmd = f"tcpdump -i {interface} -w {pcap_file} -G {duration} -W 1 &"
    proc = subprocess.Popen(cmd, shell=True)
    info(f"*** Capturing on {interface} -> {pcap_file}\n")
    return proc, pcap_file

# 3. Traffic Generation: Normal + Predefined Attacks
def generate_normal_traffic(net, duration=60):
    info('*** Generating normal background traffic\n')
    hosts = net.hosts
    end = time.time() + duration
    while time.time() < end:
        src = random.choice(hosts)
        dst = random.choice([h for h in hosts if h != src])
        if random.random() < 0.7:
            src.cmd(f"ping -c 1 {dst.IP()} &")
        else:
            dst.cmd('iperf -s -t 5 &')
            time.sleep(0.2)
            src.cmd(f"iperf -c {dst.IP()} -t 3 &")
        time.sleep(random.uniform(0.1, 1))
    info('*** Normal traffic done\n')


def generate_attack_traffic(net, attack_type, duration=30):
    info(f"*** Generating {attack_type}\n")
    attacker, victim = net.hosts[0], net.hosts[-1]
    if attack_type == 'tcp_syn_flood':
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, TCP, RandShort, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')"
            f"/TCP(dport=80, sport=RandShort(), flags='S'), verbose=0) for _ in range(1000)]\nEOF &"
        )
    elif attack_type == 'icmp_flood':
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, ICMP, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')/ICMP(), verbose=0) for _ in range(500)]\nEOF &"
        )
    elif attack_type == 'udp_flood':
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, UDP, RandShort, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')/UDP(dport=53, sport=RandShort()), verbose=0) for _ in range(800)]\nEOF &"
        )
    elif attack_type == 'http_flood':
        attacker.cmd(
            f"python - << 'EOF'\n"
            "from scapy.all import IP, TCP, Raw, RandShort, send\n"
            f"[send(IP(src='{attacker.IP()}', dst='{victim.IP()}')/TCP(dport=80, sport=RandShort(), flags='S')"
            f"/Raw(b'GET / HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n'), verbose=0) for _ in range(600)]\nEOF &"
        )
    time.sleep(duration)
    info(f"*** {attack_type} done\n")

# 4. Custom Attack Variants
def send_packet_randomized(src_ip, dst_ip, proto, num_packets):
    for _ in range(num_packets):
        delay = random.uniform(0.01, 0.1)
        pkt = IP(src=src_ip, dst=dst_ip) / proto()
        send(pkt, verbose=0)
        time.sleep(delay)


def send_mimic_traffic(src_ip, dst_ip, num_packets):
    for _ in range(num_packets):
        pkt = (
            IP(src=src_ip, dst=dst_ip)
            / TCP(dport=80, sport=RandShort(), flags='S', seq=1000, window=8192)
            / Raw(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        )
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def send_evasive_traffic(src_ip, dst_ip, num_packets):
    for _ in range(num_packets):
        ttl = random.randint(64, 128)
        win = random.randint(8192, 65535)
        pkt = IP(src=src_ip, dst=dst_ip, ttl=ttl) / TCP(dport=80, sport=RandShort(), flags='S', window=win)
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def send_hybrid_attack(src_ip, dst_ip, num_flood=500, num_ping=100):
    for _ in range(num_ping):
        pkt = IP(src=src_ip, dst=dst_ip) / ICMP()
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.1, 1))
    for _ in range(num_flood):
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(dport=80, sport=RandShort(), flags='S')
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def adaptive_attack(src_ip, dst_ip, base_flood_rate, max_flood_rate):
    cpu = psutil.cpu_percent(interval=1)
    rate = min(base_flood_rate * 2, max_flood_rate) if cpu > 80 else base_flood_rate
    for _ in range(rate):
        pkt = IP(src=src_ip, dst=dst_ip) / TCP(dport=80, sport=RandShort(), flags='S')
        send(pkt, verbose=0)
        time.sleep(random.uniform(0.01, 0.1))


def run_all():
    src, dst = '10.0.0.1', '10.0.0.2'
    send_hybrid_attack(src, dst, 1000, 100)
    send_evasive_traffic(src, dst, 1000)
    send_packet_randomized(src, dst, TCP, 1000)
    send_mimic_traffic(src, dst, 1000)
    adaptive_attack(src, dst, 500, 2000)

# 5. Feature Extraction
def process_with_cicflowmeter(input_pcap, output_dir):
    info(f"*** Processing {input_pcap}\n")
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(input_pcap))[0]
    csv_out = os.path.join(output_dir, f"{base}.csv")
    cmd = f"cicflowmeter -f {input_pcap} -c {csv_out}"
    try:
        subprocess.run(cmd, shell=True, check=True)
        return csv_out
    except subprocess.CalledProcessError:
        return None

# 6. Labeling
def label_dataset(csv_file, attack_info):
    df = pd.read_csv(csv_file)
    df['label'] = 'normal'
    for e in attack_info:
        mask = (df['timestamp'] >= e['start_time']) & (df['timestamp'] <= e['end_time'])
        df.loc[mask, 'label'] = e['type']
    out = csv_file.replace('.csv', '_labeled.csv')
    df.to_csv(out, index=False)
    return out

# 7. Merging & Finalizing
def merge_datasets(csv_list, output_file):
    df = pd.concat([pd.read_csv(f) for f in csv_list], ignore_index=True)
    df.to_csv(output_file, index=False)
    return output_file


def finalize_dataset(dataset_file, output_file):
    df = pd.read_csv(dataset_file)
    df.drop_duplicates(inplace=True)
    df.fillna(0, inplace=True)
    atk = df[df['label']!='normal'].shape[0]
    norm = df[df['label']=='normal'].shape[0]
    if norm > 2 * atk:
        df = pd.concat([df[df['label']=='normal'].sample(2 * atk), df[df['label']!='normal']])
    df.to_csv(output_file, index=False)
    return output_file

# 8. Flow Stats Collection
def collect_sdn_flow_stats(controller_ip, controller_port, output_file):
    url = f"http://{controller_ip}:8080/stats/flow/1"
    try:
        r = requests.get(url)
        with open(output_file, 'w') as f:
            json.dump(r.json(), f, indent=2)
        return output_file
    except:
        return None

# 9. Documentation Generation
def generate_dataset_documentation(dataset_file, metadata, output_file):
    df = pd.read_csv(dataset_file)
    with open(output_file, 'w') as f:
        f.write("# SDN Dataset Documentation\n\n")
        f.write(f"- Generation Date: {metadata['date']}\n")
        f.write(f"- Controller: {metadata['controller']}\n")
        f.write(f"- Topology: {metadata['topology']}\n")
        f.write(f"- Total Flows: {len(df)}\n\n")
        dist = df['label'].value_counts()
        for lbl, cnt in dist.items():
            f.write(f"- {lbl}: {cnt} ({cnt/len(df)*100:.2f}%)\n")
        f.write("\n## Features\n")
        for col in df.columns:
            f.write(f"- {col}\n")
    return output_file

# 10. Dataset Orchestrator
def generate_sdn_dataset(output_dir, controller_ip, controller_port):
    ts = time.strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(output_dir, f"sdn_dataset_{ts}")
    pcap_dir = os.path.join(run_dir, 'pcap')
    csv_dir = os.path.join(run_dir, 'csv')
    os.makedirs(pcap_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    net = create_topology(controller_ip, controller_port)
    attack_info, csvs = [], []
    try:
        # Normal traffic
        _, pcap = setup_packet_capture('s1-eth1', pcap_dir, 'normal', 60)
        generate_normal_traffic(net, 60)
        time.sleep(5)
        subprocess.call("pkill -f tcpdump", shell=True)
        csv = process_with_cicflowmeter(pcap, csv_dir)
        if csv: csvs.append(csv)
        # Attack types
        for at in ('tcp_syn_flood','icmp_flood','udp_flood','http_flood'):
            start = time.time()
            _, pcap = setup_packet_capture('s1-eth1', pcap_dir, at, 40)
            generate_normal_traffic(net, 10)
            generate_attack_traffic(net, at, 30)
            end = time.time()
            attack_info.append({'type':at,'start_time':start,'end_time':end})
            time.sleep(5)
            subprocess.call("pkill -f tcpdump", shell=True)
            csv = process_with_cicflowmeter(pcap, csv_dir)
            if csv:
                lbl = label_dataset(csv, [{'type':at,'start_time':start,'end_time':end}])
                csvs.append(lbl)
        # Merge & finalize
        merged = merge_datasets(csvs, os.path.join(run_dir,'merged.csv'))
        final = finalize_dataset(merged, os.path.join(run_dir,'final.csv'))
        # Flow stats & docs
        collect_sdn_flow_stats(controller_ip, controller_port, os.path.join(run_dir,'flow_stats.json'))
        md = generate_dataset_documentation(final,
            {'date':ts,'controller':f"{controller_ip}:{controller_port}",'topology':'3-switch linear'},
            os.path.join(run_dir,'README.md'))
        return final
    finally:
        net.stop()

# 11. Main Entry Point
def main():
    parser = argparse.ArgumentParser(description='SDN dataset workflow with Ryu support')
    parser.add_argument('--output', default='./sdn_datasets', help='Output directory')
    parser.add_argument('--controller-ip', default='127.0.0.1', help='Controller IP')
    parser.add_argument('--controller-port', default=6633, type=int, help='Controller port')
    parser.add_argument('--controller-type', choices=['ryu','remote'], default='ryu', help='Controller type')
    parser.add_argument('--ryu-app', default='ryu/app/simple_switch_13.py', help='Ryu app path')
    parser.add_argument('--run-all', action='store_true', help='Run attack suite')
    args = parser.parse_args()

    proc = None
    if args.controller_type == 'ryu':
        proc = start_ryu(args.ryu_app)
        time.sleep(3)
    if args.run_all:
        run_all()
    else:
        final = generate_sdn_dataset(args.output, args.controller_ip, args.controller_port)
        print(f"Final dataset: {final}")
    if proc:
        info('*** Stopping Ryu controller\n')
        proc.terminate()
        proc.wait()

if __name__ == '__main__':
    main()
