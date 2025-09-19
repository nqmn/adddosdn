#!/usr/bin/env python3
"""
Remove Unknown Labels Script for Combined Datasets

This script checks and removes records with 'unknown' labels from the combined datasets:
- packet_dataset.csv
- flow_dataset.csv
- cicflow_dataset.csv

The script provides detailed analysis before and after removal, with backup functionality.

Usage:
    python3 remove_unknown_labels.py [--version VERSION] [--dry-run]
    
Arguments:
    --version VERSION    Version directory to process (default: v3)
    --dry-run           Only analyze without making changes
"""

import pandas as pd
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime

def setup_logging(log_path=None):
    """Set up logging configuration."""
    log_file = log_path if log_path else 'remove_unknown_labels.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode='w')
        ]
    )
    return logging.getLogger(__name__)

def analyze_dataset_labels(csv_path, dataset_name, logger):
    """Analyze labels in a dataset and return statistics."""
    if not csv_path.exists():
        logger.warning(f"{dataset_name} not found: {csv_path}")
        return None
    
    try:
        # Read dataset
        logger.info(f"Analyzing {dataset_name}...")
        df = pd.read_csv(csv_path)
        
        # Check if Label_multi column exists
        if 'Label_multi' not in df.columns:
            logger.error(f"Label_multi column not found in {dataset_name}")
            return None
        
        # Get label statistics
        label_counts = df['Label_multi'].value_counts()
        total_records = len(df)
        unique_labels = len(label_counts)
        unknown_count = label_counts.get('unknown', 0)
        unknown_percentage = (unknown_count / total_records * 100) if total_records > 0 else 0
        
        analysis = {
            'dataset_name': dataset_name,
            'csv_path': csv_path,
            'total_records': total_records,
            'unique_labels': unique_labels,
            'unknown_count': unknown_count,
            'unknown_percentage': unknown_percentage,
            'label_distribution': label_counts.to_dict(),
            'dataframe': df
        }
        
        logger.info(f"{dataset_name} Analysis:")
        logger.info(f"  Total records: {total_records:,}")
        logger.info(f"  Unique labels: {unique_labels}")
        logger.info(f"  Unknown records: {unknown_count:,} ({unknown_percentage:.2f}%)")
        
        # Show label distribution
        if len(label_counts) <= 10:
            logger.info("  Label distribution:")
            for label, count in label_counts.items():
                pct = (count / total_records * 100)
                logger.info(f"    {label}: {count:,} ({pct:.2f}%)")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing {dataset_name}: {e}")
        return None

def create_backup(csv_path, logger):
    """Create backup of dataset file."""
    backup_path = csv_path.with_suffix('.csv.backup_before_unknown_removal')
    
    if backup_path.exists():
        logger.info(f"Backup already exists: {backup_path.name}")
        return True
    
    try:
        shutil.copy2(csv_path, backup_path)
        logger.info(f"Created backup: {backup_path.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup for {csv_path.name}: {e}")
        return False

def remove_unknown_labels(analysis, logger, dry_run=False):
    """Remove unknown labels from dataset."""
    df = analysis['dataframe']
    dataset_name = analysis['dataset_name']
    csv_path = analysis['csv_path']
    unknown_count = analysis['unknown_count']
    
    if unknown_count == 0:
        logger.info(f"{dataset_name}: No unknown labels to remove")
        return True
    
    # Filter out unknown labels
    logger.info(f"{dataset_name}: Removing {unknown_count:,} unknown records...")
    
    if dry_run:
        logger.info(f"DRY RUN: Would remove {unknown_count:,} records from {dataset_name}")
        filtered_df = df[df['Label_multi'] != 'unknown']
        logger.info(f"DRY RUN: {dataset_name} would have {len(filtered_df):,} records after removal")
        return True
    
    # Create backup before modification
    if not create_backup(csv_path, logger):
        logger.error(f"Failed to create backup for {dataset_name}, skipping removal")
        return False
    
    # Remove unknown labels
    filtered_df = df[df['Label_multi'] != 'unknown']
    records_removed = len(df) - len(filtered_df)
    
    try:
        # Save filtered dataset
        filtered_df.to_csv(csv_path, index=False)
        
        # Verify removal
        final_count = len(filtered_df)
        logger.info(f"{dataset_name}: Successfully removed {records_removed:,} unknown records")
        logger.info(f"{dataset_name}: Final record count: {final_count:,}")
        
        # Show final label distribution
        final_labels = filtered_df['Label_multi'].value_counts()
        logger.info(f"{dataset_name}: Final label distribution:")
        for label, count in final_labels.items():
            pct = (count / final_count * 100)
            logger.info(f"  {label}: {count:,} ({pct:.2f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save filtered {dataset_name}: {e}")
        return False

def analyze_dataset_consistency(analyses, logger):
    """Analyze consistency across datasets after unknown removal."""
    logger.info("\n" + "="*80)
    logger.info("CROSS-DATASET CONSISTENCY ANALYSIS")
    logger.info("="*80)
    
    # Get all unique labels across datasets
    all_labels = set()
    dataset_labels = {}
    
    for analysis in analyses:
        if analysis and analysis['dataframe'] is not None:
            labels = set(analysis['dataframe']['Label_multi'].unique())
            labels.discard('unknown')  # Remove unknown for consistency check
            all_labels.update(labels)
            dataset_labels[analysis['dataset_name']] = labels
    
    logger.info(f"Total unique labels across all datasets: {len(all_labels)}")
    logger.info(f"Labels: {sorted(all_labels)}")
    
    # Check which labels are in which datasets
    label_coverage = {}
    for label in sorted(all_labels):
        datasets_with_label = []
        for dataset_name, labels in dataset_labels.items():
            if label in labels:
                datasets_with_label.append(dataset_name)
        
        label_coverage[label] = datasets_with_label
        coverage_count = len(datasets_with_label)
        total_datasets = len(dataset_labels)
        
        if coverage_count == total_datasets:
            status = "✅ ALL DATASETS"
        elif coverage_count == total_datasets - 1:
            status = "⚠️  MISSING FROM 1"
        else:
            status = f"❌ MISSING FROM {total_datasets - coverage_count}"
        
        logger.info(f"  {label}: {status} ({', '.join(datasets_with_label)})")
    
    # Calculate consistency score
    full_coverage_labels = sum(1 for coverage in label_coverage.values() if len(coverage) == len(dataset_labels))
    consistency_score = (full_coverage_labels / len(all_labels) * 100) if all_labels else 100
    
    logger.info(f"\nLabel Consistency Score: {consistency_score:.1f}% ({full_coverage_labels}/{len(all_labels)} labels in all datasets)")
    
    return label_coverage, consistency_score

def generate_summary_report(analyses, consistency_score, logger, dry_run=False):
    """Generate final summary report."""
    logger.info("\n" + "="*80)
    logger.info("UNKNOWN LABEL REMOVAL SUMMARY")
    logger.info("="*80)
    
    total_unknown_removed = 0
    total_records_before = 0
    total_records_after = 0
    successful_datasets = 0
    
    for analysis in analyses:
        if analysis:
            unknown_count = analysis['unknown_count']
            total_records = analysis['total_records']
            
            total_unknown_removed += unknown_count
            total_records_before += total_records
            
            if not dry_run and unknown_count > 0:
                # Calculate final count (total - unknown)
                final_count = total_records - unknown_count
                total_records_after += final_count
            elif dry_run:
                final_count = total_records - unknown_count
                total_records_after += final_count
            else:
                total_records_after += total_records
            
            if unknown_count == 0 or not dry_run:
                successful_datasets += 1
    
    if not dry_run:
        operation = "REMOVED"
        status = "COMPLETED"
    else:
        operation = "WOULD REMOVE"
        status = "DRY RUN COMPLETED"
    
    logger.info(f"Operation: {status}")
    logger.info(f"Datasets processed: {successful_datasets}/{len([a for a in analyses if a is not None])}")
    logger.info(f"Total unknown records {operation.lower()}: {total_unknown_removed:,}")
    logger.info(f"Total records before: {total_records_before:,}")
    logger.info(f"Total records after: {total_records_after:,}")
    
    if total_records_before > 0:
        reduction_percentage = (total_unknown_removed / total_records_before * 100)
        logger.info(f"Data reduction: {reduction_percentage:.2f}%")
    
    logger.info(f"Label consistency score: {consistency_score:.1f}%")
    
    # Final assessment
    if total_unknown_removed == 0:
        logger.info("🎉 No unknown labels found - datasets are clean!")
    elif consistency_score >= 90:
        logger.info("✅ Unknown labels successfully removed - datasets ready for ML!")
    elif consistency_score >= 70:
        logger.info("⚠️  Unknown labels removed but some label inconsistencies remain")
    else:
        logger.error("❌ Significant label inconsistencies detected across datasets")

def main():
    """Main function to remove unknown labels from combined datasets."""
    parser = argparse.ArgumentParser(description='Remove unknown labels from combined datasets')
    parser.add_argument('--path', default='../main_output/v3', help='Path to dataset directory (default: ../main_output/v3)')
    parser.add_argument('--dry-run', action='store_true', help='Only analyze without making changes')
    
    args = parser.parse_args()
    
    # Determine dataset path
    dataset_path = Path(args.path)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset directory not found: {dataset_path}")
        return 1
    
    # Set up logging to dataset directory
    log_path = dataset_path / "remove_unknown_labels.log"
    logger = setup_logging(log_path)
    
    operation = "DRY RUN - " if args.dry_run else ""
    logger.info(f"🧹 {operation}Remove Unknown Labels from Combined Datasets")
    logger.info(f"📁 Dataset directory: {dataset_path.absolute()}")
    
    # Define combined dataset files
    datasets = [
        (dataset_path / "packet_dataset.csv", "Packet Dataset"),
        (dataset_path / "flow_dataset.csv", "Flow Dataset"),
        (dataset_path / "cicflow_dataset.csv", "CICFlow Dataset")
    ]
    
    # Analyze all datasets
    analyses = []
    logger.info(f"\n{'='*60}")
    logger.info("ANALYZING DATASETS FOR UNKNOWN LABELS")
    logger.info(f"{'='*60}")
    
    for csv_path, dataset_name in datasets:
        analysis = analyze_dataset_labels(csv_path, dataset_name, logger)
        analyses.append(analysis)
    
    # Check if any datasets have unknown labels
    unknown_found = any(analysis and analysis['unknown_count'] > 0 for analysis in analyses)
    
    if not unknown_found:
        logger.info("\n🎉 No unknown labels found in any dataset!")
        logger.info("All datasets are already clean and ready for ML training.")
        return 0
    
    # Remove unknown labels from datasets
    logger.info(f"\n{'='*60}")
    logger.info(f"{operation.upper()}REMOVING UNKNOWN LABELS")
    logger.info(f"{'='*60}")
    
    success_count = 0
    for analysis in analyses:
        if analysis:
            if remove_unknown_labels(analysis, logger, dry_run=args.dry_run):
                success_count += 1
    
    # Analyze dataset consistency after removal
    if not args.dry_run:
        # Re-analyze datasets after unknown removal for consistency check
        post_removal_analyses = []
        for csv_path, dataset_name in datasets:
            analysis = analyze_dataset_labels(csv_path, dataset_name, logger)
            post_removal_analyses.append(analysis)
        
        label_coverage, consistency_score = analyze_dataset_consistency(post_removal_analyses, logger)
    else:
        # For dry run, analyze what would remain after unknown removal
        simulated_analyses = []
        for analysis in analyses:
            if analysis and analysis['dataframe'] is not None:
                # Create simulated analysis without unknown labels
                filtered_df = analysis['dataframe'][analysis['dataframe']['Label_multi'] != 'unknown']
                simulated_analysis = analysis.copy()
                simulated_analysis['dataframe'] = filtered_df
                simulated_analyses.append(simulated_analysis)
        
        label_coverage, consistency_score = analyze_dataset_consistency(simulated_analyses, logger)
    
    # Generate final summary
    generate_summary_report(analyses, consistency_score, logger, dry_run=args.dry_run)
    
    # Return appropriate exit code
    if success_count == len([a for a in analyses if a is not None]):
        logger.info(f"\n🎉 {operation}Operation completed successfully!")
        return 0
    else:
        logger.error(f"\n❌ Some datasets failed to process")
        return 1

if __name__ == "__main__":
    exit(main())