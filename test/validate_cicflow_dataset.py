#!/usr/bin/env python3
"""
CICFlow Dataset Validation Script

This script analyzes the CICFlow features CSV to validate:
1. Protocol correctness (TCP=6, UDP=17, ICMP=1)
2. Attack type distribution and validity
3. Flow characteristics by attack type
4. Label consistency and encoding
5. Enhanced traditional attack features
"""

import pandas as pd
import numpy as np
import argparse
import sys
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def load_and_validate_csv(csv_path):
    """Load CSV and perform basic validation."""
    print(f"Loading dataset from: {csv_path}")
    
    if not Path(csv_path).exists():
        print(f"❌ ERROR: File not found: {csv_path}")
        sys.exit(1)
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"❌ ERROR loading CSV: {e}")
        sys.exit(1)

def analyze_attack_distribution(df):
    """Analyze attack type distribution."""
    print("\n" + "="*60)
    print("ATTACK TYPE DISTRIBUTION ANALYSIS")
    print("="*60)
    
    if 'Attack_Type' in df.columns:
        attack_counts = df['Attack_Type'].value_counts()
        print(f"\nTotal flows: {len(df)}")
        print(f"Unique attack types: {len(attack_counts)}")
        print("\nAttack Type Distribution:")
        for attack_type, count in attack_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {attack_type:<15}: {count:>6} flows ({percentage:>6.2f}%)")
        
        return attack_counts
    else:
        print("❌ ERROR: 'Attack_Type' column not found")
        return None

def analyze_protocol_correctness(df):
    """Analyze protocol field correctness."""
    print("\n" + "="*60)
    print("PROTOCOL CORRECTNESS ANALYSIS")
    print("="*60)
    
    if 'protocol' not in df.columns:
        print("❌ ERROR: 'protocol' column not found")
        return
    
    protocol_counts = df['protocol'].value_counts()
    print(f"\nProtocol Distribution:")
    
    # Expected protocol mappings
    protocol_map = {
        1: "ICMP",
        6: "TCP", 
        17: "UDP",
        2048: "Unknown/Ethernet Type (should be 1/6/17)"
    }
    
    total_flows = len(df)
    for protocol, count in protocol_counts.items():
        protocol_name = protocol_map.get(protocol, f"Unknown ({protocol})")
        percentage = (count / total_flows) * 100
        status = "✅" if protocol in [1, 6, 17] else "❌"
        print(f"  {status} Protocol {protocol:<4} ({protocol_name:<35}): {count:>6} flows ({percentage:>6.2f}%)")
    
    # Check for protocol consistency by attack type
    if 'Attack_Type' in df.columns:
        print(f"\nProtocol by Attack Type:")
        protocol_by_attack = df.groupby(['Attack_Type', 'protocol']).size().unstack(fill_value=0)
        print(protocol_by_attack)

def analyze_flow_characteristics(df):
    """Analyze flow characteristics by attack type."""
    print("\n" + "="*60)
    print("FLOW CHARACTERISTICS ANALYSIS")
    print("="*60)
    
    required_cols = ['Attack_Type', 'src_port', 'dst_port', 'flow_duration', 'tot_fwd_pkts', 'tot_bwd_pkts']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"❌ ERROR: Missing columns: {missing_cols}")
        return
    
    # Analyze by attack type
    attack_types = df['Attack_Type'].unique()
    
    for attack_type in sorted(attack_types):
        attack_df = df[df['Attack_Type'] == attack_type]
        
        print(f"\n--- {attack_type.upper()} Analysis ---")
        print(f"Flows: {len(attack_df)}")
        
        # Port analysis
        if attack_type in ['syn_flood', 'ad_syn']:
            # Should target port 80 (HTTP)
            port_80_flows = len(attack_df[attack_df['dst_port'] == 80])
            print(f"Port 80 targets: {port_80_flows}/{len(attack_df)} ({(port_80_flows/len(attack_df)*100):.1f}%)")
            
        elif attack_type in ['udp_flood', 'ad_udp']:
            # Should target port 53 (DNS) or use realistic UDP ports
            port_53_flows = len(attack_df[attack_df['dst_port'] == 53])
            print(f"Port 53 targets: {port_53_flows}/{len(attack_df)} ({(port_53_flows/len(attack_df)*100):.1f}%)")
            
        elif attack_type == 'icmp_flood':
            # ICMP should have port -1 or no port
            icmp_ports = attack_df['dst_port'].unique()
            print(f"ICMP ports: {icmp_ports}")
        
        # Source port analysis (should be ephemeral for enhanced attacks)
        src_ports = attack_df['src_port'].dropna()
        if len(src_ports) > 0:
            ephemeral_ports = src_ports[(src_ports >= 32768) & (src_ports <= 65535)]
            ephemeral_ratio = len(ephemeral_ports) / len(src_ports) * 100
            print(f"Ephemeral source ports: {len(ephemeral_ports)}/{len(src_ports)} ({ephemeral_ratio:.1f}%)")
            
        # Flow duration analysis
        durations = attack_df['flow_duration'].dropna()
        if len(durations) > 0:
            print(f"Flow duration - Mean: {durations.mean():.3f}s, Median: {durations.median():.3f}s")
            
        # Packet count analysis
        fwd_pkts = attack_df['tot_fwd_pkts'].dropna()
        bwd_pkts = attack_df['tot_bwd_pkts'].dropna()
        if len(fwd_pkts) > 0:
            print(f"Forward packets - Mean: {fwd_pkts.mean():.1f}, Median: {fwd_pkts.median():.1f}")
        if len(bwd_pkts) > 0:
            print(f"Backward packets - Mean: {bwd_pkts.mean():.1f}, Median: {bwd_pkts.median():.1f}")

def analyze_tcp_flags(df):
    """Analyze TCP flags for SYN flood attacks."""
    print("\n" + "="*60)
    print("TCP FLAGS ANALYSIS") 
    print("="*60)
    
    tcp_attacks = df[df['Attack_Type'].isin(['syn_flood', 'ad_syn'])].copy()
    
    if len(tcp_attacks) == 0:
        print("No TCP-based attacks found for flag analysis")
        return
    
    flag_cols = ['syn_flag_cnt', 'ack_flag_cnt', 'fin_flag_cnt', 'rst_flag_cnt', 'psh_flag_cnt']
    missing_flag_cols = [col for col in flag_cols if col not in df.columns]
    
    if missing_flag_cols:
        print(f"❌ Missing flag columns: {missing_flag_cols}")
        return
    
    for attack_type in ['syn_flood', 'ad_syn']:
        attack_df = tcp_attacks[tcp_attacks['Attack_Type'] == attack_type]
        if len(attack_df) == 0:
            continue
            
        print(f"\n--- {attack_type.upper()} TCP Flags ---")
        
        for flag_col in flag_cols:
            if flag_col in attack_df.columns:
                flag_counts = attack_df[flag_col].dropna()
                if len(flag_counts) > 0:
                    flag_name = flag_col.replace('_flag_cnt', '').upper()
                    print(f"{flag_name} flags - Mean: {flag_counts.mean():.2f}, Max: {flag_counts.max()}")

def analyze_enhanced_features(df):
    """Analyze features that indicate enhanced traditional attacks."""
    print("\n" + "="*60)
    print("ENHANCED ATTACK FEATURES ANALYSIS")
    print("="*60)
    
    traditional_attacks = df[df['Attack_Type'].isin(['syn_flood', 'udp_flood', 'icmp_flood'])].copy()
    
    if len(traditional_attacks) == 0:
        print("No traditional attacks found for enhanced feature analysis")
        return
    
    print(f"Traditional attack flows: {len(traditional_attacks)}")
    
    # Analyze timing patterns (should show ~25 pps for enhanced attacks)
    if 'flow_pkts_s' in df.columns:
        for attack_type in ['syn_flood', 'udp_flood', 'icmp_flood']:
            attack_df = traditional_attacks[traditional_attacks['Attack_Type'] == attack_type]
            if len(attack_df) > 0:
                pkt_rates = attack_df['flow_pkts_s'].dropna()
                if len(pkt_rates) > 0:
                    mean_rate = pkt_rates.mean()
                    enhancement_indicator = "✅ Enhanced" if mean_rate < 50 else "❌ Traditional"
                    print(f"{attack_type}: Avg packet rate = {mean_rate:.1f} pps ({enhancement_indicator})")
    
    # Check for realistic source ports (ephemeral range)
    for attack_type in ['syn_flood', 'udp_flood']:
        attack_df = traditional_attacks[traditional_attacks['Attack_Type'] == attack_type]
        if len(attack_df) > 0 and 'src_port' in attack_df.columns:
            src_ports = attack_df['src_port'].dropna()
            ephemeral_ports = src_ports[(src_ports >= 32768) & (src_ports <= 65535)]
            if len(src_ports) > 0:
                ephemeral_ratio = len(ephemeral_ports) / len(src_ports) * 100
                enhancement_indicator = "✅ Enhanced" if ephemeral_ratio > 80 else "❌ Basic"
                print(f"{attack_type}: Ephemeral ports = {ephemeral_ratio:.1f}% ({enhancement_indicator})")

def analyze_labels_consistency(df):
    """Analyze label consistency."""
    print("\n" + "="*60)
    print("LABEL CONSISTENCY ANALYSIS")
    print("="*60)
    
    label_cols = ['Label_Multi', 'Label_Binary', 'Attack_Type']
    missing_cols = [col for col in label_cols if col not in df.columns]
    
    if missing_cols:
        print(f"❌ Missing label columns: {missing_cols}")
        return
    
    # Check Label_Binary consistency
    print("Label_Binary Consistency:")
    normal_binary = df[df['Attack_Type'] == 'normal']['Label_Binary'].unique()
    attack_binary = df[df['Attack_Type'] != 'normal']['Label_Binary'].unique()
    
    print(f"Normal traffic Label_Binary: {normal_binary}")
    print(f"Attack traffic Label_Binary: {attack_binary}")
    
    # Expected: Normal = 0, Attacks = 1
    normal_correct = all(label == 0 for label in normal_binary)
    attack_correct = all(label == 1 for label in attack_binary)
    
    print(f"Normal labeling correct: {'✅' if normal_correct else '❌'}")
    print(f"Attack labeling correct: {'✅' if attack_correct else '❌'}")
    
    # Label_Multi analysis
    print(f"\nLabel_Multi Distribution:")
    label_multi_map = df.groupby(['Attack_Type', 'Label_Multi']).size().unstack(fill_value=0)
    print(label_multi_map)

def generate_summary_report(df, attack_counts):
    """Generate final summary report."""
    print("\n" + "="*60)
    print("VALIDATION SUMMARY REPORT")
    print("="*60)
    
    total_flows = len(df)
    
    # Dataset composition
    print(f"\n📊 Dataset Composition:")
    print(f"   Total flows: {total_flows}")
    print(f"   Attack types: {len(attack_counts) if attack_counts is not None else 'Unknown'}")
    
    # Protocol validation
    if 'protocol' in df.columns:
        protocol_2048_count = len(df[df['protocol'] == 2048])
        protocol_correct_count = len(df[df['protocol'].isin([1, 6, 17])])
        
        print(f"\n🔍 Protocol Validation:")
        print(f"   Correct protocols (1/6/17): {protocol_correct_count}/{total_flows} ({(protocol_correct_count/total_flows*100):.1f}%)")
        print(f"   Incorrect protocol (2048): {protocol_2048_count}/{total_flows} ({(protocol_2048_count/total_flows*100):.1f}%)")
    
    # Enhanced attacks validation
    traditional_count = len(df[df['Attack_Type'].isin(['syn_flood', 'udp_flood', 'icmp_flood'])])
    adversarial_count = len(df[df['Attack_Type'].isin(['ad_syn', 'ad_udp', 'ad_slow'])])
    normal_count = len(df[df['Attack_Type'] == 'normal'])
    
    print(f"\n⚔️ Attack Category Distribution:")
    print(f"   Enhanced Traditional: {traditional_count} flows ({(traditional_count/total_flows*100):.1f}%)")
    print(f"   Adversarial: {adversarial_count} flows ({(adversarial_count/total_flows*100):.1f}%)")
    print(f"   Normal: {normal_count} flows ({(normal_count/total_flows*100):.1f}%)")
    
    # Issues and recommendations
    print(f"\n⚠️ Issues Identified:")
    issues = []
    
    if 'protocol' in df.columns and len(df[df['protocol'] == 2048]) > 0:
        issues.append("Protocol field shows 2048 instead of proper values (1=ICMP, 6=TCP, 17=UDP)")
    
    if traditional_count < adversarial_count:
        issues.append("Few enhanced traditional attack flows captured")
    
    if len(issues) == 0:
        print("   ✅ No major issues detected")
    else:
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    print(f"\n💡 Recommendations:")
    recommendations = [
        "Fix protocol encoding in packet capture/flow generation",
        "Increase duration for traditional attacks to capture more flows",
        "Verify enhanced timing features are working correctly",
        "Ensure proper port targeting (80 for SYN, 53 for UDP, -1 for ICMP)"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

def create_visualizations(df, output_dir=None):
    """Create visualization plots."""
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
    
    # Attack type distribution
    plt.figure(figsize=(12, 6))
    attack_counts = df['Attack_Type'].value_counts()
    
    plt.subplot(1, 2, 1)
    attack_counts.plot(kind='bar', color='skyblue')
    plt.title('Attack Type Distribution')
    plt.xlabel('Attack Type')
    plt.ylabel('Number of Flows')
    plt.xticks(rotation=45)
    
    # Protocol distribution
    plt.subplot(1, 2, 2)
    if 'protocol' in df.columns:
        protocol_counts = df['protocol'].value_counts()
        protocol_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Protocol Distribution')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_path / 'attack_distribution.png', dpi=300, bbox_inches='tight')
        print(f"📈 Visualizations saved to: {output_path}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Validate CICFlow Dataset')
    parser.add_argument('csv_file', help='Path to CICFlow features CSV file')
    parser.add_argument('--output-dir', '-o', help='Directory to save analysis outputs')
    parser.add_argument('--visualizations', '-v', action='store_true', help='Generate visualization plots')
    
    args = parser.parse_args()
    
    # Load dataset
    df = load_and_validate_csv(args.csv_file)
    
    # Run analyses
    attack_counts = analyze_attack_distribution(df)
    analyze_protocol_correctness(df)
    analyze_flow_characteristics(df)
    analyze_tcp_flags(df)
    analyze_enhanced_features(df)
    analyze_labels_consistency(df)
    
    # Generate summary
    generate_summary_report(df, attack_counts)
    
    # Create visualizations if requested
    if args.visualizations:
        create_visualizations(df, args.output_dir)
    
    print(f"\n✅ Analysis complete!")

if __name__ == '__main__':
    main()