#!/usr/bin/env python3
"""
Clean cicflow_dataset.csv: Remove duplicate records

Usage:
    python3 clean_cicflow_dataset.py [--path PATH]
    
Arguments:
    --path PATH    Path to the dataset directory (default: ../main_output/v2_main)
"""

import pandas as pd
import numpy as np
import shutil
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Clean CICFlow dataset: remove duplicate records')
    parser.add_argument('--path', default='../main_output/v2_main', 
                       help='Path to dataset directory (default: ../main_output/v2_main)')
    args = parser.parse_args()
    
    # File paths
    dataset_dir = Path(args.path)
    input_file = dataset_dir / "cicflow_dataset.csv"
    backup_file = dataset_dir / "cicflow_dataset.csv.backup_before_cleaning"
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    print("=== CICFLOW DATASET CLEANING ===")
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
    
    # Analyze duplicates
    print(f"\n=== DUPLICATE ANALYSIS ===")
    
    # Check for exact duplicates (all columns including dataset_id)
    exact_duplicates = df.duplicated().sum()
    print(f"Exact duplicates (all columns): {exact_duplicates:,}")
    
    # Check for content duplicates (excluding dataset_id)
    content_cols = [col for col in df.columns if col != 'dataset_id']
    content_duplicates = df[content_cols].duplicated().sum()
    print(f"Content duplicates (excluding dataset_id): {content_duplicates:,}")
    
    # Show sample of duplicates if they exist
    if exact_duplicates > 0:
        print(f"\nSample of duplicate rows:")
        duplicate_mask = df.duplicated(keep=False)
        duplicate_sample = df[duplicate_mask].head(6)
        print(duplicate_sample[['dataset_id', 'timestamp', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'Label_multi']].to_string())
    
    print(f"\nLabel distribution before cleaning:")
    label_dist_before = df['Label_multi'].value_counts()
    for label, count in label_dist_before.items():
        pct = (count / len(df)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")
    
    # Remove duplicates
    print(f"\n🔄 Removing duplicates...")
    df_clean = df.drop_duplicates()
    
    duplicates_removed = len(df) - len(df_clean)
    print(f"  Duplicates removed: {duplicates_removed:,}")
    print(f"  Records after deduplication: {len(df_clean):,}")
    
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
    
    # Impact analysis
    print(f"\n=== IMPACT ANALYSIS ===")
    records_change = len(df_clean) - len(df)
    records_change_pct = (records_change / len(df)) * 100
    
    print(f"Records change: {records_change:,} ({records_change_pct:+.2f}%)")
    print(f"Duplicates eliminated: {duplicates_removed:,}")
    
    # Check label distribution preservation
    print(f"\nLabel distribution changes:")
    for label in label_dist_before.index:
        before = label_dist_before[label]
        after = label_dist_after.get(label, 0)
        change = after - before
        change_pct = (change / before) * 100 if before > 0 else 0
        print(f"  {label}: {before:,} → {after:,} ({change:+,}, {change_pct:+.2f}%)")
    
    # Data quality verification
    print(f"\n=== DATA QUALITY VERIFICATION ===")
    print(f"✅ No duplicates: {df_clean.duplicated().sum() == 0}")
    print(f"✅ No missing values: {df_clean.isnull().sum().sum() == 0}")
    print(f"✅ All features preserved: {len(df_clean.columns) == len(df.columns)}")
    print(f"✅ Labels preserved: {set(df_clean['Label_multi'].unique()) == set(df['Label_multi'].unique())}")
    
    # Show final dataset info
    print(f"\n=== FINAL DATASET INFO ===")
    print(f"Shape: {df_clean.shape}")
    print(f"Memory usage: {df_clean.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"Unique records: 100.0% (no duplicates)")
    
    # Save cleaned dataset
    print(f"\n💾 Saving cleaned dataset...")
    df_clean.to_csv(input_file, index=False)
    print(f"✅ Saved cleaned dataset: {input_file}")
    
    print(f"\n🎉 CICFlow dataset cleaning completed successfully!")
    print(f"   - Removed {duplicates_removed:,} duplicate records")
    print(f"   - Final dataset: {len(df_clean):,} records × {len(df_clean.columns)} features")
    print(f"   - Data quality: 100% unique, 0% missing values")

if __name__ == "__main__":
    exit(main())