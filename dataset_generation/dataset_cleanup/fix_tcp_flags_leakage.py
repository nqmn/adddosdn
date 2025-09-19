#!/usr/bin/env python3
"""
TCP Flags Leakage Prevention Script
Demonstrates proper protocol-aware feature engineering to prevent data leakage
"""

import pandas as pd
import numpy as np

def fix_tcp_flags_leakage(df):
    """
    Fix TCP flags leakage by properly handling protocol-specific features
    
    Args:
        df: DataFrame with packet features including ip_proto and tcp_flags
        
    Returns:
        DataFrame with properly encoded TCP flags
    """
    df_fixed = df.copy()
    
    # 1. Protocol-aware TCP flags encoding
    # Only TCP packets (ip_proto=6) should have meaningful TCP flags
    tcp_mask = df_fixed['ip_proto'] == 6
    
    # Set TCP flags to NaN for non-TCP protocols
    df_fixed.loc[~tcp_mask, 'tcp_flags'] = np.nan
    
    # 2. Alternative: Create protocol-agnostic behavioral features
    # Instead of raw TCP flags, extract behavioral patterns
    
    # Connection establishment attempts (SYN flag)
    df_fixed['is_connection_attempt'] = np.where(
        tcp_mask & (df_fixed['tcp_flags'].fillna(0) & 0b000010 > 0), 1, 0
    )
    
    # Connection responses (SYN+ACK)
    df_fixed['is_connection_response'] = np.where(
        tcp_mask & ((df_fixed['tcp_flags'].fillna(0) & 0b010010) == 0b010010), 1, 0
    )
    
    # Connection termination (FIN or RST)
    df_fixed['is_connection_termination'] = np.where(
        tcp_mask & (df_fixed['tcp_flags'].fillna(0) & 0b000101 > 0), 1, 0
    )
    
    # Data transfer (PSH flag)
    df_fixed['is_data_transfer'] = np.where(
        tcp_mask & (df_fixed['tcp_flags'].fillna(0) & 0b001000 > 0), 1, 0
    )
    
    # 3. Normalize by protocol context
    # Create protocol-relative features instead of absolute values
    
    # Window size relative to protocol standard
    df_fixed['tcp_window_normalized'] = np.where(
        tcp_mask,
        df_fixed['tcp_window'] / 65535.0,  # Normalize by max TCP window
        np.nan
    )
    
    return df_fixed

def create_protocol_agnostic_features(df):
    """
    Create features that work across all protocols without leaking protocol identity
    
    Args:
        df: DataFrame with packet features
        
    Returns:
        DataFrame with protocol-agnostic features
    """
    df_agnostic = df.copy()
    
    # 1. Packet size distributions (works for all protocols)
    df_agnostic['packet_size_category'] = pd.cut(
        df_agnostic['packet_length'], 
        bins=[0, 64, 128, 512, 1024, 1500, float('inf')],
        labels=['tiny', 'small', 'medium', 'large', 'jumbo', 'fragmented']
    )
    
    # 2. Traffic intensity features (protocol-agnostic)
    # These would require temporal grouping in practice
    df_agnostic['payload_entropy'] = np.random.normal(0.7, 0.2, len(df_agnostic))  # Placeholder
    df_agnostic['inter_arrival_time'] = np.random.exponential(0.1, len(df_agnostic))  # Placeholder
    
    # 3. Header complexity features
    df_agnostic['header_options_ratio'] = np.where(
        df_agnostic['ip_proto'] == 6,  # TCP
        df_agnostic['tcp_options_len'] / (df_agnostic['ip_len'] - 20),  # Relative to IP payload
        0  # No options for ICMP/UDP
    )
    
    # 4. Remove protocol-identifying features entirely
    protocol_identifiers = ['ip_proto', 'tcp_flags', 'icmp_type', 'transport_protocol']
    existing_identifiers = [col for col in protocol_identifiers if col in df_agnostic.columns]
    df_agnostic = df_agnostic.drop(columns=existing_identifiers)
    
    return df_agnostic

def validate_no_protocol_leakage(df, target_col):
    """
    Validate that protocol information cannot be inferred from features
    
    Args:
        df: DataFrame with features
        target_col: Target column name
        
    Returns:
        bool: True if no protocol leakage detected
    """
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    
    # Remove target columns and prepare features
    feature_cols = [col for col in df.columns if col not in ['Label_multi', 'Label_binary']]
    X = df[feature_cols].fillna(0)
    y = df[target_col]
    
    # Encode categorical features
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    # Test classification
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    dt = DecisionTreeClassifier(random_state=42, max_depth=10)
    dt.fit(X_train, y_train)
    
    accuracy = dt.score(X_test, y_test)
    
    # Check if ICMP flood can still be perfectly identified
    if target_col == 'Label_multi':
        y_pred = dt.predict(X_test)
        icmp_mask = y_test == 'icmp_flood'
        if icmp_mask.sum() > 0:
            icmp_accuracy = (y_pred[icmp_mask] == 'icmp_flood').mean()
            print(f"ICMP flood accuracy: {icmp_accuracy:.4f}")
            if icmp_accuracy > 0.98:
                print("❌ ICMP flood still perfectly separable - protocol leakage detected")
                return False
    
    print(f"Overall accuracy: {accuracy:.4f}")
    if accuracy > 0.95:
        print("❌ Suspiciously high accuracy - potential leakage")
        return False
    elif accuracy > 0.90:
        print("⚠️  High accuracy - monitor for leakage")
        return True
    else:
        print("✅ Reasonable accuracy - minimal leakage risk")
        return True

def main():
    """Demonstrate TCP flags leakage prevention techniques"""
    
    # Load original dataset
    print("🔧 TCP Flags Leakage Prevention Demo")
    print("=" * 50)
    
    # This would load your actual dataset
    # df = pd.read_csv("packet_features_30.csv")
    
    print("Techniques to prevent TCP flags leakage:")
    print()
    print("1. 📋 Protocol-Aware Feature Engineering:")
    print("   - Set tcp_flags=NaN for non-TCP protocols")
    print("   - Extract behavioral patterns instead of raw flags")
    print("   - Create connection_attempt, data_transfer features")
    print()
    print("2. 🔄 Protocol-Agnostic Features:")
    print("   - Packet size categories")
    print("   - Payload entropy and timing patterns")
    print("   - Header complexity ratios")
    print("   - Remove all protocol identifiers")
    print()
    print("3. ✅ Validation Checks:")
    print("   - Test classification without protocol features")
    print("   - Ensure ICMP flood not perfectly separable")
    print("   - Monitor for accuracy > 95% (leakage indicator)")

if __name__ == "__main__":
    main()