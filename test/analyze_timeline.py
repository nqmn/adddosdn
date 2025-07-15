#!/usr/bin/env python3
"""
Timeline Analysis Script for SDN DDoS Dataset Generation

This script analyzes the timeline alignment between packet_features.csv and flow_features.csv
to ensure proper synchronization of attack phases and identify any missing coverage.

Usage:
    python3 analyze_timeline.py [output_directory]
    
Default output directory: test_output/
"""

import csv
import sys
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def read_csv_timeline(csv_file, timestamp_col, label_col):
    """Read CSV file and extract timeline information for each attack type."""
    if not os.path.exists(csv_file):
        print(f"❌ ERROR: File not found: {csv_file}")
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
                    timeline_data[label].append(timestamp)
                    
    except Exception as e:
        print(f"❌ ERROR reading {csv_file}: {e}")
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

def print_timeline_table(packet_timeline, flow_timeline, analysis):
    """Print a formatted timeline comparison table."""
    print("\n" + "="*100)
    print("📊 TIMELINE ANALYSIS RESULTS")
    print("="*100)
    
    # Header
    print(f"{'Attack Type':<12} {'Packet Timeline':<25} {'Flow Timeline':<25} {'Overlap':<8} {'Status':<20}")
    print("-" * 100)
    
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
        
        print(f"{attack:<12} {packet_info:<25} {flow_info:<25} {overlap_info:<8} {data['status']:<20}")

def print_detailed_timing(packet_timeline, flow_timeline, analysis):
    """Print detailed timing information."""
    print("\n" + "="*80)
    print("🕐 DETAILED TIMING INFORMATION")
    print("="*80)
    
    for attack in sorted(analysis.keys()):
        data = analysis[attack]
        packet_data = data['packet_data']
        flow_data = data['flow_data']
        
        print(f"\n📍 {attack.upper()}:")
        
        if packet_data:
            print(f"   Packet: {format_timestamp(packet_data['start'])} - {format_timestamp(packet_data['end'])} ({format_duration(packet_data['duration'])})")
        else:
            print(f"   Packet: MISSING")
            
        if flow_data:
            print(f"   Flow:   {format_timestamp(flow_data['start'])} - {format_timestamp(flow_data['end'])} ({format_duration(flow_data['duration'])})")
        else:
            print(f"   Flow:   MISSING")
        
        if packet_data and flow_data:
            print(f"   Gap:    Start±{data['start_gap']:.1f}s, End±{data['end_gap']:.1f}s")

def print_summary_statistics(packet_timeline, flow_timeline, analysis):
    """Print summary statistics."""
    total_attacks = len(analysis)
    good_matches = len([a for a in analysis.values() if "✅" in a['status']])
    missing_in_flow = len([a for a in analysis.values() if "MISSING IN FLOW" in a['status']])
    missing_in_packet = len([a for a in analysis.values() if "MISSING IN PACKET" in a['status']])
    poor_overlap = len([a for a in analysis.values() if "⚠️" in a['status']])
    
    print("\n" + "="*60)
    print("📈 SUMMARY STATISTICS")
    print("="*60)
    print(f"Total attack types: {total_attacks}")
    print(f"✅ Good alignment: {good_matches}")
    print(f"❌ Missing in flow: {missing_in_flow}")
    print(f"❌ Missing in packet: {missing_in_packet}")
    print(f"⚠️  Poor alignment: {poor_overlap}")
    
    # Overall score
    score = (good_matches / total_attacks * 100) if total_attacks > 0 else 0
    print(f"\n🎯 Overall Alignment Score: {score:.1f}%")
    
    if score >= 90:
        print("🎉 EXCELLENT: Timeline alignment is very good!")
    elif score >= 70:
        print("👍 GOOD: Timeline alignment is acceptable with minor issues.")
    elif score >= 50:
        print("⚠️  FAIR: Timeline alignment needs improvement.")
    else:
        print("❌ POOR: Timeline alignment has major issues that need fixing.")

def suggest_improvements(analysis, packet_timeline, flow_timeline):
    """Suggest improvements based on analysis results."""
    print("\n" + "="*60)
    print("💡 IMPROVEMENT SUGGESTIONS")
    print("="*60)
    
    missing_in_flow = [attack for attack, data in analysis.items() if "MISSING IN FLOW" in data['status']]
    missing_in_packet = [attack for attack, data in analysis.items() if "MISSING IN PACKET" in data['status']]
    poor_timing = [attack for attack, data in analysis.items() if data['start_gap'] > 10 or data['end_gap'] > 10]
    
    if missing_in_flow:
        print(f"🔧 Flow collection ends too early - missing: {', '.join(missing_in_flow)}")
        print("   Solution: Increase flow collection duration in test.py/main.py")
        
        # Calculate required additional time
        if packet_timeline:
            latest_packet = max([data['end'] for data in packet_timeline.values()])
            latest_flow = max([data['end'] for data in flow_timeline.values()]) if flow_timeline else 0
            additional_time = latest_packet - latest_flow
            print(f"   Recommended: Add {additional_time:.0f}s to flow collection duration")
    
    if missing_in_packet:
        print(f"🔧 Packet capture missing: {', '.join(missing_in_packet)}")
        print("   Solution: Check packet capture timing and PCAP file processing")
    
    if poor_timing:
        print(f"🔧 Poor timing alignment for: {', '.join(poor_timing)}")
        print("   Solution: Check dynamic timeline updates in attack phases")
    
    # Check if flow collection duration is adequate
    if packet_timeline and flow_timeline:
        packet_total_duration = max([data['end'] for data in packet_timeline.values()]) - min([data['start'] for data in packet_timeline.values()])
        flow_total_duration = max([data['end'] for data in flow_timeline.values()]) - min([data['start'] for data in flow_timeline.values()])
        
        print(f"\n📊 Collection Duration Analysis:")
        print(f"   Packet data spans: {packet_total_duration:.1f}s")
        print(f"   Flow data spans: {flow_total_duration:.1f}s")
        
        if packet_total_duration > flow_total_duration + 10:
            shortage = packet_total_duration - flow_total_duration
            print(f"   ⚠️  Flow collection {shortage:.1f}s shorter than needed")

def main():
    """Main function to run timeline analysis."""
    # Get output directory from command line or use default
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = "test_output"
    
    output_path = Path(output_dir)
    packet_csv = output_path / "packet_features.csv"
    flow_csv = output_path / "flow_features.csv"
    
    print("🔍 SDN DDoS Dataset Timeline Analysis")
    print(f"📁 Analysis directory: {output_path.absolute()}")
    print(f"📄 Packet data: {packet_csv}")
    print(f"📄 Flow data: {flow_csv}")
    
    # Read timeline data
    print("\n📖 Reading timeline data...")
    packet_timeline = read_csv_timeline(packet_csv, timestamp_col=0, label_col=13)  # timestamp, Label_multi
    flow_timeline = read_csv_timeline(flow_csv, timestamp_col=0, label_col=16)      # timestamp, Label_multi
    
    if not packet_timeline and not flow_timeline:
        print("❌ No data found in either file. Exiting.")
        return
    
    # Perform analysis
    analysis = analyze_coverage(packet_timeline, flow_timeline)
    
    # Print results
    print_timeline_table(packet_timeline, flow_timeline, analysis)
    print_detailed_timing(packet_timeline, flow_timeline, analysis)
    print_summary_statistics(packet_timeline, flow_timeline, analysis)
    suggest_improvements(analysis, packet_timeline, flow_timeline)
    
    print(f"\n✅ Analysis complete for {output_dir}/")

if __name__ == "__main__":
    main()