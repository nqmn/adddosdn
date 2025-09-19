#!/usr/bin/env python3
"""
One-hot encode categorical features in dataset

Usage:
    python3 one_hot_encode_dataset.py --input INPUT_FILE [--output OUTPUT_FILE]
    
Arguments:
    --input INPUT_FILE     Path to the input CSV file
    --output OUTPUT_FILE   Path to the output CSV file (default: input_file_one_hot.csv)
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import time

def main():
    parser = argparse.ArgumentParser(description='One-hot encode categorical features in dataset')
    parser.add_argument('--input', required=True, help='Path to the input CSV file')
    parser.add_argument('--output', help='Path to the output CSV file (default: input_file_one_hot.csv)')
    args = parser.parse_args()
    
    # File paths
    input_file = Path(args.input)
    if args.output:
        output_file = Path(args.output)
    else:
        # Create output filename with _one_hot postfix
        output_file = input_file.parent / f"{input_file.stem}_one_hot{input_file.suffix}"
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    print("=== ONE-HOT ENCODING ===")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    # Read dataset
    print("\n📖 Reading dataset...")
    start_time = time.time()
    df = pd.read_csv(input_file)
    read_time = time.time() - start_time
    
    print(f"✅ Dataset loaded in {read_time:.2f}s")
    print(f"   Records: {len(df):,}")
    print(f"   Features: {len(df.columns)}")
    
    # Remove unnecessary features for ML generalization
    print(f"\n🔄 Removing unnecessary features for ML...")
    
    # Features to remove (network-specific identifiers that hurt generalization)
    features_to_remove = [
        'eth_type',           # Constant, not informative
        'ip_src', 'ip_dst',   # Network-specific identifiers
        'src_port', 'dst_port', # Network-specific identifiers
        'udp_sport', 'udp_dport', # Network-specific identifiers
        'transport_protocol'   # Redundant with ip_proto
    ]
    
    # Remove features that exist in the dataset
    features_removed = []
    for feature in features_to_remove:
        if feature in df.columns:
            df = df.drop(columns=[feature])
            features_removed.append(feature)
            print(f"   Removed: {feature}")
    
    print(f"✅ Removed {len(features_removed)} unnecessary features")
    print(f"   Features after removal: {len(df.columns)}")
    
    # Analyze remaining categorical features
    print(f"\n🔍 Analyzing remaining features for one-hot encoding...")
    
    # Identify categorical features (typically low cardinality integer/string columns)
    categorical_features = []
    label_features = ['Label_multi', 'Label_binary']
    
    for col in df.columns:
        if col in label_features:
            continue  # Skip label columns
            
        # Check if column has low cardinality (good candidate for one-hot encoding)
        unique_values = df[col].nunique()
        total_values = len(df)
        cardinality_ratio = unique_values / total_values
        
        # Consider for one-hot encoding if:
        # 1. Less than 20 unique values, OR
        # 2. Cardinality ratio < 0.05 (less than 5% unique values)
        if unique_values <= 20 or cardinality_ratio < 0.05:
            # Skip if it's likely a continuous feature (has decimal values)
            if df[col].dtype in ['float64', 'float32']:
                # Check if all values are integers (even if stored as float)
                if not df[col].fillna(0).apply(lambda x: float(x).is_integer()).all():
                    continue
            
            categorical_features.append(col)
            print(f"   {col}: {unique_values} unique values ({cardinality_ratio:.3f} ratio)")
    
    print(f"\nFound {len(categorical_features)} categorical features for one-hot encoding")
    
    if not categorical_features:
        print("ℹ️ No categorical features found. Copying dataset without encoding...")
        df.to_csv(output_file, index=False)
        print(f"✅ Dataset copied to: {output_file}")
        return 0
    
    # Perform one-hot encoding
    print(f"\n🔄 Performing one-hot encoding...")
    encoding_start = time.time()
    
    # Create a copy of the dataframe
    df_encoded = df.copy()
    
    # Keep track of new columns
    new_columns = []
    columns_encoded = 0
    
    for col in categorical_features:
        print(f"   Encoding {col}...")
        
        # Get unique values (excluding -1 which represents missing)
        unique_vals = df[col].unique()
        unique_vals = [val for val in unique_vals if val != -1]
        unique_vals.sort()
        
        # Create one-hot encoded columns
        for val in unique_vals:
            new_col_name = f"{col}_{val}"
            df_encoded[new_col_name] = (df[col] == val).astype(int)
            new_columns.append(new_col_name)
        
        # Drop original categorical column
        df_encoded = df_encoded.drop(columns=[col])
        columns_encoded += 1
    
    encoding_time = time.time() - encoding_start
    
    print(f"✅ One-hot encoding completed in {encoding_time:.2f}s")
    print(f"   Original categorical features: {len(categorical_features)}")
    print(f"   New one-hot features: {len(new_columns)}")
    print(f"   Total features after encoding: {len(df_encoded.columns)}")
    
    # Feature summary
    print(f"\n=== FEATURE SUMMARY ===")
    print(f"Before encoding: {len(df.columns)} features")
    print(f"After encoding: {len(df_encoded.columns)} features")
    print(f"Features added: {len(df_encoded.columns) - len(df.columns)}")
    
    # Show new one-hot features
    if new_columns:
        print(f"\nNew one-hot encoded features:")
        for col in new_columns[:10]:  # Show first 10
            print(f"   {col}")
        if len(new_columns) > 10:
            print(f"   ... and {len(new_columns) - 10} more")
    
    # Check label preservation
    print(f"\n=== LABEL VERIFICATION ===")
    if 'Label_multi' in df.columns:
        original_dist = df['Label_multi'].value_counts().sort_index()
        encoded_dist = df_encoded['Label_multi'].value_counts().sort_index()
        
        print("Label distribution preserved:")
        for label in original_dist.index:
            orig_count = original_dist[label]
            enc_count = encoded_dist.get(label, 0)
            if orig_count == enc_count:
                print(f"   Label {label}: ✅ {orig_count:,} records")
            else:
                print(f"   Label {label}: ❌ {orig_count:,} → {enc_count:,}")
    
    # Save encoded dataset
    print(f"\n💾 Saving one-hot encoded dataset...")
    save_start = time.time()
    df_encoded.to_csv(output_file, index=False)
    save_time = time.time() - save_start
    
    print(f"✅ Dataset saved in {save_time:.2f}s: {output_file}")
    
    # Final summary
    total_time = time.time() - start_time
    print(f"\n🎉 One-hot encoding completed successfully!")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Input: {len(df):,} records × {len(df.columns)} features")
    print(f"   Output: {len(df_encoded):,} records × {len(df_encoded.columns)} features")
    print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    exit(main())