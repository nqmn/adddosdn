#!/usr/bin/env python3
"""
Compare -1 vs 0 encoding for missing values in terms of ML interpretability
"""

import pandas as pd
import numpy as np

def analyze_encoding_options():
    print("🤖 ML Encoding Analysis: -1 vs 0 for Missing Values")
    print("=" * 60)
    
    # Load the packet dataset
    df = pd.read_csv('main_output/packet_dataset.csv')
    
    print("📊 Current Data Ranges (for collision analysis):")
    print("-" * 50)
    
    # Analyze existing value ranges for each column with missing values
    missing_columns = ['tcp_flags', 'ip_flags', 'src_port', 'dst_port']
    
    for col in missing_columns:
        print(f"\n{col.upper()}:")
        if col in ['src_port', 'dst_port']:
            # Numeric columns
            non_missing = df[col].dropna()
            if len(non_missing) > 0:
                print(f"  Type: {df[col].dtype}")
                print(f"  Range: {int(non_missing.min())} - {int(non_missing.max())}")
                print(f"  Contains 0: {'Yes' if (non_missing == 0).any() else 'No'}")
                print(f"  Contains -1: {'Yes' if (non_missing == -1).any() else 'No'}")
                print(f"  Missing count: {df[col].isnull().sum():,}")
                
                # Check if 0 or -1 would create confusion
                zero_count = (non_missing == 0).sum()
                neg_one_count = (non_missing == -1).sum()
                print(f"  Current 0 values: {zero_count}")
                print(f"  Current -1 values: {neg_one_count}")
        else:
            # String columns
            non_missing = df[col].dropna()
            unique_values = non_missing.unique()
            print(f"  Type: {df[col].dtype}")
            print(f"  Unique values: {list(unique_values)}")
            print(f"  Contains '0': {'Yes' if '0' in unique_values else 'No'}")
            print(f"  Contains '-1': {'Yes' if '-1' in unique_values else 'No'}")
            print(f"  Missing count: {df[col].isnull().sum():,}")
    
    print("\n" + "="*60)
    print("🧠 ML Algorithm Considerations:")
    print("="*60)
    
    # ML Algorithm impact analysis
    algorithms = {
        'Tree-based (RF, XGBoost)': {
            '-1': ['✅ Clear split: feature <= -0.5 (missing) vs >= 0.5 (present)',
                   '✅ Natural handling of missing indicators',
                   '✅ No confusion with valid values'],
            '0': ['⚠️  May confuse with valid port 0 (though rare)',
                  '✅ Still creates clear splits',
                  '⚠️  Less semantically clear']
        },
        'Neural Networks': {
            '-1': ['✅ Clear negative signal for missing',
                   '✅ Distinct from all positive valid values',
                   '✅ Good for embedding layers'],
            '0': ['⚠️  May interfere with ReLU activations',
                  '⚠️  Less distinct signal',
                  '⚠️  Could be confused with "neutral" state']
        },
        'Linear Models (SVM, Logistic)': {
            '-1': ['✅ Clear coefficient interpretation',
                   '✅ Distinct from positive feature space',
                   '✅ Good for regularization'],
            '0': ['⚠️  May be treated as "neutral" baseline',
                  '⚠️  Less interpretable coefficients',
                  '✅ Still mathematically valid']
        },
        'Distance-based (KNN, K-means)': {
            '-1': ['✅ Clear distance from positive values',
                   '✅ Missing values cluster together',
                   '✅ Preserves missing pattern similarity'],
            '0': ['⚠️  May artificially cluster with low values',
                  '⚠️  Less distinct missing pattern',
                  '⚠️  Could bias distance calculations']
        }
    }
    
    for algo, comparisons in algorithms.items():
        print(f"\n{algo}:")
        print("  -1 encoding:")
        for point in comparisons['-1']:
            print(f"    {point}")
        print("  0 encoding:")
        for point in comparisons['0']:
            print(f"    {point}")
    
    print("\n" + "="*60)
    print("🎯 Domain-Specific Considerations:")
    print("="*60)
    
    print("\nNetwork Security Context:")
    print("• Port 0: Technically invalid but may appear in malformed packets")
    print("• tcp_flags '0': Not a valid flag combination")
    print("• ip_flags '0': Could theoretically mean 'no flags set'")
    print("• Missing = 'not applicable' vs 'not captured' distinction important")
    
    print("\nInterpretability:")
    print("• -1: Clear 'missing/NA' semantic meaning")
    print("• 0: Could mean 'zero value' or 'missing' (ambiguous)")
    print("• Attack patterns may rely on missing indicators")
    
    print("\nFeature Engineering:")
    print("• -1: Easy to create has_feature = (feature != -1)")
    print("• 0: Harder to distinguish missing vs legitimate zero")
    
    print("\n" + "="*60)
    print("📈 Statistical Impact Analysis:")
    print("="*60)
    
    # Simulate encoding impact
    for col in ['src_port', 'dst_port']:
        if col in df.columns:
            non_missing = df[col].dropna()
            if len(non_missing) > 0:
                print(f"\n{col.upper()} Statistics:")
                print(f"  Current mean: {non_missing.mean():.1f}")
                print(f"  Current std: {non_missing.std():.1f}")
                print(f"  Current min: {non_missing.min()}")
                
                # Simulate with -1
                with_neg_one = pd.concat([non_missing, pd.Series([-1] * df[col].isnull().sum())])
                print(f"  With -1 encoding:")
                print(f"    New mean: {with_neg_one.mean():.1f}")
                print(f"    New std: {with_neg_one.std():.1f}")
                print(f"    New min: {with_neg_one.min()}")
                
                # Simulate with 0
                with_zero = pd.concat([non_missing, pd.Series([0] * df[col].isnull().sum())])
                print(f"  With 0 encoding:")
                print(f"    New mean: {with_zero.mean():.1f}")
                print(f"    New std: {with_zero.std():.1f}")
                print(f"    New min: {with_zero.min()}")
    
    print("\n" + "="*60)
    print("🏆 RECOMMENDATION:")
    print("="*60)
    
    # Count actual conflicts
    port_zeros = 0
    port_neg_ones = 0
    for col in ['src_port', 'dst_port']:
        if col in df.columns:
            non_missing = df[col].dropna()
            port_zeros += (non_missing == 0).sum()
            port_neg_ones += (non_missing == -1).sum()
    
    print(f"Conflict Analysis:")
    print(f"• Current port values of 0: {port_zeros}")
    print(f"• Current port values of -1: {port_neg_ones}")
    print(f"• tcp_flags conflicts: None (strings)")
    print(f"• ip_flags conflicts: None (strings)")
    
    if port_zeros == 0 and port_neg_ones == 0:
        print(f"\n✅ CLEAR WINNER: -1 encoding")
        print(f"Reasons:")
        print(f"• No value conflicts in current data")
        print(f"• Better ML algorithm compatibility")
        print(f"• Clear semantic meaning ('missing/not applicable')")
        print(f"• Standard practice in many ML frameworks")
        print(f"• Easier feature engineering")
        print(f"• Better interpretability")
    elif port_zeros > 0:
        print(f"\n⚠️  CONSIDERATION: {port_zeros} ports already use 0")
        print(f"• -1 still recommended to avoid confusion")
        print(f"• 0 encoding would merge 'missing' with 'port 0'")
    else:
        print(f"\n🤔 ANALYSIS NEEDED: Existing -1 values found")
    
    print(f"\n💡 FINAL RECOMMENDATION: Use -1 encoding")
    print(f"   Better for ML learning, clearer semantics, industry standard")

if __name__ == "__main__":
    analyze_encoding_options()