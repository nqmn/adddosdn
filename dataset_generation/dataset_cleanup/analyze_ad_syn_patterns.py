#!/usr/bin/env python3
"""
Analyze ad_syn attack patterns to identify data leakage sources
"""

import pandas as pd
import numpy as np
import json

def analyze_ad_syn_patterns(dataset_path):
    """Analyze ad_syn patterns vs normal traffic"""
    
    print(f"Loading dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    # Filter ad_syn and normal traffic
    ad_syn_data = df[df['Label_multi'] == 'ad_syn'].copy()
    normal_data = df[df['Label_multi'] == 'normal'].copy()
    
    print(f"Ad_syn records: {len(ad_syn_data)}")
    print(f"Normal records: {len(normal_data)}")
    
    if len(ad_syn_data) == 0:
        print("No ad_syn records found!")
        return
    
    # Analyze key differentiating patterns
    analysis = {
        'record_counts': {
            'ad_syn': len(ad_syn_data),
            'normal': len(normal_data)
        }
    }
    
    # 1. Destination Port Analysis
    print("\n=== DESTINATION PORT ANALYSIS ===")
    ad_syn_dst_ports = ad_syn_data['dst_port'].dropna().unique()
    normal_dst_ports = normal_data['dst_port'].dropna().unique()
    
    print(f"Ad_syn destination ports: {sorted(ad_syn_dst_ports)}")
    print(f"Normal destination ports: {sorted(normal_dst_ports)}")
    
    analysis['dst_port'] = {
        'ad_syn_unique_ports': sorted([int(p) for p in ad_syn_dst_ports]),
        'normal_unique_ports': sorted([int(p) for p in normal_dst_ports if not pd.isna(p)]),
        'ad_syn_port_80_percentage': (ad_syn_data['dst_port'] == 80.0).sum() / len(ad_syn_data) * 100
    }
    
    # 2. TCP Flags Analysis  
    print("\n=== TCP FLAGS ANALYSIS ===")
    ad_syn_tcp_flags = ad_syn_data['tcp_flags'].dropna().value_counts()
    normal_tcp_flags = normal_data['tcp_flags'].dropna().value_counts()
    
    print("Ad_syn TCP flags distribution:")
    print(ad_syn_tcp_flags)
    print("\nNormal TCP flags distribution:")
    print(normal_tcp_flags)
    
    analysis['tcp_flags'] = {
        'ad_syn_flags': ad_syn_tcp_flags.to_dict(),
        'normal_flags': normal_tcp_flags.to_dict(),
        'ad_syn_syn_only_percentage': (ad_syn_data['tcp_flags'] == 'S').sum() / len(ad_syn_data) * 100
    }
    
    # 3. Source IP Analysis
    print("\n=== SOURCE IP ANALYSIS ===")
    ad_syn_src_samples = ad_syn_data['ip_src'].dropna().head(20).tolist()
    normal_src_samples = normal_data['ip_src'].dropna().head(20).tolist()
    
    print(f"Ad_syn source IP samples: {ad_syn_src_samples}")
    print(f"Normal source IP samples: {normal_src_samples}")
    
    # Count IP range patterns
    def get_ip_range(ip_str):
        if pd.isna(ip_str):
            return 'unknown'
        if ip_str.startswith('10.0.0.'):
            return '10.0.0.x'
        elif ip_str.startswith('10.'):
            return '10.x.x.x'
        elif ip_str.startswith('172.'):
            return '172.x.x.x'  
        elif ip_str.startswith('192.168.'):
            return '192.168.x.x'
        else:
            return 'other'
    
    ad_syn_data['ip_range'] = ad_syn_data['ip_src'].apply(get_ip_range)
    normal_data['ip_range'] = normal_data['ip_src'].apply(get_ip_range)
    
    ad_syn_ip_ranges = ad_syn_data['ip_range'].value_counts()
    normal_ip_ranges = normal_data['ip_range'].value_counts()
    
    print("\nAd_syn IP range distribution:")
    print(ad_syn_ip_ranges)
    print("\nNormal IP range distribution:")
    print(normal_ip_ranges)
    
    analysis['ip_patterns'] = {
        'ad_syn_ip_ranges': ad_syn_ip_ranges.to_dict(),
        'normal_ip_ranges': normal_ip_ranges.to_dict()
    }
    
    # 4. Packet Length Analysis
    print("\n=== PACKET LENGTH ANALYSIS ===")
    ad_syn_pkt_lens = ad_syn_data['packet_length'].describe()
    normal_pkt_lens = normal_data['packet_length'].describe()
    
    print("Ad_syn packet length statistics:")
    print(ad_syn_pkt_lens)
    print("\nNormal packet length statistics:")
    print(normal_pkt_lens)
    
    analysis['packet_length'] = {
        'ad_syn_stats': ad_syn_pkt_lens.to_dict(),
        'normal_stats': normal_pkt_lens.to_dict(),
        'ad_syn_unique_lengths': sorted(ad_syn_data['packet_length'].unique().tolist()),
        'normal_unique_lengths': sorted(normal_data['packet_length'].unique().tolist())
    }
    
    # 5. TCP Options Length Analysis
    print("\n=== TCP OPTIONS LENGTH ANALYSIS ===")
    ad_syn_tcp_opts = ad_syn_data['tcp_options_len'].value_counts()
    normal_tcp_opts = normal_data['tcp_options_len'].value_counts()
    
    print("Ad_syn TCP options length distribution:")
    print(ad_syn_tcp_opts)
    print("\nNormal TCP options length distribution:")
    print(normal_tcp_opts)
    
    analysis['tcp_options'] = {
        'ad_syn_opts': ad_syn_tcp_opts.to_dict(),
        'normal_opts': normal_tcp_opts.to_dict()
    }
    
    # 6. Source Port Analysis
    print("\n=== SOURCE PORT ANALYSIS ===")
    ad_syn_src_port_stats = ad_syn_data['src_port'].describe()
    normal_src_port_stats = normal_data['src_port'].describe()
    
    print("Ad_syn source port statistics:")
    print(ad_syn_src_port_stats)
    print("\nNormal source port statistics:")
    print(normal_src_port_stats)
    
    analysis['src_port'] = {
        'ad_syn_stats': ad_syn_src_port_stats.to_dict(),
        'normal_stats': normal_src_port_stats.to_dict()
    }
    
    # 7. TTL Analysis
    print("\n=== TTL ANALYSIS ===")
    ad_syn_ttl = ad_syn_data['ip_ttl'].value_counts()
    normal_ttl = normal_data['ip_ttl'].value_counts()
    
    print("Ad_syn TTL distribution:")
    print(ad_syn_ttl.head(10))
    print("\nNormal TTL distribution:")
    print(normal_ttl.head(10))
    
    analysis['ttl'] = {
        'ad_syn_ttl': ad_syn_ttl.head(10).to_dict(),
        'normal_ttl': normal_ttl.head(10).to_dict()
    }
    
    return analysis

if __name__ == "__main__":
    dataset_path = "/mnt/c/Users/Intel/Desktop/adddosdn/dataset_generation/main_output/v3/220725-1/packet_features_30.csv"
    
    analysis_results = analyze_ad_syn_patterns(dataset_path)
    
    # Save results
    with open('/mnt/c/Users/Intel/Desktop/adddosdn/dataset_generation/ad_syn_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\nAnalysis complete. Results saved to ad_syn_analysis.json")