#!/usr/bin/env python3
"""
Quick script to examine what the duplicate records actually look like
"""

import pandas as pd
import numpy as np

def check_duplicates_detail(csv_file):
    print(f"=== Checking duplicates in {csv_file} ===")
    
    try:
        df = pd.read_csv(f"main_output/{csv_file}")
        print(f"Total records: {len(df):,}")
        
        # Regular duplicates (including dataset_id)
        regular_dups = df.duplicated(keep=False)  # keep=False marks all duplicates
        regular_dup_count = df.duplicated().sum()  # Only subsequent duplicates
        
        print(f"Regular duplicates (all columns): {regular_dup_count:,}")
        
        if regular_dup_count > 0:
            print("\nFirst 5 duplicate rows (all columns identical):")
            dup_rows = df[regular_dups].head(10)
            print(dup_rows.to_string())
            
            print(f"\nColumns with values in first duplicate:")
            first_dup = df[regular_dups].iloc[0]
            for col in df.columns:
                print(f"  {col}: {first_dup[col]}")
        
        # Cross-dataset duplicates (excluding dataset_id)
        if 'dataset_id' in df.columns:
            df_no_id = df.drop('dataset_id', axis=1)
            cross_dups = df_no_id.duplicated(keep=False)
            cross_dup_count = df_no_id.duplicated().sum()
            
            print(f"\nCross-dataset duplicates (excluding dataset_id): {cross_dup_count:,}")
            
            if cross_dup_count > 0:
                print("\nFirst 5 cross-dataset duplicate records:")
                cross_dup_rows = df[cross_dups][['dataset_id'] + list(df_no_id.columns[:5])].head(10)
                print(cross_dup_rows.to_string())
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"Error reading {csv_file}: {e}\n")

# Check all three datasets
datasets = ['packet_dataset.csv', 'flow_dataset.csv', 'cicflow_dataset.csv']

for dataset in datasets:
    check_duplicates_detail(dataset)