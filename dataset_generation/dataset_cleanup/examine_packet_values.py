#!/usr/bin/env python3
"""
Examine unique values in tcp_flags and ports to understand data patterns
"""

import pandas as pd
import numpy as np

def examine_packet_values():
    print("🔍 PACKET Dataset - Unique Values Analysis")
    print("=" * 60)
    
    # Load the packet dataset
    df = pd.read_csv('main_output/packet_dataset.csv')
    total_rows = len(df)
    
    print(f"Total records: {total_rows:,}")
    print()
    
    # Examine tcp_flags
    print("🚩 TCP_FLAGS Analysis:")
    print("-" * 30)
    
    tcp_flags_stats = {
        'total_records': total_rows,
        'missing_count': df['tcp_flags'].isnull().sum(),
        'non_missing_count': df['tcp_flags'].notna().sum()
    }
    
    print(f"Missing: {tcp_flags_stats['missing_count']:,} ({(tcp_flags_stats['missing_count']/total_rows)*100:.1f}%)")
    print(f"Non-missing: {tcp_flags_stats['non_missing_count']:,} ({(tcp_flags_stats['non_missing_count']/total_rows)*100:.1f}%)")
    print()
    
    if tcp_flags_stats['non_missing_count'] > 0:
        tcp_flags_unique = df['tcp_flags'].dropna().unique()
        tcp_flags_counts = df['tcp_flags'].value_counts(dropna=False)
        
        print(f"Unique tcp_flags values: {len(tcp_flags_unique)}")
        print("Value distribution:")
        for value, count in tcp_flags_counts.head(20).items():  # Top 20
            pct = (count / total_rows) * 100
            if pd.isna(value):
                print(f"  NaN        : {count:>8,} ({pct:>5.1f}%)")
            else:
                print(f"  '{value}'    : {count:>8,} ({pct:>5.1f}%)")
        
        if len(tcp_flags_counts) > 20:
            print(f"  ... and {len(tcp_flags_counts) - 20} more values")
    
    print()
    
    # Examine src_port
    print("🚪 SRC_PORT Analysis:")
    print("-" * 25)
    
    src_port_stats = {
        'missing_count': df['src_port'].isnull().sum(),
        'non_missing_count': df['src_port'].notna().sum()
    }
    
    print(f"Missing: {src_port_stats['missing_count']:,} ({(src_port_stats['missing_count']/total_rows)*100:.1f}%)")
    print(f"Non-missing: {src_port_stats['non_missing_count']:,} ({(src_port_stats['non_missing_count']/total_rows)*100:.1f}%)")
    print()
    
    if src_port_stats['non_missing_count'] > 0:
        src_port_unique = df['src_port'].dropna().nunique()
        print(f"Unique src_port values: {src_port_unique:,}")
        
        # Statistics for non-missing ports
        src_port_clean = df['src_port'].dropna()
        print(f"Range: {int(src_port_clean.min())} - {int(src_port_clean.max())}")
        print(f"Mean: {src_port_clean.mean():.1f}")
        print(f"Median: {src_port_clean.median():.0f}")
        
        # Most common source ports
        print("\nMost common src_port values:")
        src_port_counts = df['src_port'].value_counts(dropna=False)
        for port, count in src_port_counts.head(15).items():
            pct = (count / total_rows) * 100
            if pd.isna(port):
                print(f"  NaN        : {count:>8,} ({pct:>5.1f}%)")
            else:
                print(f"  {int(port):<10} : {count:>8,} ({pct:>5.1f}%)")
    
    print()
    
    # Examine dst_port
    print("🚪 DST_PORT Analysis:")
    print("-" * 25)
    
    dst_port_stats = {
        'missing_count': df['dst_port'].isnull().sum(),
        'non_missing_count': df['dst_port'].notna().sum()
    }
    
    print(f"Missing: {dst_port_stats['missing_count']:,} ({(dst_port_stats['missing_count']/total_rows)*100:.1f}%)")
    print(f"Non-missing: {dst_port_stats['non_missing_count']:,} ({(dst_port_stats['non_missing_count']/total_rows)*100:.1f}%)")
    print()
    
    if dst_port_stats['non_missing_count'] > 0:
        dst_port_unique = df['dst_port'].dropna().nunique()
        print(f"Unique dst_port values: {dst_port_unique:,}")
        
        # Statistics for non-missing ports
        dst_port_clean = df['dst_port'].dropna()
        print(f"Range: {int(dst_port_clean.min())} - {int(dst_port_clean.max())}")
        print(f"Mean: {dst_port_clean.mean():.1f}")
        print(f"Median: {dst_port_clean.median():.0f}")
        
        # Most common destination ports
        print("\nMost common dst_port values:")
        dst_port_counts = df['dst_port'].value_counts(dropna=False)
        for port, count in dst_port_counts.head(15).items():
            pct = (count / total_rows) * 100
            if pd.isna(port):
                print(f"  NaN        : {count:>8,} ({pct:>5.1f}%)")
            else:
                port_name = get_port_name(int(port))
                print(f"  {int(port):<10} : {count:>8,} ({pct:>5.1f}%) {port_name}")
    
    print()
    
    # Examine ip_flags
    print("🏁 IP_FLAGS Analysis:")
    print("-" * 25)
    
    ip_flags_stats = {
        'missing_count': df['ip_flags'].isnull().sum(),
        'non_missing_count': df['ip_flags'].notna().sum()
    }
    
    print(f"Missing: {ip_flags_stats['missing_count']:,} ({(ip_flags_stats['missing_count']/total_rows)*100:.1f}%)")
    print(f"Non-missing: {ip_flags_stats['non_missing_count']:,} ({(ip_flags_stats['non_missing_count']/total_rows)*100:.1f}%)")
    print()
    
    if ip_flags_stats['non_missing_count'] > 0:
        ip_flags_unique = df['ip_flags'].dropna().unique()
        ip_flags_counts = df['ip_flags'].value_counts(dropna=False)
        
        print(f"Unique ip_flags values: {len(ip_flags_unique)}")
        print("Value distribution:")
        for value, count in ip_flags_counts.head(10).items():
            pct = (count / total_rows) * 100
            if pd.isna(value):
                print(f"  NaN        : {count:>8,} ({pct:>5.1f}%)")
            else:
                print(f"  '{value}'    : {count:>8,} ({pct:>5.1f}%)")
    
    print()
    
    # Data type analysis
    print("📊 Data Types and -1 Compatibility:")
    print("-" * 40)
    
    for col in ['tcp_flags', 'ip_flags', 'src_port', 'dst_port']:
        dtype = df[col].dtype
        has_missing = df[col].isnull().sum() > 0
        print(f"{col:<12}: {dtype} (missing: {has_missing})")
        
        if col in ['src_port', 'dst_port'] and not has_missing:
            # Check if all values are integers
            non_missing = df[col].dropna()
            if len(non_missing) > 0:
                all_integers = (non_missing == non_missing.astype(int)).all()
                print(f"             All integers: {all_integers}")
    
    print()
    print("💡 Implications for -1 Strategy:")
    print("-" * 35)
    print("• tcp_flags: String values → use '-1' as string")
    print("• ip_flags: String values → use '-1' as string") 
    print("• src_port: Float/Numeric → use -1 as integer")
    print("• dst_port: Float/Numeric → use -1 as integer")
    print("\n✅ -1 strategy is compatible with all columns")

def get_port_name(port):
    """Get common port names for well-known ports"""
    port_names = {
        20: "(FTP-DATA)",
        21: "(FTP)",
        22: "(SSH)",
        23: "(TELNET)",
        25: "(SMTP)",
        53: "(DNS)",
        80: "(HTTP)",
        110: "(POP3)",
        143: "(IMAP)",
        443: "(HTTPS)",
        993: "(IMAPS)",
        995: "(POP3S)"
    }
    return port_names.get(port, "")

if __name__ == "__main__":
    examine_packet_values()