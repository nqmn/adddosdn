#!/usr/bin/env python3
"""
Analyze missing ip_flags to see if they follow protocol-appropriate patterns like tcp_flags
"""

import pandas as pd
import numpy as np

def analyze_missing_ip_flags():
    print("🔍 Missing IP_FLAGS Analysis - Protocol Pattern Check")
    print("=" * 60)
    
    # Load the packet dataset
    df = pd.read_csv('main_output/packet_dataset.csv')
    
    # Separate missing and non-missing ip_flags
    missing_ip = df[df['ip_flags'].isnull()]
    present_ip = df[df['ip_flags'].notna()]
    
    print(f"Total records: {len(df):,}")
    print(f"Missing ip_flags: {len(missing_ip):,} ({len(missing_ip)/len(df)*100:.1f}%)")
    print(f"Present ip_flags: {len(present_ip):,} ({len(present_ip)/len(df)*100:.1f}%)")
    print()
    
    # Compare with tcp_flags pattern
    missing_tcp = df[df['tcp_flags'].isnull()]
    print("📊 Comparison with TCP_FLAGS:")
    print("-" * 35)
    print(f"Missing tcp_flags: {len(missing_tcp):,} (26.3%)")
    print(f"Missing ip_flags:  {len(missing_ip):,} (60.6%)")
    print(f"Difference: {len(missing_ip) - len(missing_tcp):,} more ip_flags missing")
    print()
    
    # Analyze missing ip_flags by protocol
    print("🔬 Missing IP_FLAGS by Protocol:")
    print("-" * 40)
    
    missing_by_protocol = missing_ip['ip_proto'].value_counts().sort_index()
    total_by_protocol = df['ip_proto'].value_counts().sort_index()
    present_by_protocol = present_ip['ip_proto'].value_counts().sort_index()
    
    protocol_names = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    
    for proto in total_by_protocol.index:
        proto_name = protocol_names.get(proto, f'Proto-{proto}')
        total_count = total_by_protocol[proto]
        missing_count = missing_by_protocol.get(proto, 0)
        present_count = present_by_protocol.get(proto, 0)
        missing_pct = (missing_count / total_count) * 100
        
        print(f"{proto_name:<6} (Proto {proto}): {missing_count:>6,}/{total_count:>6,} missing ({missing_pct:>5.1f}%)")
        print(f"               {present_count:>6,}/{total_count:>6,} present ({100-missing_pct:>5.1f}%)")
        
        # Compare with tcp_flags pattern for context
        if proto in [1, 17]:  # ICMP and UDP
            tcp_missing_for_proto = len(missing_tcp[missing_tcp['ip_proto'] == proto])
            if tcp_missing_for_proto == missing_count:
                print(f"               ✅ Same as tcp_flags pattern")
            else:
                print(f"               ⚠️  Different from tcp_flags ({tcp_missing_for_proto:,} tcp_flags missing)")
        else:  # TCP
            tcp_missing_for_proto = len(missing_tcp[missing_tcp['ip_proto'] == proto])
            if tcp_missing_for_proto == 0 and missing_count > 0:
                print(f"               🚨 TCP has ip_flags missing but tcp_flags present!")
            elif tcp_missing_for_proto == missing_count:
                print(f"               ✅ Same as tcp_flags pattern")
        print()
    
    # Analyze missing ip_flags by attack type
    print("🎯 Missing IP_FLAGS by Attack Type:")
    print("-" * 45)
    
    missing_by_attack = missing_ip['Label_multi'].value_counts().sort_index()
    total_by_attack = df['Label_multi'].value_counts().sort_index()
    
    for attack in total_by_attack.index:
        total_count = total_by_attack[attack]
        missing_count = missing_by_attack.get(attack, 0)
        missing_pct = (missing_count / total_count) * 100
        
        # Compare with tcp_flags for same attack
        tcp_missing_for_attack = len(missing_tcp[missing_tcp['Label_multi'] == attack])
        
        print(f"{attack:<12}: {missing_count:>6,}/{total_count:>6,} missing ({missing_pct:>5.1f}%)")
        
        if tcp_missing_for_attack == missing_count:
            print(f"              ✅ Same as tcp_flags pattern ({tcp_missing_for_attack:,})")
        else:
            difference = missing_count - tcp_missing_for_attack
            print(f"              ⚠️  +{difference:,} more than tcp_flags ({tcp_missing_for_attack:,} tcp_flags missing)")
        
        # Show protocol breakdown for this attack
        if missing_count > 0:
            attack_missing = missing_ip[missing_ip['Label_multi'] == attack]
            attack_protocols = attack_missing['ip_proto'].value_counts().sort_index()
            protocol_str = ", ".join([f"{protocol_names.get(p, f'P{p}')}:{c}" for p, c in attack_protocols.items()])
            print(f"              Protocols: {protocol_str}")
        print()
    
    # Deep dive into the difference - where ip_flags missing but tcp_flags present
    print("🔍 Deep Dive: IP_FLAGS Missing but TCP_FLAGS Present")
    print("-" * 55)
    
    # Find records where ip_flags missing but tcp_flags present
    ip_missing_tcp_present = df[df['ip_flags'].isnull() & df['tcp_flags'].notna()]
    
    if len(ip_missing_tcp_present) > 0:
        print(f"Records with missing ip_flags but present tcp_flags: {len(ip_missing_tcp_present):,}")
        
        # Analyze by protocol
        print("\nBy protocol:")
        proto_breakdown = ip_missing_tcp_present['ip_proto'].value_counts().sort_index()
        for proto, count in proto_breakdown.items():
            proto_name = protocol_names.get(proto, f'Proto-{proto}')
            pct = (count / len(ip_missing_tcp_present)) * 100
            print(f"  {proto_name}: {count:,} ({pct:.1f}%)")
        
        # Analyze by attack type
        print("\nBy attack type:")
        attack_breakdown = ip_missing_tcp_present['Label_multi'].value_counts().sort_index()
        for attack, count in attack_breakdown.items():
            pct = (count / len(ip_missing_tcp_present)) * 100
            total_attack = len(df[df['Label_multi'] == attack])
            attack_pct = (count / total_attack) * 100
            print(f"  {attack}: {count:,} ({pct:.1f}% of diff, {attack_pct:.1f}% of {attack})")
        
        # Sample some records
        print(f"\nSample records (tcp_flags present, ip_flags missing):")
        sample_cols = ['ip_proto', 'tcp_flags', 'ip_flags', 'src_port', 'dst_port', 'Label_multi']
        sample = ip_missing_tcp_present[sample_cols].head(10)
        print(sample.to_string())
    
    print()
    
    # Analyze what ip_flags values exist when present
    print("📋 IP_FLAGS Values When Present:")
    print("-" * 35)
    
    if len(present_ip) > 0:
        ip_flag_values = present_ip['ip_flags'].value_counts()
        print("All ip_flags values found:")
        for value, count in ip_flag_values.items():
            pct = (count / len(present_ip)) * 100
            print(f"  '{value}': {count:,} ({pct:.1f}%)")
        
        # By protocol when present
        print("\nip_flags 'DF' by protocol:")
        for proto in present_ip['ip_proto'].unique():
            proto_name = protocol_names.get(proto, f'Proto-{proto}')
            proto_present = present_ip[present_ip['ip_proto'] == proto]
            proto_total = len(df[df['ip_proto'] == proto])
            present_count = len(proto_present)
            present_pct = (present_count / proto_total) * 100
            print(f"  {proto_name}: {present_count:,}/{proto_total:,} have DF flag ({present_pct:.1f}%)")
    
    print()
    
    # Network standards analysis
    print("🌐 Network Standards Analysis:")
    print("-" * 35)
    
    print("Expected IP flag behavior:")
    print("• DF (Don't Fragment): Can appear on any IP packet")
    print("• MF (More Fragments): Only on fragmented packets") 
    print("• Reserved bit: Should be 0")
    print()
    
    print("Observations:")
    print("• Only 'DF' flag found in dataset (no fragmentation)")
    print("• 60.6% packets missing ip_flags vs 26.3% missing tcp_flags")
    print("• This suggests ip_flags capture may be incomplete")
    
    print()
    
    # Recommendation
    print("💡 RECOMMENDATIONS:")
    print("-" * 20)
    
    # Check if missing pattern makes sense
    icmp_missing_ip = len(missing_ip[missing_ip['ip_proto'] == 1])
    tcp_missing_ip = len(missing_ip[missing_ip['ip_proto'] == 6])
    udp_missing_ip = len(missing_ip[missing_ip['ip_proto'] == 17])
    
    icmp_missing_tcp = len(missing_tcp[missing_tcp['ip_proto'] == 1])
    tcp_missing_tcp = len(missing_tcp[missing_tcp['ip_proto'] == 6])
    udp_missing_tcp = len(missing_tcp[missing_tcp['ip_proto'] == 17])
    
    print("Pattern comparison:")
    print(f"ICMP: {icmp_missing_ip:,} ip_flags missing vs {icmp_missing_tcp:,} tcp_flags missing")
    print(f"TCP:  {tcp_missing_ip:,} ip_flags missing vs {tcp_missing_tcp:,} tcp_flags missing")
    print(f"UDP:  {udp_missing_ip:,} ip_flags missing vs {udp_missing_tcp:,} tcp_flags missing")
    
    if tcp_missing_ip > tcp_missing_tcp:
        tcp_difference = tcp_missing_ip - tcp_missing_tcp
        print(f"\n🚨 FINDING: {tcp_difference:,} TCP packets missing ip_flags but have tcp_flags")
        print("This suggests ip_flags capture issues, not protocol compliance")
        print("\nRecommendation for ip_flags:")
        print("• Use -1 for missing ip_flags (capture artifact)")
        print("• Missing ip_flags ≠ protocol requirement (unlike tcp_flags)")
        print("• Consider ip_flags less reliable than tcp_flags")
    else:
        print("\n✅ ip_flags follow same protocol pattern as tcp_flags")
        print("Recommendation: Use -1 (protocol-appropriate)")
    
    return {
        'total_missing_ip': len(missing_ip),
        'total_missing_tcp': len(missing_tcp),
        'difference': len(missing_ip) - len(missing_tcp),
        'tcp_with_missing_ip': len(ip_missing_tcp_present)
    }

if __name__ == "__main__":
    results = analyze_missing_ip_flags()