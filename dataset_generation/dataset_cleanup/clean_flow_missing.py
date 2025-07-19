#!/usr/bin/env python3
"""
Clean FLOW Dataset Missing Values

This script removes:
1. Columns that are 100% missing (table_id, cookie, duration_nsec)
2. Rows with missing values in network metadata columns (in_port, eth_src, eth_dst)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('clean_flow_missing.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)

def clean_flow_dataset(logger):
    """Clean the FLOW dataset by removing empty columns and rows with missing values."""
    
    file_path = Path("main_output/flow_dataset.csv")
    
    try:
        logger.info("🔍 Loading FLOW dataset...")
        df = pd.read_csv(file_path)
        original_rows = len(df)
        original_cols = len(df.columns)
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        logger.info(f"  Original: {original_rows:,} rows × {original_cols} columns")
        logger.info(f"  Original memory: {original_memory:.1f} MB")
        
        # Create backup
        backup_path = file_path.with_suffix('.csv.backup_missing')
        if not backup_path.exists():
            df.to_csv(backup_path, index=False)
            logger.info(f"  📁 Backup created: {backup_path.name}")
        else:
            logger.info(f"  📁 Backup already exists: {backup_path.name}")
        
        # Analyze missing values before cleaning
        logger.info("\n📊 Pre-cleaning analysis:")
        missing_analysis = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(df)) * 100
                missing_analysis[col] = {'count': missing_count, 'pct': missing_pct}
                logger.info(f"  {col}: {missing_count:,} missing ({missing_pct:.2f}%)")
        
        # Step 1: Drop columns that are 100% missing
        logger.info(f"\n🗑️  Step 1: Dropping 100% missing columns...")
        columns_to_drop = []
        for col, stats in missing_analysis.items():
            if stats['pct'] == 100.0:
                columns_to_drop.append(col)
        
        if columns_to_drop:
            logger.info(f"  Dropping columns: {', '.join(columns_to_drop)}")
            df_step1 = df.drop(columns=columns_to_drop)
            step1_memory = df_step1.memory_usage(deep=True).sum() / 1024 / 1024
            logger.info(f"  After column drop: {len(df_step1):,} rows × {len(df_step1.columns)} columns")
            logger.info(f"  Memory after column drop: {step1_memory:.1f} MB")
            logger.info(f"  Memory savings: {original_memory - step1_memory:.1f} MB")
        else:
            logger.info("  No 100% missing columns found")
            df_step1 = df.copy()
        
        # Step 2: Drop rows with missing values in remaining partially missing columns
        logger.info(f"\n🗑️  Step 2: Dropping rows with missing values...")
        
        # Find remaining columns with missing values
        remaining_missing_cols = []
        for col in df_step1.columns:
            if df_step1[col].isnull().sum() > 0:
                remaining_missing_cols.append(col)
        
        if remaining_missing_cols:
            logger.info(f"  Columns with missing values: {', '.join(remaining_missing_cols)}")
            
            # Count rows with any missing value
            rows_with_missing = df_step1[remaining_missing_cols].isnull().any(axis=1).sum()
            logger.info(f"  Rows with missing values: {rows_with_missing:,}")
            
            # Drop rows with missing values
            df_final = df_step1.dropna(subset=remaining_missing_cols)
            final_rows = len(df_final)
            final_memory = df_final.memory_usage(deep=True).sum() / 1024 / 1024
            
            logger.info(f"  After row drop: {final_rows:,} rows × {len(df_final.columns)} columns")
            logger.info(f"  Rows removed: {original_rows - final_rows:,}")
            logger.info(f"  Data loss: {((original_rows - final_rows) / original_rows) * 100:.2f}%")
        else:
            logger.info("  No remaining missing values found")
            df_final = df_step1.copy()
            final_rows = len(df_final)
            final_memory = df_final.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Verify no missing values remain
        logger.info(f"\n✅ Step 3: Verification...")
        remaining_missing = df_final.isnull().sum().sum()
        logger.info(f"  Total missing values remaining: {remaining_missing:,}")
        
        if remaining_missing == 0:
            logger.info("  ✅ All missing values successfully removed")
        else:
            logger.warning(f"  ⚠️  {remaining_missing} missing values still remain")
        
        # Save cleaned dataset
        logger.info(f"\n💾 Saving cleaned dataset...")
        df_final.to_csv(file_path, index=False)
        logger.info(f"  ✅ Cleaned dataset saved: {file_path.name}")
        
        # Final summary
        logger.info(f"\n📊 CLEANING SUMMARY:")
        logger.info(f"  Original: {original_rows:,} rows × {original_cols} columns ({original_memory:.1f} MB)")
        logger.info(f"  Final:    {final_rows:,} rows × {len(df_final.columns)} columns ({final_memory:.1f} MB)")
        logger.info(f"  Removed:  {original_rows - final_rows:,} rows ({original_cols - len(df_final.columns)} columns)")
        logger.info(f"  Data reduction: {((original_rows - final_rows) / original_rows) * 100:.2f}%")
        logger.info(f"  Memory savings: {original_memory - final_memory:.1f} MB")
        
        # Analyze impact by dataset and attack type
        logger.info(f"\n📋 Impact by Dataset ID:")
        dataset_impact = df_final['dataset_id'].value_counts().sort_index()
        original_dataset_counts = df['dataset_id'].value_counts().sort_index()
        
        for dataset_id in dataset_impact.index:
            original_count = original_dataset_counts[dataset_id]
            final_count = dataset_impact[dataset_id]
            loss = original_count - final_count
            loss_pct = (loss / original_count) * 100
            logger.info(f"  {dataset_id}: {final_count:,}/{original_count:,} remaining ({loss_pct:.2f}% loss)")
        
        logger.info(f"\n🎯 Impact by Attack Type:")
        attack_impact = df_final['Label_multi'].value_counts().sort_index()
        original_attack_counts = df['Label_multi'].value_counts().sort_index()
        
        for attack_type in attack_impact.index:
            original_count = original_attack_counts[attack_type]
            final_count = attack_impact[attack_type]
            loss = original_count - final_count
            loss_pct = (loss / original_count) * 100
            logger.info(f"  {attack_type:<12}: {final_count:,}/{original_count:,} remaining ({loss_pct:.2f}% loss)")
        
        return True, {
            'original_rows': original_rows,
            'final_rows': final_rows,
            'original_cols': original_cols,
            'final_cols': len(df_final.columns),
            'rows_removed': original_rows - final_rows,
            'cols_removed': original_cols - len(df_final.columns),
            'memory_savings': original_memory - final_memory,
            'missing_values_removed': remaining_missing == 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error cleaning FLOW dataset: {e}")
        return False, {}

def main():
    """Main function to clean FLOW dataset missing values."""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("FLOW DATASET MISSING VALUES CLEANING")
    logger.info("=" * 60)
    
    success, results = clean_flow_dataset(logger)
    
    if success:
        logger.info("\n🎉 FLOW dataset cleaning completed successfully!")
        return 0
    else:
        logger.error("\n❌ FLOW dataset cleaning failed!")
        return 1

if __name__ == "__main__":
    exit(main())