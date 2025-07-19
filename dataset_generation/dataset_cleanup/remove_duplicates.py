#!/usr/bin/env python3
"""
Remove Duplicates Script

This script removes duplicate rows from the combined datasets while preserving
the original files as backups.
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
            logging.FileHandler('remove_duplicates.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)

def remove_duplicates_from_file(file_path, logger):
    """Remove duplicates from a single CSV file."""
    try:
        logger.info(f"Processing {file_path.name}...")
        
        # Read the original file
        df = pd.read_csv(file_path)
        original_count = len(df)
        
        logger.info(f"  Original records: {original_count:,}")
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        logger.info(f"  Duplicates found: {duplicate_count:,}")
        
        if duplicate_count == 0:
            logger.info(f"  ✅ No duplicates found - skipping {file_path.name}")
            return True, original_count, original_count, 0
        
        # Create backup
        backup_path = file_path.with_suffix('.csv.backup_duplicates')
        if not backup_path.exists():
            df.to_csv(backup_path, index=False)
            logger.info(f"  📁 Backup created: {backup_path.name}")
        else:
            logger.info(f"  📁 Backup already exists: {backup_path.name}")
        
        # Remove duplicates (keep first occurrence)
        df_clean = df.drop_duplicates(keep='first')
        cleaned_count = len(df_clean)
        
        # Save cleaned file
        df_clean.to_csv(file_path, index=False)
        
        logger.info(f"  ✅ Cleaned records: {cleaned_count:,}")
        logger.info(f"  🗑️  Removed duplicates: {duplicate_count:,}")
        logger.info(f"  💾 Updated file: {file_path.name}")
        
        # Verify the cleaning
        df_verify = pd.read_csv(file_path)
        remaining_duplicates = df_verify.duplicated().sum()
        
        if remaining_duplicates == 0:
            logger.info(f"  ✅ Verification passed - no duplicates remain")
        else:
            logger.warning(f"  ⚠️  Verification warning - {remaining_duplicates} duplicates still found")
        
        return True, original_count, cleaned_count, duplicate_count
        
    except Exception as e:
        logger.error(f"  ❌ Error processing {file_path.name}: {e}")
        return False, 0, 0, 0

def main():
    """Main function to remove duplicates from all combined datasets."""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("DUPLICATE REMOVAL STARTED")
    logger.info("=" * 60)
    
    # Define the files to process
    base_path = Path("main_output")
    files_to_process = [
        "packet_dataset.csv",
        "flow_dataset.csv", 
        "cicflow_dataset.csv"
    ]
    
    # Track results
    results = []
    total_original = 0
    total_cleaned = 0
    total_removed = 0
    
    # Process each file
    for filename in files_to_process:
        file_path = base_path / filename
        
        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {filename}")
            continue
        
        logger.info(f"\n{'='*50}")
        success, original, cleaned, removed = remove_duplicates_from_file(file_path, logger)
        
        results.append({
            'filename': filename,
            'success': success,
            'original_count': original,
            'cleaned_count': cleaned,
            'removed_count': removed
        })
        
        if success:
            total_original += original
            total_cleaned += cleaned
            total_removed += removed
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("DUPLICATE REMOVAL SUMMARY")
    logger.info(f"{'='*60}")
    
    successful_files = 0
    for result in results:
        if result['success']:
            successful_files += 1
            logger.info(f"✅ {result['filename']}:")
            logger.info(f"   Original: {result['original_count']:,}")
            logger.info(f"   Cleaned:  {result['cleaned_count']:,}")
            logger.info(f"   Removed:  {result['removed_count']:,}")
        else:
            logger.error(f"❌ {result['filename']}: Failed to process")
    
    logger.info(f"\n📊 TOTALS:")
    logger.info(f"   Files processed: {successful_files}/{len(files_to_process)}")
    logger.info(f"   Original records: {total_original:,}")
    logger.info(f"   Cleaned records:  {total_cleaned:,}")
    logger.info(f"   Total removed:    {total_removed:,}")
    
    if total_removed > 0:
        reduction_pct = (total_removed / total_original) * 100
        logger.info(f"   Data reduction:   {reduction_pct:.2f}%")
    
    if successful_files == len(files_to_process):
        logger.info("🎉 All datasets cleaned successfully!")
        return 0
    else:
        logger.error(f"⚠️  {len(files_to_process) - successful_files} file(s) failed to process")
        return 1

if __name__ == "__main__":
    exit(main())