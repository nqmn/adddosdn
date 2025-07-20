#!/usr/bin/env python3
"""
Real-Time 30-Feature Network Traffic Extractor
Extracts only the optimal 30 features for real-time DDoS detection
Designed for live traffic processing with <1ms latency per packet

Features: 28 extractable + 2 labels = 30 total
No statistical calculations, no flow aggregations
Direct packet header field extraction only
"""

import time
import csv
import sys
import argparse
import logging
from pathlib import Path
from scapy.all import sniff, rdpcap, IP, TCP, UDP, ICMP, Ether, CookedLinux

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTime30FeatureExtractor:
    def __init__(self, output_file=None, interface=None, pcap_file=None):
        """
        Initialize real-time feature extractor
        
        Args:
            output_file: CSV file to save features
            interface: Network interface for live capture  
            pcap_file: PCAP file for offline processing
        """
        self.output_file = output_file or "realtime_features.csv"
        self.interface = interface
        self.pcap_file = pcap_file
        self.packet_count = 0
        
        # Attack type detection patterns
        self.attack_patterns = {
            'normal': ['normal', 'benign'],
            'syn_flood': ['syn_flood', 'syn'],
            'udp_flood': ['udp_flood', 'udp'], 
            'icmp_flood': ['icmp_flood', 'icmp'],
            'ad_syn': ['ad_syn'],
            'ad_udp': ['ad_udp'],
            'ad_slow': ['ad_slow', 'slow']
        }
        
        # Label mappings
        self.multi_labels = {
            'normal': 0, 'syn_flood': 1, 'udp_flood': 2, 'icmp_flood': 3,
            'ad_syn': 4, 'ad_udp': 5, 'ad_slow': 6
        }
        
        self.binary_labels = {
            'normal': 0, 'syn_flood': 1, 'udp_flood': 1, 'icmp_flood': 1,
            'ad_syn': 1, 'ad_udp': 1, 'ad_slow': 1
        }
        
        # Initialize CSV file
        self._initialize_csv()
        
    def _initialize_csv(self):
        """Initialize CSV file with 30-feature header"""
        header = [
            # Pure live extractable (24 features)
            'eth_type', 'ip_src', 'ip_dst', 'ip_proto', 'ip_ttl', 'ip_id', 
            'ip_flags', 'ip_len', 'ip_tos', 'ip_version', 'ip_frag_offset',
            'src_port', 'dst_port', 'tcp_flags', 'tcp_seq', 'tcp_ack', 
            'tcp_window', 'tcp_urgent', 'udp_sport', 'udp_dport', 'udp_len', 
            'udp_checksum', 'icmp_type', 'icmp_code', 'icmp_id', 'icmp_seq',
            
            # Minimal calculation (4 features)
            'timestamp', 'packet_length', 'transport_protocol', 'tcp_options_len',
            
            # Labels (2 features)
            'Label_multi', 'Label_binary'
        ]
        
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        
        logger.info(f"Initialized CSV file: {self.output_file}")
    
    def _detect_attack_type(self, source_info=""):
        """Detect attack type from source information (filename, interface, etc.)"""
        source_lower = source_info.lower()
        
        for attack_type, patterns in self.attack_patterns.items():
            if any(pattern in source_lower for pattern in patterns):
                return attack_type
        
        return 'normal'  # Default to normal if no pattern matches
    
    def extract_30_features(self, packet, attack_type='normal'):
        """
        Extract exactly 30 features from a network packet
        Real-time optimized - direct header field access only
        
        Args:
            packet: Scapy packet object
            attack_type: Attack type for labeling
            
        Returns:
            dict: 30 features (28 extractable + 2 labels)
        """
        # Initialize all features with empty values
        features = {
            # Pure live extractable (24 features) - initialized empty
            'eth_type': '', 'ip_src': '', 'ip_dst': '', 'ip_proto': '', 'ip_ttl': '', 
            'ip_id': '', 'ip_flags': '', 'ip_len': '', 'ip_tos': '', 'ip_version': '', 
            'ip_frag_offset': '', 'src_port': '', 'dst_port': '', 'tcp_flags': '', 
            'tcp_seq': '', 'tcp_ack': '', 'tcp_window': '', 'tcp_urgent': '', 
            'udp_sport': '', 'udp_dport': '', 'udp_len': '', 'udp_checksum': '', 
            'icmp_type': '', 'icmp_code': '', 'icmp_id': '', 'icmp_seq': '',
            
            # Minimal calculation (4 features)
            'timestamp': time.time(),
            'packet_length': len(packet),
            'transport_protocol': '',
            'tcp_options_len': '',
            
            # Labels (2 features)
            'Label_multi': self.multi_labels.get(attack_type, 0),
            'Label_binary': self.binary_labels.get(attack_type, 0)
        }
        
        # Extract link layer - Ethernet type
        if Ether in packet:
            features['eth_type'] = hex(packet[Ether].type)
        elif CookedLinux in packet:
            features['eth_type'] = hex(packet[CookedLinux].proto)
        
        # Extract IP layer features
        if IP in packet:
            ip = packet[IP]
            features.update({
                'ip_src': ip.src,
                'ip_dst': ip.dst,
                'ip_proto': ip.proto,
                'ip_ttl': ip.ttl,
                'ip_id': ip.id,
                'ip_flags': str(ip.flags),
                'ip_len': ip.len,
                'ip_tos': ip.tos,
                'ip_version': ip.version,
                'ip_frag_offset': ip.frag
            })
            
            # Extract transport layer features based on protocol
            if TCP in packet:
                tcp = packet[TCP]
                features.update({
                    'src_port': tcp.sport,
                    'dst_port': tcp.dport,
                    'tcp_flags': str(tcp.flags),
                    'tcp_seq': tcp.seq,
                    'tcp_ack': tcp.ack,
                    'tcp_window': tcp.window,
                    'tcp_urgent': tcp.urgptr,
                    'tcp_options_len': len(tcp.options) if hasattr(tcp, 'options') and tcp.options else 0,
                    'transport_protocol': 'TCP'
                })
                
            elif UDP in packet:
                udp = packet[UDP]
                features.update({
                    'udp_sport': udp.sport,
                    'udp_dport': udp.dport,
                    'udp_len': udp.len,
                    'udp_checksum': udp.chksum,
                    'transport_protocol': 'UDP'
                })
                
            elif ICMP in packet:
                icmp = packet[ICMP]
                features.update({
                    'icmp_type': icmp.type,
                    'icmp_code': icmp.code,
                    'icmp_id': icmp.id if hasattr(icmp, 'id') else '',
                    'icmp_seq': icmp.seq if hasattr(icmp, 'seq') else '',
                    'transport_protocol': 'ICMP'
                })
        
        return features
    
    def save_features_to_csv(self, features):
        """Save features to CSV file (append mode)"""
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write features in the exact order of the header
            row = [
                # Pure live extractable (24 features)
                features['eth_type'], features['ip_src'], features['ip_dst'], 
                features['ip_proto'], features['ip_ttl'], features['ip_id'],
                features['ip_flags'], features['ip_len'], features['ip_tos'], 
                features['ip_version'], features['ip_frag_offset'], features['src_port'],
                features['dst_port'], features['tcp_flags'], features['tcp_seq'], 
                features['tcp_ack'], features['tcp_window'], features['tcp_urgent'],
                features['udp_sport'], features['udp_dport'], features['udp_len'], 
                features['udp_checksum'], features['icmp_type'], features['icmp_code'],
                features['icmp_id'], features['icmp_seq'],
                
                # Minimal calculation (4 features)
                features['timestamp'], features['packet_length'], 
                features['transport_protocol'], features['tcp_options_len'],
                
                # Labels (2 features)
                features['Label_multi'], features['Label_binary']
            ]
            
            writer.writerow(row)
    
    def process_packet_realtime(self, packet, attack_type='normal'):
        """
        Process a single packet in real-time
        Optimized for <1ms processing time
        """
        try:
            # Extract 30 features
            features = self.extract_30_features(packet, attack_type)
            
            # Save to CSV
            self.save_features_to_csv(features)
            
            # Update counter
            self.packet_count += 1
            
            # Log progress every 1000 packets
            if self.packet_count % 1000 == 0:
                logger.info(f"Processed {self.packet_count} packets")
                
            return features
            
        except Exception as e:
            logger.error(f"Error processing packet {self.packet_count + 1}: {e}")
            return None
    
    def process_pcap_file(self, pcap_path, attack_type=None):
        """
        Process PCAP file and extract 30 features from all packets
        
        Args:
            pcap_path: Path to PCAP file
            attack_type: Override attack type detection
        """
        pcap_path = Path(pcap_path)
        
        if not pcap_path.exists():
            logger.error(f"PCAP file not found: {pcap_path}")
            return False
        
        # Detect attack type from filename if not provided
        if attack_type is None:
            attack_type = self._detect_attack_type(pcap_path.name)
        
        logger.info(f"Processing PCAP file: {pcap_path}")
        logger.info(f"Detected attack type: {attack_type}")
        
        try:
            # Load PCAP file
            packets = rdpcap(str(pcap_path))
            logger.info(f"Loaded {len(packets)} packets")
            
            # Process each packet
            start_time = time.time()
            
            for i, packet in enumerate(packets):
                self.process_packet_realtime(packet, attack_type)
                
                # Progress update every 5000 packets
                if (i + 1) % 5000 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    logger.info(f"Processed {i + 1}/{len(packets)} packets ({rate:.0f} pps)")
            
            # Final statistics
            total_time = time.time() - start_time
            avg_rate = len(packets) / total_time if total_time > 0 else 0
            avg_time_per_packet = (total_time / len(packets)) * 1000 if len(packets) > 0 else 0
            
            logger.info(f"Completed processing {len(packets)} packets")
            logger.info(f"Total time: {total_time:.2f} seconds")
            logger.info(f"Average rate: {avg_rate:.0f} packets/second")
            logger.info(f"Average time per packet: {avg_time_per_packet:.2f} ms")
            logger.info(f"Features saved to: {self.output_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing PCAP file: {e}")
            return False
    
    def start_live_capture(self, interface, attack_type='normal', packet_count=None):
        """
        Start live packet capture and real-time feature extraction
        
        Args:
            interface: Network interface name (e.g., 'eth0', 'wlan0')
            attack_type: Attack type for labeling
            packet_count: Maximum packets to capture (None for infinite)
        """
        logger.info(f"Starting live capture on interface: {interface}")
        logger.info(f"Attack type: {attack_type}")
        logger.info(f"Output file: {self.output_file}")
        
        def packet_handler(packet):
            """Handle each captured packet"""
            self.process_packet_realtime(packet, attack_type)
        
        try:
            # Start packet capture
            sniff(
                iface=interface,
                prn=packet_handler,
                count=packet_count,
                filter="ip"  # Only capture IP packets
            )
            
        except PermissionError:
            logger.error("Permission denied. Try running with sudo for live capture.")
            return False
        except Exception as e:
            logger.error(f"Error during live capture: {e}")
            return False
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Real-Time 30-Feature Network Traffic Extractor')
    parser.add_argument('--output', '-o', default='realtime_features.csv',
                       help='Output CSV file (default: realtime_features.csv)')
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--pcap', help='Process PCAP file')
    mode_group.add_argument('--interface', '-i', help='Network interface for live capture')
    
    # Optional arguments
    parser.add_argument('--attack-type', choices=['normal', 'syn_flood', 'udp_flood', 'icmp_flood', 'ad_syn', 'ad_udp', 'ad_slow'],
                       help='Attack type for labeling (auto-detected for PCAP files)')
    parser.add_argument('--count', type=int, help='Maximum packets to capture (live mode only)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize extractor
    extractor = RealTime30FeatureExtractor(output_file=args.output)
    
    try:
        if args.pcap:
            # PCAP file mode
            success = extractor.process_pcap_file(args.pcap, args.attack_type)
            
        elif args.interface:
            # Live capture mode
            attack_type = args.attack_type or 'normal'
            success = extractor.start_live_capture(args.interface, attack_type, args.count)
        
        if success:
            logger.info("Feature extraction completed successfully!")
        else:
            logger.error("Feature extraction failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        logger.info(f"Processed {extractor.packet_count} packets before interruption")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()