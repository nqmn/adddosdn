#!/usr/bin/env python3
"""
Analyze FLOW dataset missing values to understand impact of different cleaning strategies
"""

import pandas as pd
import numpy as np

def analyze_flow_missing_values():
    print("🔍 FLOW Dataset Missing Values Analysis")
    print("=" * 60)
    
    # Load the flow dataset
    df = pd.read_csv('main_output/flow_dataset.csv')
    total_rows = len(df)
    
    print(f"Total records: {total_rows:,}")
    print(f"Total columns: {len(df.columns)}")
    print()
    
    # Analyze missing values per column
    missing_info = []
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / total_rows) * 100
        if missing_count > 0:
            missing_info.append({
                'column': col,
                'missing_count': missing_count,
                'missing_pct': missing_pct,
                'non_missing': total_rows - missing_count
            })
    
    print("📊 Missing Values by Column:")
    print("-" * 60)
    for info in sorted(missing_info, key=lambda x: x['missing_pct'], reverse=True):
        print(f"{info['column']:<15}: {info['missing_count']:>8,} ({info['missing_pct']:>6.2f}%) missing")
    print()
    
    # Identify 100% missing columns
    fully_missing = [info['column'] for info in missing_info if info['missing_pct'] == 100.0]
    partially_missing = [info['column'] for info in missing_info if 0 < info['missing_pct'] < 100.0]
    
    print("🗑️  100% Missing Columns (CANDIDATES FOR DROPPING):")
    for col in fully_missing:
        print(f"   - {col}")
    print(f"   Total: {len(fully_missing)} columns")
    print()
    
    print("⚠️  Partially Missing Columns:")
    for info in missing_info:
        if info['column'] in partially_missing:
            print(f"   - {info['column']}: {info['missing_count']:,} missing ({info['missing_pct']:.2f}%)")
    print()
    
    # Analyze impact of row deletion for partially missing
    if partially_missing:
        print("🧮 Impact Analysis: Row Deletion vs Column Imputation")
        print("-" * 60)
        
        # Find rows with ANY missing value in partially missing columns
        partial_missing_mask = df[partially_missing].isnull().any(axis=1)
        rows_with_missing = partial_missing_mask.sum()
        rows_remaining = total_rows - rows_with_missing
        
        print(f"Rows with ANY missing value in partial columns: {rows_with_missing:,}")
        print(f"Rows that would remain after deletion: {rows_remaining:,}")
        print(f"Data loss from row deletion: {(rows_with_missing/total_rows)*100:.2f}%")
        print()
        
        # Analyze by dataset_id
        print("📋 Impact by Dataset ID:")
        print("-" * 40)
        dataset_impact = df.groupby('dataset_id').apply(
            lambda x: pd.Series({
                'total_rows': len(x),
                'rows_with_missing': x[partially_missing].isnull().any(axis=1).sum(),
                'rows_remaining': len(x) - x[partially_missing].isnull().any(axis=1).sum()
            })
        )
        
        for dataset_id, data in dataset_impact.iterrows():
            loss_pct = (data['rows_with_missing'] / data['total_rows']) * 100
            print(f"{dataset_id}: {data['rows_with_missing']:,}/{data['total_rows']:,} missing ({loss_pct:.2f}% loss)")
        print()
        
        # Analyze by attack type
        print("🎯 Impact by Attack Type:")
        print("-" * 40)
        attack_impact = df.groupby('Label_multi').apply(
            lambda x: pd.Series({
                'total_rows': len(x),
                'rows_with_missing': x[partially_missing].isnull().any(axis=1).sum(),
                'rows_remaining': len(x) - x[partially_missing].isnull().any(axis=1).sum()
            })
        )
        
        for attack_type, data in attack_impact.iterrows():
            loss_pct = (data['rows_with_missing'] / data['total_rows']) * 100
            print(f"{attack_type:<12}: {data['rows_with_missing']:,}/{data['total_rows']:,} missing ({loss_pct:.2f}% loss)")
        print()
    
    # Memory and size impact
    print("💾 Memory Impact Analysis:")
    print("-" * 30)
    current_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
    print(f"Current memory usage: {current_memory:.1f} MB")
    
    if fully_missing:
        df_no_full_missing = df.drop(columns=fully_missing)
        memory_after_col_drop = df_no_full_missing.memory_usage(deep=True).sum() / 1024 / 1024
        print(f"After dropping 100% missing columns: {memory_after_col_drop:.1f} MB")
        print(f"Memory savings: {current_memory - memory_after_col_drop:.1f} MB")
        
        if partially_missing:
            df_no_missing_rows = df_no_full_missing.dropna(subset=partially_missing)
            memory_after_row_drop = df_no_missing_rows.memory_usage(deep=True).sum() / 1024 / 1024
            print(f"After also dropping rows with missing: {memory_after_row_drop:.1f} MB")
            print(f"Total memory savings: {current_memory - memory_after_row_drop:.1f} MB")
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("-" * 20)
    print("1. 🗑️  DROP 100% missing columns - no information loss")
    for col in fully_missing:
        print(f"   ✓ Drop: {col}")
    
    if partially_missing:
        rows_loss_pct = (rows_with_missing/total_rows)*100
        print(f"\n2. ⚠️  Partially missing columns ({rows_loss_pct:.2f}% row loss if deleted):")
        
        if rows_loss_pct < 5:
            print(f"   ✅ RECOMMENDATION: DROP ROWS - Low impact ({rows_loss_pct:.2f}% loss)")
            print("   Reasons:")
            print("   - Minimal data loss")
            print("   - Simpler than imputation")
            print("   - Preserves data integrity")
            print("   - No artificial values introduced")
        else:
            print(f"   ⚠️  RECOMMENDATION: CONSIDER IMPUTATION - High impact ({rows_loss_pct:.2f}% loss)")
            print("   Alternative strategies:")
            print("   - Simple imputation (mode for categorical, median for numeric)")
            print("   - Keep missing as separate category")
            print("   - Advanced imputation techniques")
    
    return {
        'total_rows': total_rows,
        'fully_missing_cols': fully_missing,
        'partially_missing_cols': partially_missing,
        'rows_with_missing': rows_with_missing if partially_missing else 0,
        'impact_by_dataset': dataset_impact.to_dict('index') if partially_missing else {},
        'impact_by_attack': attack_impact.to_dict('index') if partially_missing else {}
    }

if __name__ == "__main__":
    results = analyze_flow_missing_values()