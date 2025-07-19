#!/usr/bin/env python3
"""
Analyze missing tcp_flags to understand if they should have specific values
"""

import pandas as pd
import numpy as np

def analyze_missing_tcp_flags():
    print("🔍 Missing TCP_FLAGS Analysis - Could They Be Inferred?")
    print("=" * 65)
    
    # Load the packet dataset
    df = pd.read_csv('main_output/packet_dataset.csv')
    
    # Separate missing and non-missing tcp_flags
    missing_tcp = df[df['tcp_flags'].isnull()]
    present_tcp = df[df['tcp_flags'].notna()]
    
    print(f"Total records: {len(df):,}")
    print(f"Missing tcp_flags: {len(missing_tcp):,} ({len(missing_tcp)/len(df)*100:.1f}%)")
    print(f"Present tcp_flags: {len(present_tcp):,} ({len(present_tcp)/len(df)*100:.1f}%)")
    print()
    
    # Analyze missing tcp_flags by protocol
    print("🔬 Missing TCP_FLAGS by Protocol:")
    print("-" * 40)
    
    missing_by_protocol = missing_tcp['ip_proto'].value_counts().sort_index()
    total_by_protocol = df['ip_proto'].value_counts().sort_index()
    
    protocol_names = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    
    for proto in total_by_protocol.index:
        proto_name = protocol_names.get(proto, f'Proto-{proto}')
        total_count = total_by_protocol[proto]
        missing_count = missing_by_protocol.get(proto, 0)
        missing_pct = (missing_count / total_count) * 100
        
        print(f"{proto_name:<6} (Proto {proto}): {missing_count:>6,}/{total_count:>6,} missing ({missing_pct:>5.1f}%)")
        
        if proto == 6:  # TCP protocol
            print(f"  ⚠️  TCP packets should ALWAYS have tcp_flags!")
            if missing_count > 0:
                print(f"  🔍 Need to investigate {missing_count:,} TCP packets with missing flags")
    
    print()
    
    # Deep dive into TCP packets with missing flags
    tcp_missing = missing_tcp[missing_tcp['ip_proto'] == 6]
    if len(tcp_missing) > 0:
        print("🚨 TCP Packets with Missing Flags (This is unusual!):")
        print("-" * 55)
        print(f"Count: {len(tcp_missing):,}")
        
        # Analyze by attack type
        print("\nBy attack type:")
        tcp_missing_attacks = tcp_missing['Label_multi'].value_counts()
        for attack, count in tcp_missing_attacks.items():
            pct = (count / len(tcp_missing)) * 100
            print(f"  {attack:<12}: {count:>6,} ({pct:>5.1f}%)")
        
        # Sample some TCP packets with missing flags
        print(f"\nSample TCP packets with missing tcp_flags:")
        print("-" * 50)
        sample_cols = ['timestamp', 'packet_length', 'ip_src', 'ip_dst', 'src_port', 'dst_port', 'Label_multi']
        tcp_sample = tcp_missing[sample_cols].head(10)
        print(tcp_sample.to_string())
    
    print()
    
    # Analyze missing tcp_flags by attack type
    print("🎯 Missing TCP_FLAGS by Attack Type:")
    print("-" * 40)
    
    missing_by_attack = missing_tcp['Label_multi'].value_counts().sort_index()
    total_by_attack = df['Label_multi'].value_counts().sort_index()
    
    for attack in total_by_attack.index:
        total_count = total_by_attack[attack]
        missing_count = missing_by_attack.get(attack, 0)
        missing_pct = (missing_count / total_count) * 100
        
        print(f"{attack:<12}: {missing_count:>6,}/{total_count:>6,} missing ({missing_pct:>5.1f}%)")
        
        # Show protocol breakdown for this attack
        if missing_count > 0:
            attack_missing = missing_tcp[missing_tcp['Label_multi'] == attack]
            attack_protocols = attack_missing['ip_proto'].value_counts().sort_index()
            protocol_str = ", ".join([f"{protocol_names.get(p, f'P{p}')}:{c}" for p, c in attack_protocols.items()])
            print(f"              Protocols: {protocol_str}")
    
    print()
    
    # Analyze patterns in similar packets to infer tcp_flags
    print("🔍 Pattern Analysis - Can We Infer Missing Flags?")
    print("-" * 50)
    
    # For TCP packets specifically
    tcp_present = present_tcp[present_tcp['ip_proto'] == 6]
    if len(tcp_present) > 0:
        print("TCP Flag patterns in existing data:")
        tcp_flag_patterns = tcp_present['tcp_flags'].value_counts()
        for flag, count in tcp_flag_patterns.items():
            pct = (count / len(tcp_present)) * 100
            print(f"  {flag:<4}: {count:>6,} ({pct:>5.1f}%)")
        
        print()
        
        # Analyze flag patterns by attack type for TCP
        print("TCP Flag patterns by attack type:")
        tcp_attack_flags = tcp_present.groupby(['Label_multi', 'tcp_flags']).size().unstack(fill_value=0)
        print(tcp_attack_flags)
    
    print()
    
    # Check if missing flags correlate with specific packet characteristics
    print("📊 Characteristics of Missing TCP_FLAGS packets:")
    print("-" * 50)
    
    if len(missing_tcp) > 0:
        # Packet length analysis
        print("Packet length distribution:")
        missing_lengths = missing_tcp['packet_length'].describe()
        present_lengths = present_tcp['packet_length'].describe()
        
        print("Missing tcp_flags packets:")
        print(f"  Mean length: {missing_lengths['mean']:.1f}")
        print(f"  Median length: {missing_lengths['50%']:.1f}")
        print(f"  Range: {missing_lengths['min']:.0f} - {missing_lengths['max']:.0f}")
        
        print("Present tcp_flags packets:")
        print(f"  Mean length: {present_lengths['mean']:.1f}")
        print(f"  Median length: {present_lengths['50%']:.1f}")
        print(f"  Range: {present_lengths['min']:.0f} - {present_lengths['max']:.0f}")
        
        # Port analysis for missing flags
        print(f"\nPort patterns in missing tcp_flags:")
        missing_src_ports = missing_tcp['src_port'].value_counts(dropna=False).head(10)
        missing_dst_ports = missing_tcp['dst_port'].value_counts(dropna=False).head(10)
        
        print("Top source ports:")
        for port, count in missing_src_ports.items():
            if pd.isna(port):
                print(f"  NaN: {count:,}")
            else:
                print(f"  {int(port)}: {count:,}")
        
        print("Top destination ports:")
        for port, count in missing_dst_ports.items():
            if pd.isna(port):
                print(f"  NaN: {count:,}")
            else:
                print(f"  {int(port)}: {count:,}")
    
    print()
    
    # Recommendation based on analysis
    print("💡 RECOMMENDATIONS:")
    print("-" * 20)
    
    # Check ICMP/UDP vs TCP missing patterns
    icmp_missing = len(missing_tcp[missing_tcp['ip_proto'] == 1])
    udp_missing = len(missing_tcp[missing_tcp['ip_proto'] == 17])
    tcp_missing_count = len(missing_tcp[missing_tcp['ip_proto'] == 6])
    
    print(f"ICMP missing flags: {icmp_missing:,} (expected - ICMP has no TCP flags)")
    print(f"UDP missing flags: {udp_missing:,} (expected - UDP has no TCP flags)")
    print(f"TCP missing flags: {tcp_missing_count:,} (unexpected - needs investigation)")
    
    if tcp_missing_count == 0:
        print("\n✅ PERFECT: All missing tcp_flags are from non-TCP protocols")
        print("   Recommendation: Use '-1' for missing flags (protocol-appropriate)")
    elif tcp_missing_count < len(missing_tcp) * 0.05:  # Less than 5%
        print(f"\n⚠️  MINOR ISSUE: {tcp_missing_count} TCP packets missing flags")
        print("   Recommendation: Investigate these specific packets")
        print("   Could be capture artifacts or malformed packets")
    else:
        print(f"\n🚨 MAJOR ISSUE: {tcp_missing_count} TCP packets missing flags")
        print("   Recommendation: Deep investigation needed")
        print("   May need protocol-specific imputation")
    
    return {
        'total_missing': len(missing_tcp),
        'icmp_missing': icmp_missing,
        'udp_missing': udp_missing,
        'tcp_missing': tcp_missing_count,
        'missing_by_attack': missing_by_attack.to_dict()
    }

if __name__ == "__main__":
    results = analyze_missing_tcp_flags()