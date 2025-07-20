#!/usr/bin/env python3
"""
Example Usage for Real-Time 30-Feature Extractor
Demonstrates different ways to use the real-time feature extractor
"""

import time
import pandas as pd
from pathlib import Path
from realtime_30_feature_extractor import RealTime30FeatureExtractor

def example_pcap_processing():
    """Example: Process PCAP file and extract 30 features"""
    print("=== PCAP File Processing Example ===")
    
    # Initialize extractor
    extractor = RealTime30FeatureExtractor(output_file="example_pcap_features.csv")
    
    # Process PCAP file (example path - adjust as needed)
    pcap_file = "dataset_generation/main_output/v2_main/190725-1/normal.pcap"
    
    if Path(pcap_file).exists():
        print(f"Processing PCAP file: {pcap_file}")
        success = extractor.process_pcap_file(pcap_file)
        
        if success:
            # Load and display results
            df = pd.read_csv("example_pcap_features.csv")
            print(f"Extracted features from {len(df)} packets")
            print(f"Feature columns: {list(df.columns)}")
            print(f"Protocol distribution:")
            print(df['transport_protocol'].value_counts())
            print(f"Attack type distribution:")
            print(df['Label_multi'].value_counts())
    else:
        print(f"PCAP file not found: {pcap_file}")

def example_live_capture():
    """Example: Live network capture (requires sudo)"""
    print("=== Live Capture Example ===")
    print("Note: This requires sudo privileges for packet capture")
    
    # Initialize extractor
    extractor = RealTime30FeatureExtractor(output_file="example_live_features.csv")
    
    # Start live capture (uncomment to use)
    # Replace 'eth0' with your network interface
    # extractor.start_live_capture('eth0', attack_type='normal', packet_count=100)

def example_single_packet_processing():
    """Example: Process individual packets"""
    print("=== Single Packet Processing Example ===")
    
    from scapy.all import IP, TCP, Ether
    
    # Create a sample packet
    packet = Ether()/IP(src="192.168.1.10", dst="192.168.1.1")/TCP(sport=12345, dport=80, flags="S")
    
    # Initialize extractor
    extractor = RealTime30FeatureExtractor(output_file="example_single_packet.csv")
    
    # Extract features from single packet
    features = extractor.extract_30_features(packet, attack_type='syn_flood')
    
    print("Extracted 30 features:")
    for key, value in features.items():
        if value:  # Only show non-empty features
            print(f"  {key}: {value}")
    
    # Save to CSV
    extractor.save_features_to_csv(features)
    print("Features saved to CSV")

def example_batch_pcap_processing():
    """Example: Process multiple PCAP files"""
    print("=== Batch PCAP Processing Example ===")
    
    # PCAP files to process
    pcap_files = {
        "dataset_generation/main_output/v2_main/190725-1/normal.pcap": "normal",
        "dataset_generation/main_output/v2_main/190725-1/syn_flood.pcap": "syn_flood",
        "dataset_generation/main_output/v2_main/190725-1/udp_flood.pcap": "udp_flood",
        "dataset_generation/main_output/v2_main/190725-1/icmp_flood.pcap": "icmp_flood"
    }
    
    # Initialize extractor
    extractor = RealTime30FeatureExtractor(output_file="example_batch_features.csv")
    
    total_packets = 0
    start_time = time.time()
    
    for pcap_file, attack_type in pcap_files.items():
        if Path(pcap_file).exists():
            print(f"Processing {attack_type}: {pcap_file}")
            initial_count = extractor.packet_count
            
            success = extractor.process_pcap_file(pcap_file, attack_type)
            
            if success:
                packets_processed = extractor.packet_count - initial_count
                total_packets += packets_processed
                print(f"  Processed {packets_processed} packets")
        else:
            print(f"  File not found: {pcap_file}")
    
    # Summary
    total_time = time.time() - start_time
    if total_time > 0:
        avg_rate = total_packets / total_time
        print(f"\nBatch processing completed:")
        print(f"  Total packets: {total_packets}")
        print(f"  Total time: {total_time:.2f} seconds")
        print(f"  Average rate: {avg_rate:.0f} packets/second")

def example_feature_analysis():
    """Example: Analyze extracted features"""
    print("=== Feature Analysis Example ===")
    
    # Check if we have extracted features
    feature_files = ["example_pcap_features.csv", "example_batch_features.csv"]
    
    for file_path in feature_files:
        if Path(file_path).exists():
            print(f"\nAnalyzing {file_path}:")
            df = pd.read_csv(file_path)
            
            print(f"  Total packets: {len(df)}")
            print(f"  Features extracted: {len(df.columns)}")
            
            # Protocol analysis
            if 'transport_protocol' in df.columns:
                print(f"  Protocol distribution:")
                protocol_dist = df['transport_protocol'].value_counts()
                for protocol, count in protocol_dist.items():
                    print(f"    {protocol}: {count} packets")
            
            # Attack type analysis
            if 'Label_multi' in df.columns:
                print(f"  Attack type distribution:")
                attack_dist = df['Label_multi'].value_counts()
                attack_names = {0: 'normal', 1: 'syn_flood', 2: 'udp_flood', 
                              3: 'icmp_flood', 4: 'ad_syn', 5: 'ad_udp', 6: 'ad_slow'}
                for label, count in attack_dist.items():
                    attack_name = attack_names.get(label, f"unknown_{label}")
                    print(f"    {attack_name}: {count} packets")
            
            # Packet size analysis
            if 'packet_length' in df.columns:
                sizes = df['packet_length'].astype(float)
                print(f"  Packet size stats:")
                print(f"    Min: {sizes.min():.0f} bytes")
                print(f"    Max: {sizes.max():.0f} bytes")
                print(f"    Mean: {sizes.mean():.2f} bytes")
        else:
            print(f"Feature file not found: {file_path}")

def main():
    """Run all examples"""
    print("Real-Time 30-Feature Extractor - Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_single_packet_processing()
    print()
    
    example_pcap_processing()
    print()
    
    # example_live_capture()  # Commented out - requires sudo
    # print()
    
    example_batch_pcap_processing()
    print()
    
    example_feature_analysis()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nGenerated files:")
    print("  - example_single_packet.csv")
    print("  - example_pcap_features.csv") 
    print("  - example_batch_features.csv")
    print("\nFor live capture, run with sudo:")
    print("  sudo python3 realtime_30_feature_extractor.py --interface eth0 --attack-type normal")

if __name__ == "__main__":
    main()