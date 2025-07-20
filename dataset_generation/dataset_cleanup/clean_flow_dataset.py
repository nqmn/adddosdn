#!/usr/bin/env python3
"""
Clean flow_dataset.csv: Remove empty columns and rows with missing values

Usage:
    python3 clean_flow_dataset.py [--path PATH]
    
Arguments:
    --path PATH    Path to the dataset directory (default: ../main_output/v2_main)
"""

import pandas as pd
import numpy as np
import shutil
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Clean flow dataset: remove empty columns and rows with missing values')
    parser.add_argument('--path', default='../main_output/v2_main', 
                       help='Path to dataset directory (default: ../main_output/v2_main)')
    args = parser.parse_args()
    
    # File paths
    dataset_dir = Path(args.path)
    input_file = dataset_dir / "flow_dataset.csv"
    backup_file = dataset_dir / "flow_dataset.csv.backup_before_cleaning"
    
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    print("=== FLOW DATASET CLEANING ===")
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
    print(f"Missing values: {df.isnull().sum().sum():,}")
    
    # Identify empty columns (100% missing)
    empty_columns = []
    for col in df.columns:
        if df[col].isnull().all():
            empty_columns.append(col)
    
    print(f"\nEmpty columns (100% missing): {len(empty_columns)}")
    for col in empty_columns:
        print(f"  - {col}")
    
    # Identify columns with some missing values
    partial_missing = []
    missing_counts = df.isnull().sum()
    for col, count in missing_counts.items():
        if 0 < count < len(df):
            pct = (count / len(df)) * 100
            partial_missing.append((col, count, pct))
    
    print(f"\nColumns with partial missing values: {len(partial_missing)}")
    for col, count, pct in partial_missing:
        print(f"  - {col}: {count:,} ({pct:.1f}%)")
    
    print(f"\nLabel distribution before cleaning:")
    label_dist_before = df['Label_multi'].value_counts()
    for label, count in label_dist_before.items():
        pct = (count / len(df)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")
    
    # Step 1: Remove empty columns
    print(f"\n🔄 Step 1: Removing empty columns...")
    df_clean = df.drop(columns=empty_columns)
    columns_removed = len(empty_columns)
    
    print(f"  Empty columns removed: {columns_removed}")
    print(f"  Features after column removal: {len(df_clean.columns)}")
    
    # Step 2: Remove rows with missing values
    print(f"\n🔄 Step 2: Removing rows with missing values...")
    rows_before = len(df_clean)
    missing_before = df_clean.isnull().sum().sum()
    
    # Remove any rows that still have missing values
    df_clean = df_clean.dropna()
    
    rows_after = len(df_clean)
    rows_removed = rows_before - rows_after
    missing_after = df_clean.isnull().sum().sum()
    
    print(f"  Rows before removal: {rows_before:,}")
    print(f"  Rows with missing values removed: {rows_removed:,}")
    print(f"  Rows after removal: {rows_after:,}")
    print(f"  Missing values before: {missing_before:,}")
    print(f"  Missing values after: {missing_after:,}")
    
    # Final statistics
    print(f"\n=== AFTER CLEANING ===")
    print(f"Total records: {len(df_clean):,}")
    print(f"Total features: {len(df_clean.columns)}")
    print(f"Missing values: {df_clean.isnull().sum().sum():,}")
    print(f"Duplicates: {df_clean.duplicated().sum():,}")
    
    print(f"\nRemaining columns:")
    for i, col in enumerate(df_clean.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nLabel distribution after cleaning:")
    label_dist_after = df_clean['Label_multi'].value_counts()
    for label, count in label_dist_after.items():
        pct = (count / len(df_clean)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")
    
    # Impact analysis
    print(f"\n=== IMPACT ANALYSIS ===")
    records_change = len(df_clean) - len(df)
    records_change_pct = (records_change / len(df)) * 100
    features_change = len(df_clean.columns) - len(df.columns)
    
    print(f"Records change: {records_change:,} ({records_change_pct:+.2f}%)")
    print(f"Features change: {features_change:+,}")
    print(f"Missing values eliminated: {df.isnull().sum().sum():,} → 0")
    
    # Check label distribution preservation
    print(f"\nLabel distribution preservation:")
    for label in label_dist_before.index:
        before = label_dist_before[label]
        after = label_dist_after.get(label, 0)
        change = after - before
        change_pct = (change / before) * 100 if before > 0 else 0
        print(f"  {label}: {before:,} → {after:,} ({change:+,}, {change_pct:+.2f}%)")
    
    # Data quality verification
    print(f"\n=== DATA QUALITY VERIFICATION ===")
    print(f"✅ No missing values: {df_clean.isnull().sum().sum() == 0}")
    print(f"✅ All columns have data: {all(df_clean[col].notna().any() for col in df_clean.columns)}")
    print(f"✅ Labels preserved: {set(df_clean['Label_multi'].unique()) <= set(df['Label_multi'].unique())}")
    
    # Save cleaned dataset
    print(f"\n💾 Saving cleaned dataset...")
    df_clean.to_csv(input_file, index=False)
    print(f"✅ Saved cleaned dataset: {input_file}")
    
    print(f"\n🎉 Flow dataset cleaning completed successfully!")
    print(f"   - Removed {columns_removed} empty columns")
    print(f"   - Removed {rows_removed:,} rows with missing values")
    print(f"   - Final dataset: {len(df_clean):,} records × {len(df_clean.columns)} features")

if __name__ == "__main__":
    exit(main())