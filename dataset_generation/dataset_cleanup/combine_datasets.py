#!/usr/bin/env python3
"""
Dataset Combination Script

This script combines all CSV files from multiple dataset directories into 
three consolidated datasets:
- packet_dataset.csv (all packet_features.csv files)
- flow_dataset.csv (all flow_features.csv files)  
- cicflow_dataset.csv (all cicflow_features_all.csv files)

The script adds a 'dataset_id' column to track the source dataset.

Usage:
    python3 combine_datasets.py [--path PATH]
    
Arguments:
    --path PATH    Path to the dataset directory (default: ../main_output/v2_main)
"""

import pandas as pd
import os
import argparse
import re
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
            logging.FileHandler('combine_datasets.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)

def find_dataset_directories(base_path):
    """Find all dataset directories matching the pattern."""
    v2_main_path = Path(base_path) / "main_output" / "v2_main"
    datasets = []
    
    if v2_main_path.exists():
        for item in v2_main_path.iterdir():
            if item.is_dir() and re.match(r'^\d{6}-\d+$', item.name):
                datasets.append(item)
    
    return sorted(datasets)

def combine_csv_files(datasets, filename, output_name, logger):
    """Combine CSV files of the same type from all datasets."""
    
    logger.info(f"Combining {filename} files into {output_name}")
    combined_data = []
    total_records = 0
    
    for dataset_dir in datasets:
        csv_path = dataset_dir / filename
        
        if csv_path.exists():
            try:
                # Read the CSV file
                df = pd.read_csv(csv_path)
                
                # Add dataset_id column
                df['dataset_id'] = dataset_dir.name
                
                # Reorder columns to put dataset_id first
                cols = ['dataset_id'] + [col for col in df.columns if col != 'dataset_id']
                df = df[cols]
                
                combined_data.append(df)
                records = len(df)
                total_records += records
                
                logger.info(f"  {dataset_dir.name}: {records:,} records loaded")
                
            except Exception as e:
                logger.error(f"  Failed to read {csv_path}: {e}")
        else:
            logger.warning(f"  {csv_path} not found - skipping")
    
    if combined_data:
        # Combine all dataframes
        final_df = pd.concat(combined_data, ignore_index=True)
        
        # Save to output directory
        output_path = Path("main_output") / "v2_main" / output_name
        final_df.to_csv(output_path, index=False)
        
        logger.info(f"  Combined dataset saved: {output_name}")
        logger.info(f"  Total records: {total_records:,}")
        logger.info(f"  Final shape: {final_df.shape}")
        
        # Show dataset distribution
        dataset_counts = final_df['dataset_id'].value_counts().sort_index()
        logger.info("  Dataset distribution:")
        for dataset_id, count in dataset_counts.items():
            logger.info(f"    {dataset_id}: {count:,} records")
        
        return True, total_records, final_df.shape
    else:
        logger.error(f"  No data found for {filename}")
        return False, 0, (0, 0)

def main():
    """Main function to combine all datasets."""
    parser = argparse.ArgumentParser(description='Combine individual datasets into unified CSV files')
    parser.add_argument('--path', default='../main_output/v2_main', 
                       help='Path to dataset directory (default: ../main_output/v2_main)')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("DATASET COMBINATION STARTED")
    logger.info("=" * 60)
    
    # Change to the specified directory
    dataset_base_path = Path(args.path)
    if not dataset_base_path.exists():
        logger.error(f"Dataset path not found: {dataset_base_path}")
        return 1
    
    original_dir = Path.cwd()
    os.chdir(dataset_base_path)
    
    try:
        # Find all dataset directories
        datasets = find_dataset_directories(".")
        
        if not datasets:
            logger.error("No dataset directories found!")
            return 1
        
        logger.info(f"Found {len(datasets)} dataset directories:")
        for dataset in datasets:
            logger.info(f"  - {dataset.name}")
        
        # Define the file combinations
        file_combinations = [
            ("packet_features.csv", "packet_dataset.csv"),
            ("flow_features.csv", "flow_dataset.csv"),
            ("cicflow_features_all.csv", "cicflow_dataset.csv")
        ]
        
        # Combine each type of file
        results = []
        total_combined_records = 0
        
        for source_filename, output_filename in file_combinations:
            logger.info(f"\n{'='*50}")
            logger.info(f"Combining {source_filename} files into {output_filename}")
            success, records, shape = combine_csv_files(datasets, source_filename, output_filename, logger)
            results.append((output_filename, success, records, shape))
            if success:
                total_combined_records += records
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("DATASET COMBINATION SUMMARY")
        logger.info(f"{'='*60}")
        
        successful_combinations = 0
        for output_name, success, records, shape in results:
            if success:
                successful_combinations += 1
                logger.info(f"✅ {output_name}: {records:,} records, shape {shape}")
            else:
                logger.error(f"❌ {output_name}: Failed to create")
        
        logger.info(f"\nTotal files created: {successful_combinations}/3")
        logger.info(f"Total records combined: {total_combined_records:,}")
        
        if successful_combinations == 3:
            logger.info("🎉 All datasets combined successfully!")
            return 0
        else:
            logger.error(f"⚠️  {3 - successful_combinations} dataset(s) failed to combine")
            return 1
    
    finally:
        # Return to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    exit(main())