from scapy.all import rdpcap, Ether, IP, TCP, UDP, ICMP
import csv
import os

def process_pcap_to_csv(pcap_file, output_csv_file):
    print(f"Processing {pcap_file} to {output_csv_file}...")
    
    if not os.path.exists(pcap_file):
        print(f"Error: PCAP file not found at {pcap_file}")
        return

    packets = rdpcap(pcap_file)

    with open(output_csv_file, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'packet_length', 'eth_type',
            'ip_src', 'ip_dst', 'ip_proto', 'ip_ttl', 'ip_id', 'ip_flags', 'ip_len',
            'src_port', 'dst_port',
            'tcp_flags', 'tcp_seq', 'tcp_ack', 'tcp_window',
            'icmp_type', 'icmp_code'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for packet in packets:
            row = {
                'timestamp': packet.time,
                'packet_length': len(packet),
                'eth_type': '',
                'ip_src': '',
                'ip_dst': '',
                'ip_proto': '',
                'ip_ttl': '',
                'ip_id': '',
                'ip_flags': '',
                'ip_len': '',
                'src_port': '',
                'dst_port': '',
                'tcp_flags': '',
                'tcp_seq': '',
                'tcp_ack': '',
                'tcp_window': '',
                'icmp_type': '',
                'icmp_code': ''
            }

            if Ether in packet:
                row['eth_type'] = hex(packet[Ether].type)

            if IP in packet:
                row['ip_src'] = packet[IP].src
                row['ip_dst'] = packet[IP].dst
                row['ip_proto'] = packet[IP].proto
                row['ip_ttl'] = packet[IP].ttl
                row['ip_id'] = packet[IP].id
                row['ip_flags'] = str(packet[IP].flags)
                row['ip_len'] = packet[IP].len

                if TCP in packet:
                    row['src_port'] = packet[TCP].sport
                    row['dst_port'] = packet[TCP].dport
                    row['tcp_flags'] = str(packet[TCP].flags)
                    row['tcp_seq'] = packet[TCP].seq
                    row['tcp_ack'] = packet[TCP].ack
                    row['tcp_window'] = packet[TCP].window
                elif UDP in packet:
                    row['src_port'] = packet[UDP].sport
                    row['dst_port'] = packet[UDP].dport
                elif ICMP in packet:
                    row['icmp_type'] = packet[ICMP].type
                    row['icmp_code'] = packet[ICMP].code
            
            writer.writerow(row)
    
    print(f"Successfully processed {len(packets)} packets to {output_csv_file}")

if __name__ == "__main__":
    # Default file paths (can be changed if script is run with arguments)
    default_pcap_file = "traffic.pcap"
    default_output_csv_file = "offline_dataset.csv"

    # You can run this script from the command line like:
    # python process_pcap_to_csv.py [input_pcap_file] [output_csv_file]
    import sys
    pcap_file_arg = sys.argv[1] if len(sys.argv) > 1 else default_pcap_file
    output_csv_file_arg = sys.argv[2] if len(sys.argv) > 2 else default_output_csv_file

    process_pcap_to_csv(pcap_file_arg, output_csv_file_arg)