#!/usr/bin/env python3
"""
Timeline Analysis Script for V3 Combined SDN DDoS Datasets

This script analyzes the timeline alignment between the three combined datasets:
- packet_dataset.csv
- flow_dataset.csv  
- cicflow_dataset.csv

Ensures proper synchronization of attack phases across all three combined dataset types.

Usage:
    python3 analyze_timeline_v3.py [--version VERSION]
    
Arguments:
    --version VERSION    Version directory to analyze (default: v3)
"""

import csv
import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def parse_timestamp(timestamp_str):
    """Parse timestamp from either Unix epoch (float) or datetime string format."""
    try:
        # Try Unix timestamp first (float)
        return float(timestamp_str)
    except ValueError:
        # Try datetime string parsing
        try:
            # Handle various datetime formats
            if ' ' in timestamp_str:
                # Format: '2025-09-12 16:19:49'
                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            else:
                # Fallback for other formats
                dt = datetime.fromisoformat(timestamp_str)
            return dt.timestamp()
        except (ValueError, AttributeError):
            # Try additional common formats
            try:
                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                return dt.timestamp()
            except ValueError:
                raise ValueError(f"Unable to parse timestamp: {timestamp_str}")

def setup_logging(log_path=None):
    """Set up logging configuration."""
    log_file = log_path if log_path else 'analyze_timeline_v3.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode='w')
        ]
    )
    return logging.getLogger(__name__)

def read_csv_timeline(csv_file, timestamp_col, label_col, logger):
    """Read CSV file and extract timeline information for each attack type."""
    if not os.path.exists(csv_file):
        logger.error(f"File not found: {csv_file}")
        return {}
    
    timeline_data = defaultdict(list)
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Get header to determine column indices
            
            # Auto-detect timestamp column if "auto" specified
            if timestamp_col == "auto":
                if 'timestamp' in header:
                    timestamp_col = header.index('timestamp')
                else:
                    logger.error(f"No 'timestamp' column found in {csv_file.name}")
                    return {}
            
            # Auto-detect label column if -1 specified
            if label_col == -1:
                if 'Label_multi' in header:
                    label_col = header.index('Label_multi')
                else:
                    # Fallback to second-to-last column
                    label_col = len(header) - 2
            
            logger.info(f"Reading {csv_file.name} - timestamp col: {timestamp_col} ({header[timestamp_col]}), label col: {label_col} ({header[label_col] if label_col < len(header) else 'UNKNOWN'})")
            logger.info(f"Total columns: {len(header)}")
            
            for row_num, row in enumerate(reader):
                if len(row) > max(timestamp_col, label_col):
                    try:
                        timestamp = parse_timestamp(row[timestamp_col])
                        label = row[label_col]
                        if label.strip():  # Skip empty labels
                            timeline_data[label].append(timestamp)
                    except (ValueError, IndexError) as e:
                        if row_num < 10:  # Only log first few errors
                            logger.warning(f"Row {row_num}: {e}")
                        
    except Exception as e:
        logger.error(f"Error reading {csv_file}: {e}")
        return {}
    
    # Calculate start/end times for each attack type
    attack_timeline = {}
    for label, timestamps in timeline_data.items():
        if timestamps:
            attack_timeline[label] = {
                'start': min(timestamps),
                'end': max(timestamps),
                'duration': max(timestamps) - min(timestamps),
                'count': len(timestamps)
            }
    
    logger.info(f"Found {len(attack_timeline)} attack types with {sum(len(ts) for ts in timeline_data.values())} total records")
    return attack_timeline

def format_timestamp(timestamp):
    """Convert timestamp to readable format."""
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]

def format_duration(duration):
    """Format duration in seconds with 1 decimal place."""
    return f"{duration:.1f}s"

def analyze_three_way_coverage(packet_timeline, flow_timeline, cicflow_timeline):
    """Analyze coverage and alignment between all three timeline types."""
    all_attacks = set(packet_timeline.keys()) | set(flow_timeline.keys()) | set(cicflow_timeline.keys())
    analysis = {}
    
    for attack in sorted(all_attacks):
        packet_data = packet_timeline.get(attack)
        flow_data = flow_timeline.get(attack)
        cicflow_data = cicflow_timeline.get(attack)
        
        # Count presence
        present_count = sum([bool(packet_data), bool(flow_data), bool(cicflow_data)])
        
        # Calculate overlaps if all three are present
        if packet_data and flow_data and cicflow_data:
            # Three-way overlap calculation
            overlap_start = max(packet_data['start'], flow_data['start'], cicflow_data['start'])
            overlap_end = min(packet_data['end'], flow_data['end'], cicflow_data['end'])
            overlap_duration = max(0, overlap_end - overlap_start)
            
            # Calculate pairwise gaps
            packet_flow_gap = abs(packet_data['start'] - flow_data['start'])
            packet_cicflow_gap = abs(packet_data['start'] - cicflow_data['start'])
            flow_cicflow_gap = abs(flow_data['start'] - cicflow_data['start'])
            max_gap = max(packet_flow_gap, packet_cicflow_gap, flow_cicflow_gap)
            
            # Determine status
            if overlap_duration < 1:
                status = "❌ POOR 3-WAY OVERLAP"
            elif max_gap > 30:
                status = "⚠️  LARGE TIMING GAPS"
            elif overlap_duration > min(packet_data['duration'], flow_data['duration'], cicflow_data['duration']) * 0.8:
                status = "✅ EXCELLENT 3-WAY MATCH"
            else:
                status = "✅ GOOD 3-WAY OVERLAP"
                
        elif present_count == 2:
            # Partial coverage
            overlap_duration = 0
            max_gap = 0
            if packet_data and flow_data:
                overlap_start = max(packet_data['start'], flow_data['start'])
                overlap_end = min(packet_data['end'], flow_data['end'])
                overlap_duration = max(0, overlap_end - overlap_start)
                max_gap = abs(packet_data['start'] - flow_data['start'])
            status = f"⚠️  PARTIAL COVERAGE ({present_count}/3)"
            
        elif present_count == 1:
            overlap_duration = 0
            max_gap = 0
            status = f"❌ SINGLE SOURCE ONLY ({present_count}/3)"
        else:
            overlap_duration = 0
            max_gap = 0
            status = "❌ NO DATA FOUND"
        
        analysis[attack] = {
            'packet_data': packet_data,
            'flow_data': flow_data,
            'cicflow_data': cicflow_data,
            'present_count': present_count,
            'overlap_duration': overlap_duration,
            'max_gap': max_gap,
            'status': status
        }
    
    return analysis

def print_three_way_timeline_table(packet_timeline, flow_timeline, cicflow_timeline, analysis, logger):
    """Print a formatted three-way timeline comparison table."""
    logger.info("\n" + "="*120)
    logger.info("📊 THREE-WAY TIMELINE ANALYSIS RESULTS")
    logger.info("="*120)
    
    # Header
    header = f"{'Attack Type':<12} {'Packet Timeline':<25} {'Flow Timeline':<25} {'CICFlow Timeline':<25} {'3-Way Status':<25}"
    logger.info(header)
    logger.info("-" * 120)
    
    for attack in sorted(analysis.keys()):
        data = analysis[attack]
        packet_data = data['packet_data']
        flow_data = data['flow_data']
        cicflow_data = data['cicflow_data']
        
        # Format packet timeline
        if packet_data:
            packet_info = f"{format_duration(packet_data['duration'])} ({packet_data['count']} entries)"
        else:
            packet_info = "MISSING"
        
        # Format flow timeline  
        if flow_data:
            flow_info = f"{format_duration(flow_data['duration'])} ({flow_data['count']} entries)"
        else:
            flow_info = "MISSING"
            
        # Format cicflow timeline
        if cicflow_data:
            cicflow_info = f"{format_duration(cicflow_data['duration'])} ({cicflow_data['count']} entries)"
        else:
            cicflow_info = "MISSING"
        
        row = f"{attack:<12} {packet_info:<25} {flow_info:<25} {cicflow_info:<25} {data['status']:<25}"
        logger.info(row)

def print_detailed_three_way_timing(packet_timeline, flow_timeline, cicflow_timeline, analysis, logger):
    """Print detailed timing information for all three datasets."""
    logger.info("\n" + "="*100)
    logger.info("🕐 DETAILED THREE-WAY TIMING INFORMATION")
    logger.info("="*100)
    
    for attack in sorted(analysis.keys()):
        data = analysis[attack]
        packet_data = data['packet_data']
        flow_data = data['flow_data']
        cicflow_data = data['cicflow_data']
        
        logger.info(f"\n📍 {attack.upper()}:")
        
        if packet_data:
            logger.info(f"   Packet:  {format_timestamp(packet_data['start'])} - {format_timestamp(packet_data['end'])} ({format_duration(packet_data['duration'])})")
        else:
            logger.info(f"   Packet:  MISSING")
            
        if flow_data:
            logger.info(f"   Flow:    {format_timestamp(flow_data['start'])} - {format_timestamp(flow_data['end'])} ({format_duration(flow_data['duration'])})")
        else:
            logger.info(f"   Flow:    MISSING")
            
        if cicflow_data:
            logger.info(f"   CICFlow: {format_timestamp(cicflow_data['start'])} - {format_timestamp(cicflow_data['end'])} ({format_duration(cicflow_data['duration'])})")
        else:
            logger.info(f"   CICFlow: MISSING")
        
        # Calculate and display timing gaps
        if data['present_count'] >= 2:
            gaps = []
            if packet_data and flow_data:
                gap = abs(packet_data['start'] - flow_data['start'])
                gaps.append(f"Packet-Flow: ±{gap:.1f}s")
            if packet_data and cicflow_data:
                gap = abs(packet_data['start'] - cicflow_data['start'])
                gaps.append(f"Packet-CICFlow: ±{gap:.1f}s")
            if flow_data and cicflow_data:
                gap = abs(flow_data['start'] - cicflow_data['start'])
                gaps.append(f"Flow-CICFlow: ±{gap:.1f}s")
            
            if gaps:
                logger.info(f"   Gaps:    {', '.join(gaps)}")

def print_three_way_summary_statistics(packet_timeline, flow_timeline, cicflow_timeline, analysis, logger):
    """Print summary statistics for three-way analysis."""
    total_attacks = len(analysis)
    excellent_matches = len([a for a in analysis.values() if "EXCELLENT 3-WAY MATCH" in a['status']])
    good_matches = len([a for a in analysis.values() if "GOOD 3-WAY OVERLAP" in a['status']])
    partial_coverage = len([a for a in analysis.values() if "PARTIAL COVERAGE" in a['status']])
    single_source = len([a for a in analysis.values() if "SINGLE SOURCE ONLY" in a['status']])
    poor_overlap = len([a for a in analysis.values() if "POOR 3-WAY OVERLAP" in a['status'] or "LARGE TIMING GAPS" in a['status']])
    
    logger.info("\n" + "="*80)
    logger.info("📈 THREE-WAY SUMMARY STATISTICS")
    logger.info("="*80)
    logger.info(f"Total attack types: {total_attacks}")
    logger.info(f"✅ Excellent 3-way match: {excellent_matches}")
    logger.info(f"✅ Good 3-way alignment: {good_matches}")
    logger.info(f"⚠️  Partial coverage (2/3): {partial_coverage}")
    logger.info(f"❌ Single source only (1/3): {single_source}")
    logger.info(f"❌ Poor alignment/gaps: {poor_overlap}")
    
    # Calculate coverage percentages
    full_coverage = excellent_matches + good_matches
    coverage_score = (full_coverage / total_attacks * 100) if total_attacks > 0 else 0
    
    logger.info(f"\n🎯 Full Coverage Score: {coverage_score:.1f}% ({full_coverage}/{total_attacks})")
    
    # Dataset-specific coverage
    packet_coverage = len([a for a in analysis.values() if a['packet_data'] is not None])
    flow_coverage = len([a for a in analysis.values() if a['flow_data'] is not None])
    cicflow_coverage = len([a for a in analysis.values() if a['cicflow_data'] is not None])
    
    logger.info(f"\n📊 Individual Dataset Coverage:")
    logger.info(f"   Packet dataset:  {packet_coverage}/{total_attacks} ({packet_coverage/total_attacks*100:.1f}%)")
    logger.info(f"   Flow dataset:    {flow_coverage}/{total_attacks} ({flow_coverage/total_attacks*100:.1f}%)")
    logger.info(f"   CICFlow dataset: {cicflow_coverage}/{total_attacks} ({cicflow_coverage/total_attacks*100:.1f}%)")
    
    if coverage_score >= 90:
        logger.info("🎉 EXCELLENT: Three-way timeline alignment is outstanding!")
    elif coverage_score >= 70:
        logger.info("👍 GOOD: Three-way timeline alignment is solid with minor gaps.")
    elif coverage_score >= 50:
        logger.info("⚠️  FAIR: Three-way timeline alignment needs improvement.")
    else:
        logger.info("❌ POOR: Three-way timeline alignment has major issues requiring attention.")

def suggest_three_way_improvements(analysis, packet_timeline, flow_timeline, cicflow_timeline, logger):
    """Suggest improvements based on three-way analysis results."""
    logger.info("\n" + "="*80)
    logger.info("💡 THREE-WAY IMPROVEMENT SUGGESTIONS")
    logger.info("="*80)
    
    missing_in_packet = [attack for attack, data in analysis.items() if data['packet_data'] is None]
    missing_in_flow = [attack for attack, data in analysis.items() if data['flow_data'] is None]
    missing_in_cicflow = [attack for attack, data in analysis.items() if data['cicflow_data'] is None]
    large_gaps = [attack for attack, data in analysis.items() if data['max_gap'] > 30]
    
    if missing_in_packet:
        logger.info(f"🔧 Packet data missing for: {', '.join(missing_in_packet)}")
        logger.info("   Solution: Check packet capture timing and PCAP processing")
    
    if missing_in_flow:
        logger.info(f"🔧 Flow data missing for: {', '.join(missing_in_flow)}")
        logger.info("   Solution: Verify flow collection duration and timing")
        
    if missing_in_cicflow:
        logger.info(f"🔧 CICFlow data missing for: {', '.join(missing_in_cicflow)}")
        logger.info("   Solution: Check CICFlow processing and feature extraction")
    
    if large_gaps:
        logger.info(f"🔧 Large timing gaps (>30s) for: {', '.join(large_gaps)}")
        logger.info("   Solution: Synchronize data collection start times across all three sources")
    
    # Analyze timing patterns
    if packet_timeline and flow_timeline and cicflow_timeline:
        packet_span = max([data['end'] for data in packet_timeline.values()]) - min([data['start'] for data in packet_timeline.values()])
        flow_span = max([data['end'] for data in flow_timeline.values()]) - min([data['start'] for data in flow_timeline.values()])
        cicflow_span = max([data['end'] for data in cicflow_timeline.values()]) - min([data['start'] for data in cicflow_timeline.values()])
        
        logger.info(f"\n📊 Data Collection Span Analysis:")
        logger.info(f"   Packet data spans:  {packet_span:.1f}s")
        logger.info(f"   Flow data spans:    {flow_span:.1f}s")  
        logger.info(f"   CICFlow data spans: {cicflow_span:.1f}s")
        
        max_span = max(packet_span, flow_span, cicflow_span)
        if packet_span < max_span - 10:
            logger.info(f"   ⚠️  Packet collection {max_span - packet_span:.1f}s shorter than needed")
        if flow_span < max_span - 10:
            logger.info(f"   ⚠️  Flow collection {max_span - flow_span:.1f}s shorter than needed")
        if cicflow_span < max_span - 10:
            logger.info(f"   ⚠️  CICFlow collection {max_span - cicflow_span:.1f}s shorter than needed")

def analyze_combined_datasets(dataset_path, logger):
    """Analyze timeline for the three combined dataset files."""
    logger.info(f"\n{'='*80}")
    logger.info(f"ANALYZING COMBINED DATASETS IN: {dataset_path.name}")
    logger.info(f"{'='*80}")
    
    # Define file paths for combined datasets
    packet_csv = dataset_path / "packet_dataset.csv"
    flow_csv = dataset_path / "flow_dataset.csv"
    cicflow_csv = dataset_path / "cicflow_dataset.csv"
    
    logger.info(f"📁 Dataset directory: {dataset_path.absolute()}")
    logger.info(f"📄 Packet dataset: {packet_csv}")
    logger.info(f"📄 Flow dataset: {flow_csv}")
    logger.info(f"📄 CICFlow dataset: {cicflow_csv}")
    
    # Check if files exist
    files_found = []
    if packet_csv.exists():
        files_found.append("packet_dataset.csv")
    if flow_csv.exists():
        files_found.append("flow_dataset.csv")
    if cicflow_csv.exists():
        files_found.append("cicflow_dataset.csv")
    
    logger.info(f"Found combined datasets: {', '.join(files_found)}")
    
    if len(files_found) == 0:
        logger.error("❌ No combined dataset files found. Run combine_datasets.py first.")
        return False
    
    # Read timeline data - combined datasets have dataset_id as first column
    logger.info("\n📖 Reading combined timeline data...")
    
    # Combined datasets have different structures - auto-detect timestamp column
    packet_timeline = read_csv_timeline(packet_csv, timestamp_col="auto", label_col=-1, logger=logger) if packet_csv.exists() else {}
    flow_timeline = read_csv_timeline(flow_csv, timestamp_col="auto", label_col=-1, logger=logger) if flow_csv.exists() else {}
    cicflow_timeline = read_csv_timeline(cicflow_csv, timestamp_col="auto", label_col=-1, logger=logger) if cicflow_csv.exists() else {}
    
    if not packet_timeline and not flow_timeline and not cicflow_timeline:
        logger.error("❌ No timeline data found in any combined dataset file.")
        return False
    
    # Perform three-way analysis
    analysis = analyze_three_way_coverage(packet_timeline, flow_timeline, cicflow_timeline)
    
    # Print results
    print_three_way_timeline_table(packet_timeline, flow_timeline, cicflow_timeline, analysis, logger)
    print_detailed_three_way_timing(packet_timeline, flow_timeline, cicflow_timeline, analysis, logger)
    print_three_way_summary_statistics(packet_timeline, flow_timeline, cicflow_timeline, analysis, logger)
    suggest_three_way_improvements(analysis, packet_timeline, flow_timeline, cicflow_timeline, logger)
    
    return True

def main():
    """Main function to run three-way combined datasets timeline analysis."""
    parser = argparse.ArgumentParser(description='Analyze timeline alignment for V3 combined datasets')
    parser.add_argument('--path', default='../main_output/v3', help='Path to dataset directory (default: ../main_output/v3)')
    
    args = parser.parse_args()
    
    # Determine dataset path
    dataset_path = Path(args.path)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset directory not found: {dataset_path}")
        return 1
    
    # Set up logging to dataset directory
    log_path = dataset_path / "analyze_timeline_v3.log"
    logger = setup_logging(log_path)
    
    logger.info("🔍 V3 Combined SDN DDoS Datasets Three-Way Timeline Analysis")
    logger.info(f"📁 Dataset directory: {dataset_path.absolute()}")
    
    # Analyze the combined datasets
    try:
        if analyze_combined_datasets(dataset_path, logger):
            logger.info(f"\n{'='*80}")
            logger.info("ANALYSIS COMPLETE")
            logger.info(f"{'='*80}")
            logger.info("🎉 Combined datasets timeline analysis completed successfully!")
            return 0
        else:
            logger.error("❌ Failed to analyze combined datasets")
            return 1
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return 1

if __name__ == "__main__":
    exit(main())