#!/usr/bin/env python3
"""
Protocol-Aware Feature Engineering to Prevent Data Leakage
Demonstrates proper handling of protocol-specific features
"""

import pandas as pd
import numpy as np

def fix_protocol_leakage_in_dataset(df):
    """
    Fix protocol-specific feature leakage in existing dataset
    
    The issue: ICMP and UDP packets incorrectly have tcp_flags=8
    The fix: Protocol-aware feature engineering
    """
    df_fixed = df.copy()
    
    print("=== PROTOCOL LEAKAGE ANALYSIS ===")
    
    # Analyze current protocol distribution by tcp_flags
    if 'tcp_flags' in df_fixed.columns and 'ip_proto' in df_fixed.columns:
        protocol_flags_analysis = df_fixed.groupby(['ip_proto', 'tcp_flags']).size().unstack(fill_value=0)
        print("\nCurrent protocol vs tcp_flags distribution:")
        print(protocol_flags_analysis)
        
        # Identify the leakage pattern
        icmp_with_tcp_flags = df_fixed[(df_fixed['ip_proto'] == 1) & (df_fixed['tcp_flags'] == 8)]
        udp_with_tcp_flags = df_fixed[(df_fixed['ip_proto'] == 17) & (df_fixed['tcp_flags'] == 8)]
        
        print(f"\n❌ LEAKAGE DETECTED:")
        print(f"   ICMP packets with tcp_flags=8: {len(icmp_with_tcp_flags)}")
        print(f"   UDP packets with tcp_flags=8: {len(udp_with_tcp_flags)}")
    
    # Fix 1: Protocol-aware TCP flags
    print("\n=== APPLYING FIXES ===")
    
    if 'tcp_flags' in df_fixed.columns and 'ip_proto' in df_fixed.columns:
        # Only TCP packets (ip_proto=6) should have tcp_flags
        tcp_mask = df_fixed['ip_proto'] == 6
        
        # Set tcp_flags to NaN for non-TCP protocols  
        original_tcp_flags = df_fixed['tcp_flags'].copy()
        df_fixed.loc[~tcp_mask, 'tcp_flags'] = np.nan
        
        changes_made = (original_tcp_flags != df_fixed['tcp_flags']).sum()
        print(f"✅ Fixed {changes_made} non-TCP packets with incorrect tcp_flags")
    
    # Fix 2: Create protocol-agnostic behavioral features
    if 'tcp_flags' in df_fixed.columns and 'ip_proto' in df_fixed.columns:
        tcp_mask = df_fixed['ip_proto'] == 6
        tcp_flags_int = pd.to_numeric(df_fixed['tcp_flags'], errors='coerce')
        
        # Extract behavioral patterns that work across protocols
        df_fixed['has_connection_setup'] = np.where(
            tcp_mask & (tcp_flags_int.fillna(0) & 2 > 0), 1, 0  # SYN flag
        )
        
        df_fixed['has_data_push'] = np.where(
            tcp_mask & (tcp_flags_int.fillna(0) & 8 > 0), 1, 0  # PSH flag
        )
        
        df_fixed['has_connection_reset'] = np.where(
            tcp_mask & (tcp_flags_int.fillna(0) & 4 > 0), 1, 0  # RST flag
        )
        
        print("✅ Created protocol-agnostic behavioral features")
    
    # Fix 3: Create packet-level behavioral features (protocol-independent)
    if 'packet_length' in df_fixed.columns:
        # Packet size patterns (works for all protocols)
        df_fixed['packet_size_category'] = pd.cut(
            df_fixed['packet_length'],
            bins=[0, 64, 128, 512, 1024, 1500, float('inf')],
            labels=[0, 1, 2, 3, 4, 5]  # Numeric labels to avoid categorical leakage
        )
        
        # Header efficiency ratio
        if 'ip_len' in df_fixed.columns:
            df_fixed['header_payload_ratio'] = np.where(
                df_fixed['ip_len'] > 0,
                (df_fixed['packet_length'] - df_fixed['ip_len']) / df_fixed['packet_length'],
                0
            )
        
        print("✅ Created protocol-independent packet features")
    
    # Fix 4: Remove direct protocol identifiers for ML training
    features_to_remove_for_training = ['ip_proto', 'tcp_flags']  # Keep icmp_type, transport_protocol removed already
    
    print(f"\n=== RECOMMENDED FEATURES TO REMOVE FOR TRAINING ===")
    for feature in features_to_remove_for_training:
        if feature in df_fixed.columns:
            print(f"❌ Remove: {feature} (direct protocol identifier)")
    
    return df_fixed

def create_training_safe_features(df):
    """
    Create a version of the dataset safe for ML training without protocol leakage
    """
    df_safe = df.copy()
    
    # Remove all direct protocol identifiers
    protocol_identifiers = [
        'ip_proto',           # Direct protocol number
        'tcp_flags',          # Protocol-specific flags
        'icmp_type',          # ICMP-specific
        'icmp_code',          # ICMP-specific  
        'transport_protocol', # Direct protocol encoder
        'udp_len',            # UDP-specific
        'udp_checksum',       # UDP-specific
        'tcp_window',         # TCP-specific (major leakage source)
        'tcp_urgent',         # TCP-specific
        'tcp_options_len'     # TCP-specific
    ]
    
    # Remove existing protocol identifiers
    existing_identifiers = [col for col in protocol_identifiers if col in df_safe.columns]
    df_safe = df_safe.drop(columns=existing_identifiers)
    
    print(f"✅ Removed {len(existing_identifiers)} protocol-identifying features:")
    for feature in existing_identifiers:
        print(f"   - {feature}")
    
    # Keep only protocol-agnostic features
    safe_features = [
        'ip_ttl',             # TTL patterns (behavioral)
        'ip_flags',           # IP fragmentation (behavioral)  
        'ip_len',             # Packet size (behavioral)
        'ip_tos',             # Traffic class (behavioral)
        'packet_length',      # Total packet size (behavioral)
        # New behavioral features we created
        'has_connection_setup',
        'has_data_push', 
        'has_connection_reset',
        'packet_size_category',
        'header_payload_ratio'
    ]
    
    # Keep only safe features plus labels
    available_safe_features = [col for col in safe_features if col in df_safe.columns]
    label_columns = ['Label_multi', 'Label_binary']
    final_columns = available_safe_features + [col for col in label_columns if col in df_safe.columns]
    
    df_safe = df_safe[final_columns]
    
    print(f"\n✅ Created training-safe dataset with {len(available_safe_features)} behavioral features:")
    for feature in available_safe_features:
        print(f"   + {feature}")
    
    return df_safe

def main():
    """Demonstrate protocol-aware feature engineering"""
    print("🔧 Protocol-Aware Feature Engineering")
    print("=" * 60)
    
    print("\n📋 Key Principles to Prevent TCP Flags Leakage:")
    print("1. Protocol-Specific Features:")
    print("   - tcp_flags should ONLY exist for TCP packets (ip_proto=6)")
    print("   - ICMP packets should have tcp_flags=NaN")  
    print("   - UDP packets should have tcp_flags=NaN")
    print()
    print("2. Behavioral Feature Extraction:")
    print("   - Convert tcp_flags to behavioral patterns")
    print("   - has_connection_setup, has_data_push, etc.")
    print("   - Works across all protocol types")
    print()
    print("3. Protocol-Agnostic Features:")
    print("   - Packet size patterns, timing, header ratios")
    print("   - Remove ALL direct protocol identifiers")
    print("   - Focus on behavioral patterns, not protocol signatures")
    print()
    print("4. Data Collection Fix:")
    print("   - Fix in process_pcap_to_csv.py")
    print("   - Ensure tcp_flags only set for TCP packets")
    print("   - Validate no protocol cross-contamination")

if __name__ == "__main__":
    main()