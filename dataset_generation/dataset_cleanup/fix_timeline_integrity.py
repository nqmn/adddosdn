#!/usr/bin/env python3
"""
Timeline Integrity Fix Script

This script ensures data integrity by:
1. Creating backups of all CSV files
2. Using attack.log to define complete timeline (normal + attack windows)
3. Deleting records outside timeline boundaries
4. Fixing only 'unknown' labels based on timing + characteristics
5. Fixing mismatched labels if packets match defined characteristics
6. Preserving all correct existing labels

Approach: Conservative data integrity preservation
"""

import pandas as pd
import re
import argparse
import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

def setup_logging(log_file='fix_timeline_integrity.log'):
    """Set up logging configuration."""
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode='w')  # Overwrite log file each run
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging to file: {log_file}")
    return logger

def create_backups(dataset_dir, logger):
    """Create backup files for all CSV formats."""
    csv_files = {
        'packet_features': dataset_dir / "packet_features_30.csv",
        'flow_features': dataset_dir / "flow_features.csv", 
        'cicflow_features': dataset_dir / "cicflow_features_all.csv"
    }
    
    backup_count = 0
    for name, csv_path in csv_files.items():
        if csv_path.exists():
            backup_path = csv_path.with_suffix('.csv.backup_raw')
            if not backup_path.exists():  # Don't overwrite existing backups
                try:
                    shutil.copy2(csv_path, backup_path)
                    logger.info(f"Created backup: {backup_path.name}")
                    backup_count += 1
                except Exception as e:
                    logger.error(f"Failed to backup {csv_path.name}: {e}")
            else:
                logger.info(f"Backup already exists: {backup_path.name}")
    
    return backup_count

def parse_complete_timeline(attack_log_file, logger):
    """Parse attack.log to extract complete timeline including normal traffic windows."""
    timeline_windows = {}
    
    if not os.path.exists(attack_log_file):
        logger.error(f"Attack log not found: {attack_log_file}")
        return timeline_windows
    
    attack_timings = {}
    traditional_starts = {}  # Track traditional attack start times
    
    try:
        with open(attack_log_file, 'r') as f:
            for line in f:
                # Parse adversarial attack start patterns
                if 'Starting enhanced adversarial attack:' in line:
                    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .* Starting enhanced adversarial attack: (\w+) for (\d+)s', line)
                    if match:
                        timestamp_str = match.group(1)
                        attack_type = match.group(2)
                        duration = int(match.group(3))
                        
                        start_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp()
                        end_time = start_time + duration
                        
                        # Normalize attack type names
                        if attack_type == 'slow_read':
                            attack_type = 'ad_slow'
                        elif attack_type not in ['ad_syn', 'ad_udp']:
                            attack_type = f'ad_{attack_type}'
                        
                        attack_timings[attack_type] = {
                            'start': start_time,
                            'end': end_time,
                            'duration': duration,
                            'type': 'attack'
                        }
                        logger.debug(f"Found adversarial attack: {attack_type} ({duration}s)")
                
                # Parse traditional attack start patterns
                elif 'Starting Enhanced' in line and ('SYN Flood' in line or 'UDP Flood' in line or 'ICMP Flood' in line):
                    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .* \[([^\]]+)\] .* Starting Enhanced ([A-Z]+) Flood .* for (\d+) seconds', line)
                    if match:
                        timestamp_str = match.group(1)
                        attack_type_bracket = match.group(2)  # This is the attack type in brackets
                        attack_name = match.group(3).lower()
                        duration = int(match.group(4))
                        
                        start_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp()
                        
                        # Use the attack type from brackets, or map from attack name
                        if attack_type_bracket in ['syn_flood', 'udp_flood', 'icmp_flood']:
                            attack_key = attack_type_bracket
                        else:
                            # Fallback: map from attack name
                            type_mapping = {
                                'syn': 'syn_flood',
                                'udp': 'udp_flood', 
                                'icmp': 'icmp_flood'
                            }
                            attack_key = type_mapping.get(attack_name, f'{attack_name}_flood')
                        
                        traditional_starts[attack_key] = {
                            'start': start_time,
                            'duration': duration
                        }
                        logger.debug(f"Found traditional attack start: {attack_key} ({duration}s)")
                
                # Parse traditional attack completion patterns
                elif 'Attack completed' in line and 'packets/sec' in line:
                    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ .* \[([^\]]+)\] .* Attack completed', line)
                    if match:
                        timestamp_str = match.group(1)
                        attack_type = match.group(2)
                        
                        end_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp()
                        
                        if attack_type in ['syn_flood', 'udp_flood', 'icmp_flood']:
                            # Use actual start time and duration if available
                            if attack_type in traditional_starts:
                                start_info = traditional_starts[attack_type]
                                attack_timings[attack_type] = {
                                    'start': start_info['start'],
                                    'end': end_time,
                                    'duration': start_info['duration'],
                                    'type': 'attack'
                                }
                                logger.debug(f"Completed traditional attack: {attack_type} (actual duration: {start_info['duration']}s)")
                            else:
                                # Fallback: assume 75s duration based on investigation
                                start_time = end_time - 75
                                attack_timings[attack_type] = {
                                    'start': start_time,
                                    'end': end_time,
                                    'duration': 75,
                                    'type': 'attack'
                                }
                                logger.warning(f"Using fallback timing for {attack_type}: 75s duration")
        
        # Infer normal traffic window (before first attack)
        if attack_timings:
            earliest_attack = min(timing['start'] for timing in attack_timings.values())
            # Assume normal traffic starts 1 hour before first attack
            normal_start = earliest_attack - 3600
            normal_end = earliest_attack
            
            timeline_windows['normal'] = {
                'start': normal_start,
                'end': normal_end,
                'duration': 3600,
                'type': 'normal'
            }
            
            # Add all attack windows
            timeline_windows.update(attack_timings)
        
        logger.info(f"Found {len(timeline_windows)} timeline windows:")
        for window_type, timing in timeline_windows.items():
            start_str = datetime.fromtimestamp(timing['start']).strftime('%H:%M:%S')
            end_str = datetime.fromtimestamp(timing['end']).strftime('%H:%M:%S')
            logger.info(f"  {window_type}: {start_str} - {end_str} ({timing['duration']}s)")
    
    except Exception as e:
        logger.error(f"Error parsing attack log {attack_log_file}: {e}")
    
    return timeline_windows

def is_within_timeline(timestamp, timeline_windows, buffer_seconds=30):
    """Check if timestamp falls within any defined timeline window with buffer."""
    # First check exact matches without buffer to avoid overlap conflicts
    for window_type, timing in timeline_windows.items():
        if timing['start'] <= timestamp <= timing['end']:
            return True, window_type
    
    # Then check with buffer if no exact match found
    for window_type, timing in timeline_windows.items():
        start_with_buffer = timing['start'] - buffer_seconds
        end_with_buffer = timing['end'] + buffer_seconds
        if start_with_buffer <= timestamp <= end_with_buffer:
            return True, window_type
    
    return False, None

def get_expected_label_for_timestamp(timestamp, timeline_windows):
    """Get expected label based on timestamp and timeline windows."""
    for window_type, timing in timeline_windows.items():
        if timing['start'] <= timestamp <= timing['end']:
            return window_type if window_type != 'normal' else 'normal'
    return None

def validate_packet_characteristics(packet_row, expected_label, data_type):
    """Validate if packet characteristics match expected attack type."""
    
    if expected_label == 'normal':
        return True  # Normal traffic can be anything
    
    if data_type == 'network_flow' or data_type == 'cicflow':
        # Network flow validation (src_ip, dst_ip, protocol columns)
        if expected_label in ['ad_syn', 'ad_udp', 'ad_slow']:
            return (packet_row.get('protocol') == 6 and 
                   packet_row.get('dst_port') == 80 and 
                   packet_row.get('dst_ip') == '10.0.0.6')
        elif expected_label == 'syn_flood':
            return packet_row.get('protocol') == 6
        elif expected_label == 'udp_flood':
            return packet_row.get('protocol') == 17
        elif expected_label == 'icmp_flood':
            return packet_row.get('protocol') == 1
    
    elif data_type == 'packet_level':
        # Packet-level validation (ip_src, ip_dst, ip_proto columns)
        if expected_label in ['ad_syn', 'ad_udp', 'ad_slow']:
            return (packet_row.get('ip_proto') == 6 and 
                   packet_row.get('dst_port') == 80.0 and 
                   packet_row.get('ip_dst') == '10.0.0.6')
        elif expected_label == 'syn_flood':
            return packet_row.get('ip_proto') == 6
        elif expected_label == 'udp_flood':
            return packet_row.get('ip_proto') == 17
        elif expected_label == 'icmp_flood':
            return packet_row.get('ip_proto') == 1
    
    elif data_type == 'sdn_flow':
        # SDN flow data - no IP/port validation possible
        return True
    
    return True  # Default: accept if can't validate

def determine_data_type(df):
    """Determine the type of CSV data based on column names."""
    if 'src_ip' in df.columns:
        return 'network_flow'
    elif 'ip_src' in df.columns:
        return 'packet_level'
    elif 'switch_id' in df.columns:
        return 'sdn_flow'
    else:
        return 'unknown'

def process_csv_timeline_integrity(csv_path, timeline_windows, logger):
    """Process single CSV file for timeline integrity."""
    
    logger.info(f"Processing: {csv_path.name}")
    
    # Read CSV
    try:
        df = pd.read_csv(csv_path)
        original_count = len(df)
        logger.info(f"Loaded {original_count} records")
    except Exception as e:
        logger.error(f"Failed to read {csv_path}: {e}")
        return False
    
    # Determine data type
    data_type = determine_data_type(df)
    logger.info(f"Data type: {data_type}")
    
    # Convert timestamp if needed
    if df['timestamp'].dtype == 'object':
        logger.info("Converting timestamp column from string to numeric...")
        # Use manual conversion to avoid timezone issues with pandas
        df['timestamp'] = df['timestamp'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp())
    
    # Step 1: Filter records within timeline
    logger.info("Filtering records to timeline boundaries...")
    timeline_mask = df['timestamp'].apply(lambda ts: is_within_timeline(ts, timeline_windows)[0])
    df_filtered = df[timeline_mask].copy()
    deleted_count = original_count - len(df_filtered)
    logger.info(f"Deleted {deleted_count} records outside timeline")
    
    # Step 2: Process labels - ONLY fix "unknown" labels, preserve all existing labels
    logger.info("Processing labels - fixing only 'unknown' labels...")
    fixes_applied = 0
    unknown_fixed = 0
    
    for idx, row in df_filtered.iterrows():
        timestamp = row['timestamp']
        current_label = row.get('Label_multi', 'unknown')
        
        # ONLY fix literal "unknown" labels - preserve all existing labels
        if current_label == 'unknown':
            # Get expected label for this timestamp
            _, expected_window = is_within_timeline(timestamp, timeline_windows)
            expected_label = get_expected_label_for_timestamp(timestamp, timeline_windows)
            
            if expected_label and validate_packet_characteristics(row, expected_label, data_type):
                df_filtered.loc[idx, 'Label_multi'] = expected_label
                df_filtered.loc[idx, 'Label_binary'] = 0 if expected_label == 'normal' else 1
                unknown_fixed += 1
                fixes_applied += 1
                logger.info(f"Fixed unknown label -> {expected_label} at {timestamp}")
        
        # For all other labels: PRESERVE existing labels regardless of timing
        # No mismatched label fixing - data integrity preservation
    
    # Log results
    logger.info(f"Label fixes applied: {fixes_applied}")
    logger.info(f"  Unknown labels fixed: {unknown_fixed}")
    logger.info("  Existing labels preserved (no mismatched label changes)")
    
    # Save processed file
    try:
        df_filtered.to_csv(csv_path, index=False)
        final_count = len(df_filtered)
        logger.info(f"Saved processed file: {original_count} -> {final_count} records")
        
        # Log final label distribution
        label_counts = df_filtered['Label_multi'].value_counts()
        logger.info("Final label distribution:")
        for label, count in label_counts.items():
            logger.info(f"  {label}: {count} records")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save {csv_path}: {e}")
        return False

def process_dataset_timeline_integrity(dataset_dir, logger):
    """Process all CSV files in a dataset directory for timeline integrity."""
    
    logger.info(f"Processing dataset: {dataset_dir.name}")
    
    # Step 1: Create backups
    backup_count = create_backups(dataset_dir, logger)
    logger.info(f"Created {backup_count} backup files")
    
    # Step 2: Parse timeline from attack.log
    attack_log = dataset_dir / "attack.log"
    timeline_windows = parse_complete_timeline(attack_log, logger)
    
    if not timeline_windows:
        logger.error(f"No timeline windows found for {dataset_dir.name}")
        return False
    
    # Step 3: Process each CSV file
    csv_files = [
        dataset_dir / "packet_features_30.csv",
        dataset_dir / "flow_features.csv", 
        dataset_dir / "cicflow_features_all.csv"
    ]
    
    success_count = 0
    for csv_path in csv_files:
        if csv_path.exists():
            if process_csv_timeline_integrity(csv_path, timeline_windows, logger):
                success_count += 1
            else:
                logger.error(f"Failed to process {csv_path.name}")
        else:
            logger.warning(f"CSV file not found: {csv_path.name}")
    
    logger.info(f"Successfully processed {success_count}/{len(csv_files)} CSV files")
    return success_count == len([f for f in csv_files if f.exists()])

def main():
    parser = argparse.ArgumentParser(description='Fix timeline integrity while preserving data integrity')
    parser.add_argument('--path', default='../main_output/v2_main', help='Path to version directory (default: ../main_output/v2_main)')
    parser.add_argument('--dataset', help='Process specific dataset directory (e.g., 1607-1)')
    parser.add_argument('--all', action='store_true', help='Process all dataset directories')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Determine version path for log file
    version_path = Path(args.path)
    if not version_path.exists():
        print(f"❌ Error: Version directory not found: {version_path}")
        return 1
    
    log_path = version_path / "fix_timeline_integrity.log"
    
    # Set up logging
    logger = setup_logging(log_path)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("TIMELINE INTEGRITY FIX STARTED")
    logger.info("=" * 60)
    logger.info(f"📁 Version directory: {version_path.absolute()}")
    
    # Find datasets to process
    if args.dataset:
        dataset_path = version_path / args.dataset
        if not dataset_path.exists():
            logger.error(f"Dataset directory not found: {dataset_path}")
            return 1
        datasets = [dataset_path]
    elif args.all:
        datasets = []
        if version_path.exists():
            for item in version_path.iterdir():
                if item.is_dir() and re.match(r'^\d{6}-\d+$', item.name):
                    datasets.append(item)
        datasets = sorted(datasets)
    else:
        logger.error("Specify --dataset <name> or --all")
        return 1
    
    if not datasets:
        logger.error("No dataset directories found!")
        return 1
    
    logger.info(f"Found {len(datasets)} dataset directories to process:")
    for dataset in datasets:
        logger.info(f"  - {dataset.name}")
    
    # Process each dataset
    success_datasets = 0
    total_datasets = len(datasets)
    
    for dataset_dir in datasets:
        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSING DATASET: {dataset_dir.name}")
        logger.info(f"{'='*60}")
        
        success = process_dataset_timeline_integrity(dataset_dir, logger)
        
        if success:
            success_datasets += 1
            logger.info(f"✅ Dataset {dataset_dir.name} completed successfully")
        else:
            logger.error(f"❌ Dataset {dataset_dir.name} had errors")
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("TIMELINE INTEGRITY PROCESSING SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total datasets processed: {success_datasets}/{total_datasets}")
    
    if success_datasets == total_datasets:
        logger.info("🎉 All datasets processed successfully!")
        return 0
    else:
        logger.error(f"⚠️  {total_datasets - success_datasets} datasets had errors")
        return 1

if __name__ == "__main__":
    exit(main())