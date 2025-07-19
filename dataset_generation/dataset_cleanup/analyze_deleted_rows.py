#!/usr/bin/env python3
"""
Analyze which attack types were affected by missing value row deletions
"""

import pandas as pd

def analyze_deleted_rows():
    print("🔍 Analyzing which attack types were deleted from FLOW dataset")
    print("=" * 60)
    
    # Load original (backup) and cleaned datasets
    original_df = pd.read_csv('main_output/flow_dataset.csv.backup_missing')
    cleaned_df = pd.read_csv('main_output/flow_dataset.csv')
    
    print(f"Original dataset: {len(original_df):,} records")
    print(f"Cleaned dataset:  {len(cleaned_df):,} records")
    print(f"Deleted records:  {len(original_df) - len(cleaned_df):,}")
    print()
    
    # Analyze attack distribution in original dataset
    print("📊 ORIGINAL Dataset - Attack Type Distribution:")
    print("-" * 50)
    original_attacks = original_df['Label_multi'].value_counts().sort_index()
    for attack, count in original_attacks.items():
        pct = (count / len(original_df)) * 100
        print(f"{attack:<12}: {count:>8,} ({pct:>5.1f}%)")
    print()
    
    # Analyze attack distribution in cleaned dataset
    print("📊 CLEANED Dataset - Attack Type Distribution:")
    print("-" * 50)
    cleaned_attacks = cleaned_df['Label_multi'].value_counts().sort_index()
    for attack, count in cleaned_attacks.items():
        pct = (count / len(cleaned_df)) * 100
        print(f"{attack:<12}: {count:>8,} ({pct:>5.1f}%)")
    print()
    
    # Calculate impact per attack type
    print("📉 IMPACT Analysis - Records Lost by Attack Type:")
    print("-" * 60)
    
    total_deleted = 0
    for attack in original_attacks.index:
        original_count = original_attacks[attack]
        cleaned_count = cleaned_attacks.get(attack, 0)
        deleted_count = original_count - cleaned_count
        deleted_pct = (deleted_count / original_count) * 100
        
        total_deleted += deleted_count
        
        print(f"{attack:<12}: {deleted_count:>8,} lost ({deleted_pct:>5.1f}% of {attack})")
    
    print(f"{'TOTAL':<12}: {total_deleted:>8,} lost")
    print()
    
    # Check if deletion was uniform across attack types
    print("🎯 UNIFORMITY Analysis:")
    print("-" * 30)
    
    deletion_rates = []
    for attack in original_attacks.index:
        original_count = original_attacks[attack]
        cleaned_count = cleaned_attacks.get(attack, 0)
        deleted_count = original_count - cleaned_count
        deletion_rate = (deleted_count / original_count) * 100
        deletion_rates.append(deletion_rate)
        
    avg_deletion_rate = sum(deletion_rates) / len(deletion_rates)
    min_deletion_rate = min(deletion_rates)
    max_deletion_rate = max(deletion_rates)
    
    print(f"Average deletion rate: {avg_deletion_rate:.2f}%")
    print(f"Min deletion rate:     {min_deletion_rate:.2f}%")
    print(f"Max deletion rate:     {max_deletion_rate:.2f}%")
    print(f"Rate variation:        {max_deletion_rate - min_deletion_rate:.2f}%")
    
    if max_deletion_rate - min_deletion_rate < 1.0:
        print("✅ UNIFORM: Deletion was uniform across attack types (< 1% variation)")
    elif max_deletion_rate - min_deletion_rate < 5.0:
        print("⚠️  MOSTLY UNIFORM: Deletion mostly uniform (< 5% variation)")
    else:
        print("❌ NON-UNIFORM: Deletion significantly biased toward certain attacks")
    
    print()
    
    # Analyze which specific attack types were most affected
    print("🔍 DETAILED Impact by Attack Type:")
    print("-" * 40)
    
    attack_impact = []
    for attack in original_attacks.index:
        original_count = original_attacks[attack]
        cleaned_count = cleaned_attacks.get(attack, 0)
        deleted_count = original_count - cleaned_count
        deletion_rate = (deleted_count / original_count) * 100
        
        attack_impact.append({
            'attack': attack,
            'original': original_count,
            'cleaned': cleaned_count,
            'deleted': deleted_count,
            'rate': deletion_rate
        })
    
    # Sort by deletion rate (highest first)
    attack_impact.sort(key=lambda x: x['rate'], reverse=True)
    
    for impact in attack_impact:
        print(f"{impact['attack']:<12}: {impact['deleted']:>8,} deleted ({impact['rate']:>5.1f}%) - {impact['cleaned']:>8,} remaining")
    
    print()
    
    # Protocol analysis - try to understand WHY these rows were missing
    print("🔬 PROTOCOL Analysis (if protocol column exists):")
    print("-" * 50)
    
    if 'ip_proto' in original_df.columns:
        # Find rows that were deleted by comparing timestamps or using set difference
        # Since we can't directly identify deleted rows, we'll infer from the patterns
        
        # Check missing pattern in original data
        missing_cols = ['in_port', 'eth_src', 'eth_dst']
        if all(col in original_df.columns for col in missing_cols):
            rows_with_missing = original_df[missing_cols].isnull().any(axis=1)
            missing_data = original_df[rows_with_missing]
            
            if len(missing_data) > 0:
                print("Attack types in DELETED rows (those with missing values):")
                deleted_attacks = missing_data['Label_multi'].value_counts().sort_index()
                for attack, count in deleted_attacks.items():
                    pct_of_deleted = (count / len(missing_data)) * 100
                    pct_of_original = (count / original_attacks[attack]) * 100
                    print(f"  {attack:<12}: {count:>6,} ({pct_of_deleted:>5.1f}% of deleted, {pct_of_original:>5.1f}% of original {attack})")
            else:
                print("No missing values found in backup - analysis may be incomplete")
        else:
            print("Missing value columns not found in original dataset")
    else:
        print("Protocol column not available for analysis")

if __name__ == "__main__":
    analyze_deleted_rows()