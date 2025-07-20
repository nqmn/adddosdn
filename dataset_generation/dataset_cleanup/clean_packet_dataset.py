#!/usr/bin/env python3
"""
Clean packet_dataset.csv: Remove duplicates and encode missing values as -1

Usage:
    python3 clean_packet_dataset.py [--path PATH]
    
Arguments:
    --path PATH    Path to the dataset directory (default: ../main_output/v2_main)
"""

import pandas as pd
import numpy as np
import shutil
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Clean packet dataset: remove duplicates and encode missing values as -1')
    parser.add_argument('--path', default='../main_output/v2_main', 
                       help='Path to dataset directory (default: ../main_output/v2_main)')
    args = parser.parse_args()
    
    # File paths
    dataset_dir = Path(args.path)
    input_file = dataset_dir / "packet_dataset.csv"
    backup_file = dataset_dir / "packet_dataset.csv.backup_before_cleaning"
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    print("=== PACKET DATASET CLEANING ===")
    print(f"Input file: {input_file}")
    
    # Create backup
    if not backup_file.exists():
        shutil.copy2(input_file, backup_file)
        print(f"✅ Created backup: {backup_file.name}")
    else:
        print(f"ℹ️ Backup already exists: {backup_file.name}")
    
    # Read dataset
    print("\n📖 Reading dataset...")
    df = pd.read_csv(input_file)
    
    # Initial statistics
    print(f"\n=== BEFORE CLEANING ===")
    print(f"Total records: {len(df):,}")
    print(f"Total features: {len(df.columns)}")
    print(f"Duplicates: {df.duplicated().sum():,}")
    print(f"Missing values: {df.isnull().sum().sum():,}")
    
    print(f"\nMissing values by column:")
    missing_before = df.isnull().sum()
    for col, count in missing_before.items():
        if count > 0:
            pct = (count / len(df)) * 100
            print(f"  {col}: {count:,} ({pct:.1f}%)")
    
    print(f"\nLabel distribution:")
    label_dist_before = df['Label_multi'].value_counts()
    for label, count in label_dist_before.items():
        pct = (count / len(df)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")
    
    # Step 1: Remove duplicates
    print(f"\n🔄 Step 1: Removing duplicates...")
    duplicates_before = df.duplicated().sum()
    df_clean = df.drop_duplicates()
    duplicates_removed = len(df) - len(df_clean)
    
    print(f"  Duplicates found: {duplicates_before:,}")
    print(f"  Duplicates removed: {duplicates_removed:,}")
    print(f"  Records after deduplication: {len(df_clean):,}")
    
    # Step 2: Encode missing values as -1
    print(f"\n🔄 Step 2: Encoding missing values as -1...")
    missing_before_encoding = df_clean.isnull().sum().sum()
    
    # Apply -1 encoding to all missing values
    df_clean = df_clean.fillna(-1)
    
    missing_after_encoding = df_clean.isnull().sum().sum()
    values_encoded = missing_before_encoding - missing_after_encoding
    
    print(f"  Missing values before encoding: {missing_before_encoding:,}")
    print(f"  Missing values after encoding: {missing_after_encoding:,}")
    print(f"  Values encoded as -1: {values_encoded:,}")
    
    # Final statistics
    print(f"\n=== AFTER CLEANING ===")
    print(f"Total records: {len(df_clean):,}")
    print(f"Total features: {len(df_clean.columns)}")
    print(f"Duplicates: {df_clean.duplicated().sum():,}")
    print(f"Missing values: {df_clean.isnull().sum().sum():,}")
    
    print(f"\nLabel distribution after cleaning:")
    label_dist_after = df_clean['Label_multi'].value_counts()
    for label, count in label_dist_after.items():
        pct = (count / len(df_clean)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")
    
    # Check for any -1 values that were introduced
    print(f"\n=== -1 ENCODING VERIFICATION ===")
    for col in df_clean.columns:
        if col not in ['Label_multi', 'Label_binary']:  # Skip label columns
            neg_ones = (df_clean[col] == -1).sum()
            if neg_ones > 0:
                pct = (neg_ones / len(df_clean)) * 100
                print(f"  {col}: {neg_ones:,} values encoded as -1 ({pct:.1f}%)")
    
    # Impact analysis
    print(f"\n=== IMPACT ANALYSIS ===")
    records_change = len(df_clean) - len(df)
    records_change_pct = (records_change / len(df)) * 100
    print(f"Records change: {records_change:,} ({records_change_pct:+.2f}%)")
    
    # Check if label distribution was preserved
    print(f"\nLabel distribution preservation:")
    for label in label_dist_before.index:
        before = label_dist_before[label]
        after = label_dist_after.get(label, 0)
        change = after - before
        change_pct = (change / before) * 100 if before > 0 else 0
        print(f"  {label}: {before:,} → {after:,} ({change:+,}, {change_pct:+.2f}%)")
    
    # Save cleaned dataset
    print(f"\n💾 Saving cleaned dataset...")
    df_clean.to_csv(input_file, index=False)
    print(f"✅ Saved cleaned dataset: {input_file}")
    
    print(f"\n🎉 Cleaning completed successfully!")
    print(f"   - Removed {duplicates_removed:,} duplicate records")
    print(f"   - Encoded {values_encoded:,} missing values as -1")
    print(f"   - Final dataset: {len(df_clean):,} records")

if __name__ == "__main__":
    exit(main())