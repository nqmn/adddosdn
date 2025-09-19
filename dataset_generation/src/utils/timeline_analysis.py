#!/usr/bin/env python3
"""
Timeline Analysis Module for SDN DDoS Dataset Generation

This module provides functions to analyze the timeline alignment between packet_features.csv 
and flow_features.csv to ensure proper synchronization of attack phases and identify any 
missing coverage.
"""

import csv
import os
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def read_csv_timeline(csv_file, timestamp_col, label_col):
    """Read CSV file and extract timeline information for each attack type.

    Notes:
    - Excludes 'cooldown' label to avoid merging it with pre-attack 'normal'.
    """
    if not os.path.exists(csv_file):
        return {}
    
    timeline_data = defaultdict(list)
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            
            for row in reader:
                if len(row) > max(timestamp_col, label_col):
                    timestamp = float(row[timestamp_col])
                    label = row[label_col]
                    # Exclude cooldown and unknown from analysis to prevent skewing
                    if label and label.strip() and label not in ('cooldown', 'unknown'):
                        timeline_data[label].append(timestamp)
                    
    except Exception as e:
        logging.error(f"Error reading {csv_file}: {e}")
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
    
    return attack_timeline

def format_timestamp(timestamp):
    """Convert timestamp to readable format."""
    return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]

def format_duration(duration):
    """Format duration in seconds with 1 decimal place."""
    return f"{duration:.1f}s"

def analyze_coverage(packet_timeline, flow_timeline):
    """Analyze coverage and alignment between packet and flow timelines."""
    all_attacks = set(packet_timeline.keys()) | set(flow_timeline.keys())
    analysis = {}
    
    for attack in sorted(all_attacks):
        packet_data = packet_timeline.get(attack)
        flow_data = flow_timeline.get(attack)
        
        if packet_data and flow_data:
            # Calculate overlap
            overlap_start = max(packet_data['start'], flow_data['start'])
            overlap_end = min(packet_data['end'], flow_data['end'])
            overlap_duration = max(0, overlap_end - overlap_start)
            
            # Calculate time gaps
            start_gap = abs(packet_data['start'] - flow_data['start'])
            end_gap = abs(packet_data['end'] - flow_data['end'])
            
            status = "✅ GOOD OVERLAP"
            if overlap_duration < 1:
                status = "⚠️  POOR OVERLAP"
            elif start_gap > 10 or end_gap > 10:
                status = "⚠️  TIMING OFFSET"
            elif overlap_duration > min(packet_data['duration'], flow_data['duration']) * 0.8:
                status = "✅ EXCELLENT MATCH"
            
        elif packet_data and not flow_data:
            overlap_duration = 0
            start_gap = 0
            end_gap = 0
            status = "❌ MISSING IN FLOW"
            
        elif not packet_data and flow_data:
            overlap_duration = 0
            start_gap = 0
            end_gap = 0
            status = "❌ MISSING IN PACKET"
            
        analysis[attack] = {
            'packet_data': packet_data,
            'flow_data': flow_data,
            'overlap_duration': overlap_duration,
            'start_gap': start_gap,
            'end_gap': end_gap,
            'status': status
        }
    
    return analysis

def calculate_alignment_score(analysis):
    """Calculate overall alignment score."""
    total_attacks = len(analysis)
    good_matches = len([a for a in analysis.values() if "✅" in a['status']])
    score = (good_matches / total_attacks * 100) if total_attacks > 0 else 0
    return score, good_matches, total_attacks

def get_alignment_status(score):
    """Get alignment status based on score."""
    if score >= 90:
        return "🎉 EXCELLENT: Timeline alignment is very good!"
    elif score >= 70:
        return "👍 GOOD: Timeline alignment is acceptable with minor issues."
    elif score >= 50:
        return "⚠️  FAIR: Timeline alignment needs improvement."
    else:
        return "❌ POOR: Timeline alignment has major issues that need fixing."

def analyze_dataset_timeline(packet_csv, flow_csv, logger=None):
    """
    Main function to analyze timeline alignment between packet and flow datasets.
    
    Args:
        packet_csv: Path to packet_features.csv
        flow_csv: Path to flow_features.csv
        logger: Logger instance for output
    
    Returns:
        dict: Analysis results with score, status, and detailed breakdown
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.info("Starting timeline analysis...")
    
    # Read timeline data
    packet_timeline = read_csv_timeline(packet_csv, timestamp_col=0, label_col=30)  # timestamp, Label_multi
    flow_timeline = read_csv_timeline(flow_csv, timestamp_col=0, label_col=16)      # timestamp, Label_multi
    
    if not packet_timeline and not flow_timeline:
        logger.error("No timeline data found in either file.")
        return {
            'score': 0,
            'status': 'NO_DATA',
            'analysis': {},
            'packet_timeline': {},
            'flow_timeline': {}
        }
    
    # Perform analysis
    analysis = analyze_coverage(packet_timeline, flow_timeline)
    score, good_matches, total_attacks = calculate_alignment_score(analysis)
    status = get_alignment_status(score)
    
    # Log summary
    logger.info(f"Timeline Analysis Results:")
    logger.info(f"  Total attack types: {total_attacks}")
    logger.info(f"  Good alignment: {good_matches}")
    logger.info(f"  Overall score: {score:.1f}%")
    logger.info(f"  Status: {status}")
    
    # Log detailed breakdown
    missing_in_flow = [attack for attack, data in analysis.items() if "MISSING IN FLOW" in data['status']]
    missing_in_packet = [attack for attack, data in analysis.items() if "MISSING IN PACKET" in data['status']]
    poor_alignment = [attack for attack, data in analysis.items() if "⚠️" in data['status']]
    
    if missing_in_flow:
        logger.warning(f"Missing in flow data: {', '.join(missing_in_flow)}")
    if missing_in_packet:
        logger.warning(f"Missing in packet data: {', '.join(missing_in_packet)}")
    if poor_alignment:
        logger.warning(f"Poor alignment: {', '.join(poor_alignment)}")
    
    # Suggest improvements
    if missing_in_flow and packet_timeline and flow_timeline:
        latest_packet = max([data['end'] for data in packet_timeline.values()])
        latest_flow = max([data['end'] for data in flow_timeline.values()])
        if latest_packet > latest_flow:
            additional_time = latest_packet - latest_flow
            logger.info(f"Suggestion: Add {additional_time:.0f}s to flow collection duration")
    
    return {
        'score': score,
        'status': status,
        'analysis': analysis,
        'packet_timeline': packet_timeline,
        'flow_timeline': flow_timeline,
        'good_matches': good_matches,
        'total_attacks': total_attacks,
        'missing_in_flow': missing_in_flow,
        'missing_in_packet': missing_in_packet,
        'poor_alignment': poor_alignment
    }

def print_detailed_timeline_report(analysis_results, logger=None):
    """Print detailed timeline analysis report."""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    analysis = analysis_results['analysis']
    packet_timeline = analysis_results['packet_timeline']
    flow_timeline = analysis_results['flow_timeline']
    
    logger.info("\n" + "="*80)
    logger.info("📊 DETAILED TIMELINE ANALYSIS REPORT")
    logger.info("="*80)
    
    # Header
    logger.info(f"{'Attack Type':<15} {'Packet Timeline':<25} {'Flow Timeline':<25} {'Overlap':<10} {'Status':<20}")
    logger.info("-" * 100)
    
    for attack in sorted(analysis.keys()):
        data = analysis[attack]
        packet_data = data['packet_data']
        flow_data = data['flow_data']
        
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
        
        # Format overlap
        if data['overlap_duration'] > 0:
            overlap_info = format_duration(data['overlap_duration'])
        else:
            overlap_info = "NONE"
        
        logger.info(f"{attack:<15} {packet_info:<25} {flow_info:<25} {overlap_info:<10} {data['status']:<20}")
    
    # Detailed timing information
    logger.info("\n" + "="*80)
    logger.info("🕐 DETAILED TIMING INFORMATION")
    logger.info("="*80)
    
    for attack in sorted(analysis.keys()):
        data = analysis[attack]
        packet_data = data['packet_data']
        flow_data = data['flow_data']
        
        logger.info(f"\n📍 {attack.upper()}:")
        
        if packet_data:
            logger.info(f"   Packet: {format_timestamp(packet_data['start'])} - {format_timestamp(packet_data['end'])} ({format_duration(packet_data['duration'])})")
        else:
            logger.info(f"   Packet: MISSING")
            
        if flow_data:
            logger.info(f"   Flow:   {format_timestamp(flow_data['start'])} - {format_timestamp(flow_data['end'])} ({format_duration(flow_data['duration'])})")
        else:
            logger.info(f"   Flow:   MISSING")
        
        if packet_data and flow_data:
            logger.info(f"   Gap:    Start±{data['start_gap']:.1f}s, End±{data['end_gap']:.1f}s")
    
    logger.info("="*80)
