#!/usr/bin/env python3
"""
Analyze PACKET dataset missing values to understand patterns and make informed decisions
"""

import pandas as pd
import numpy as np

def analyze_packet_missing_values():
    print("🔍 PACKET Dataset Missing Values Analysis")
    print("=" * 60)
    
    # Load the packet dataset
    df = pd.read_csv('main_output/packet_dataset.csv')
    total_rows = len(df)
    
    print(f"Total records: {total_rows:,}")
    print(f"Total columns: {len(df.columns)}")
    print()
    
    # Detailed missing values analysis
    missing_info = []
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / total_rows) * 100
        if missing_count > 0:
            missing_info.append({
                'column': col,
                'missing_count': missing_count,
                'missing_pct': missing_pct,
                'data_type': str(df[col].dtype),
                'non_missing': total_rows - missing_count
            })
    
    print("📊 Missing Values by Column:")
    print("-" * 70)
    print(f"{'Column':<15} {'Missing':<10} {'%':<8} {'Type':<10} {'Non-Missing':<12}")
    print("-" * 70)
    
    for info in sorted(missing_info, key=lambda x: x['missing_pct'], reverse=True):
        print(f"{info['column']:<15} {info['missing_count']:<10,} {info['missing_pct']:<8.2f} {info['data_type']:<10} {info['non_missing']:<12,}")
    print()
    
    # Analyze missing patterns by protocol
    print("🔬 Missing Values by Protocol (ip_proto):")
    print("-" * 50)
    
    if 'ip_proto' in df.columns:
        proto_analysis = df.groupby('ip_proto').agg({
            'tcp_flags': lambda x: f"{x.isnull().sum():,} ({(x.isnull().sum()/len(x)*100):.1f}%)",
            'ip_flags': lambda x: f"{x.isnull().sum():,} ({(x.isnull().sum()/len(x)*100):.1f}%)",
            'src_port': lambda x: f"{x.isnull().sum():,} ({(x.isnull().sum()/len(x)*100):.1f}%)",
            'dst_port': lambda x: f"{x.isnull().sum():,} ({(x.isnull().sum()/len(x)*100):.1f}%)"
        })
        
        # Add protocol names
        protocol_names = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        
        for proto in df['ip_proto'].unique():
            proto_name = protocol_names.get(proto, f'Proto-{proto}')
            proto_count = (df['ip_proto'] == proto).sum()
            print(f"\n{proto_name} (Protocol {proto}) - {proto_count:,} packets:")
            
            if proto in proto_analysis.index:
                for col in ['tcp_flags', 'ip_flags', 'src_port', 'dst_port']:
                    if col in proto_analysis.columns:
                        print(f"  {col:<12}: {proto_analysis.loc[proto, col]} missing")
    
    print()
    
    # Analyze missing patterns by attack type
    print("🎯 Missing Values by Attack Type:")
    print("-" * 60)
    
    attack_missing = df.groupby('Label_multi').agg({
        'tcp_flags': lambda x: (x.isnull().sum(), len(x), (x.isnull().sum()/len(x)*100)),
        'ip_flags': lambda x: (x.isnull().sum(), len(x), (x.isnull().sum()/len(x)*100)),
        'src_port': lambda x: (x.isnull().sum(), len(x), (x.isnull().sum()/len(x)*100)),
        'dst_port': lambda x: (x.isnull().sum(), len(x), (x.isnull().sum()/len(x)*100))
    })
    
    for attack in df['Label_multi'].unique():
        attack_count = (df['Label_multi'] == attack).sum()
        print(f"\n{attack} - {attack_count:,} packets:")
        
        for col in ['tcp_flags', 'ip_flags', 'src_port', 'dst_port']:
            if col in df.columns and df[col].isnull().sum() > 0:
                missing_count = df[df['Label_multi'] == attack][col].isnull().sum()
                missing_pct = (missing_count / attack_count) * 100
                print(f"  {col:<12}: {missing_count:,} missing ({missing_pct:.1f}%)")
    
    print()
    
    # Correlation analysis - do missing values occur together?
    print("🔗 Missing Value Correlation Analysis:")
    print("-" * 40)
    
    missing_cols = [info['column'] for info in missing_info]
    if len(missing_cols) > 1:
        # Create missing indicators
        missing_indicators = pd.DataFrame()
        for col in missing_cols:
            missing_indicators[f'{col}_missing'] = df[col].isnull()
        
        # Count co-occurrence patterns
        print("Missing value co-occurrence patterns:")
        
        # Check if tcp_flags and ports missing together (expected for non-TCP)
        if 'tcp_flags' in missing_cols and 'src_port' in missing_cols:
            both_missing = (df['tcp_flags'].isnull() & df['src_port'].isnull()).sum()
            print(f"  tcp_flags + ports both missing: {both_missing:,} rows")
            
        # Check if all network fields missing together
        network_cols = [col for col in missing_cols if col in ['tcp_flags', 'src_port', 'dst_port']]
        if len(network_cols) >= 2:
            all_network_missing = df[network_cols].isnull().all(axis=1).sum()
            print(f"  All network fields missing: {all_network_missing:,} rows")
            
        # Check ip_flags missing patterns
        if 'ip_flags' in missing_cols:
            ip_flags_missing = df['ip_flags'].isnull().sum()
            print(f"  ip_flags missing alone: {ip_flags_missing:,} rows")
    
    print()
    
    # Impact analysis of different strategies
    print("💡 STRATEGY IMPACT Analysis:")
    print("-" * 40)
    
    strategies = [
        ("Drop rows with ANY missing", df[missing_cols].isnull().any(axis=1).sum()),
        ("Drop rows with ALL missing", df[missing_cols].isnull().all(axis=1).sum()),
        ("Drop only tcp_flags missing", df['tcp_flags'].isnull().sum() if 'tcp_flags' in missing_cols else 0),
        ("Drop only ip_flags missing", df['ip_flags'].isnull().sum() if 'ip_flags' in missing_cols else 0),
        ("Drop only ports missing", df['src_port'].isnull().sum() if 'src_port' in missing_cols else 0)
    ]
    
    for strategy, rows_affected in strategies:
        if rows_affected > 0:
            impact_pct = (rows_affected / total_rows) * 100
            remaining = total_rows - rows_affected
            print(f"  {strategy:<25}: -{rows_affected:>6,} rows ({impact_pct:>5.1f}% loss) → {remaining:,} remain")
    
    print()
    
    # Recommendations based on analysis
    print("💭 STRATEGY RECOMMENDATIONS:")
    print("-" * 30)
    
    # Calculate expected missing patterns
    icmp_count = (df['ip_proto'] == 1).sum() if 'ip_proto' in df.columns else 0
    tcp_count = (df['ip_proto'] == 6).sum() if 'ip_proto' in df.columns else 0
    udp_count = (df['ip_proto'] == 17).sum() if 'ip_proto' in df.columns else 0
    
    print("Expected missing patterns based on protocols:")
    print(f"  ICMP packets ({icmp_count:,}): Should have NO tcp_flags, NO ports")
    print(f"  TCP packets ({tcp_count:,}): Should have tcp_flags AND ports") 
    print(f"  UDP packets ({udp_count:,}): Should have NO tcp_flags, but HAVE ports")
    
    # Actual missing analysis
    if 'tcp_flags' in missing_cols:
        tcp_flags_missing = df['tcp_flags'].isnull().sum()
        expected_tcp_flags_missing = icmp_count + udp_count
        print(f"\n  Actual tcp_flags missing: {tcp_flags_missing:,}")
        print(f"  Expected tcp_flags missing: {expected_tcp_flags_missing:,} (ICMP + UDP)")
        
        if abs(tcp_flags_missing - expected_tcp_flags_missing) < total_rows * 0.01:  # Within 1%
            print("  ✅ tcp_flags missing pattern matches protocol expectations")
        else:
            print("  ⚠️  tcp_flags missing pattern doesn't match protocol expectations")
    
    if 'src_port' in missing_cols:
        ports_missing = df['src_port'].isnull().sum()
        expected_ports_missing = icmp_count
        print(f"\n  Actual ports missing: {ports_missing:,}")
        print(f"  Expected ports missing: {expected_ports_missing:,} (ICMP only)")
        
        if abs(ports_missing - expected_ports_missing) < total_rows * 0.01:  # Within 1%
            print("  ✅ Port missing pattern matches protocol expectations")
        else:
            print("  ⚠️  Port missing pattern doesn't match protocol expectations")
    
    print(f"\n🎯 RECOMMENDATION:")
    print("Since missing values appear to be protocol-specific (not random):")
    print("1. 🔄 IMPUTE based on protocol:")
    print("   - tcp_flags: Keep NULL for ICMP/UDP (correct behavior)")
    print("   - src_port/dst_port: Keep NULL for ICMP (correct behavior)")
    print("   - ip_flags: Investigate why 60.7% missing - may need protocol-specific handling")
    print("\n2. 🏷️  CREATE INDICATOR FEATURES:")
    print("   - has_tcp_flags, has_ports, has_ip_flags")
    print("   - These missing patterns may be valuable attack signatures")
    print("\n3. ❌ AVOID row deletion due to low sample size")
    
    return {
        'total_rows': total_rows,
        'missing_info': missing_info,
        'protocol_counts': {'icmp': icmp_count, 'tcp': tcp_count, 'udp': udp_count}
    }

if __name__ == "__main__":
    results = analyze_packet_missing_values()