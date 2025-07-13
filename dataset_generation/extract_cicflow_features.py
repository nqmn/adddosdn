#!/usr/bin/env python3
"""
CICFlowMeter Feature Extraction Script
Extracts 83 network flow features from PCAP files using CICFlowMeter
Includes multi-class and binary labeling based on attack types
"""

import os
import sys
import subprocess
import pandas as pd
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CICFlowFeatureExtractor:
    def __init__(self, pcap_dir, output_dir):
        self.pcap_dir = Path(pcap_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Label mappings from the label files
        self.multi_labels = {
            'normal': 0,
            'syn_flood': 1,
            'udp_flood': 2,
            'icmp_flood': 3,
            'ad_syn': 4,
            'ad_udp': 5,
            'ad_slow': 6
        }
        
        self.binary_labels = {
            'normal': 0,
            'syn_flood': 1,
            'udp_flood': 1,
            'icmp_flood': 1,
            'ad_syn': 1,
            'ad_udp': 1,
            'ad_slow': 1
        }
        
        # PCAP file to attack type mapping
        self.pcap_attack_mapping = {
            'normal.pcap': 'normal',
            'syn_flood.pcap': 'syn_flood',
            'udp_flood.pcap': 'udp_flood',
            'icmp_flood.pcap': 'icmp_flood',
            'ad_syn.pcap': 'ad_syn',
            'ad_udp.pcap': 'ad_udp',
            'ad_slow.pcap': 'ad_slow'
        }

    def check_cicflowmeter(self):
        """Check if CICFlowMeter is installed and accessible"""
        try:
            result = subprocess.run(['cicflowmeter', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("CICFlowMeter is available")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.error("CICFlowMeter not found. Please install it:")
        logger.error("pip install cicflowmeter")
        logger.error("or")
        logger.error("git clone https://github.com/datthinh1801/cicflowmeter.git")
        logger.error("cd cicflowmeter && pip install .")
        return False

    def extract_features_from_pcap(self, pcap_file):
        """Extract features from a single PCAP file using CICFlowMeter"""
        if isinstance(pcap_file, str):
            pcap_file = Path(pcap_file)
        pcap_path = self.pcap_dir / pcap_file
        temp_output = self.output_dir / f"temp_{pcap_file.stem}_flows.csv"
        
        if not pcap_path.exists():
            logger.warning(f"PCAP file not found: {pcap_path}")
            return None
        
        logger.info(f"Processing {pcap_file}...")
        
        try:
            # Run CICFlowMeter
            cmd = [
                'cicflowmeter',
                '-f', str(pcap_path),
                '-c', str(temp_output)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"CICFlowMeter failed for {pcap_file}: {result.stderr}")
                logger.debug(f"CICFlowMeter stdout: {result.stdout}")
                return None
            
            # Check if output file was created
            if not temp_output.exists():
                logger.error(f"No output file generated for {pcap_file}")
                return None
            
            # Read the generated CSV
            try:
                df = pd.read_csv(temp_output)
                if len(df) == 0:
                    logger.warning(f"No flows found in output for {pcap_file}")
                    temp_output.unlink()
                    return None
                logger.info(f"Extracted {len(df)} flows from {pcap_file}")
            except pd.errors.EmptyDataError:
                logger.warning(f"CICFlowMeter generated empty output for {pcap_file}")
                temp_output.unlink()
                return None
            except Exception as e:
                logger.error(f"Error reading CICFlowMeter output for {pcap_file}: {e}")
                if temp_output.exists():
                    temp_output.unlink()
                return None
            
            # Clean up temporary file
            temp_output.unlink()
            
            return df
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout processing {pcap_file}")
            return None
        except Exception as e:
            logger.error(f"Error processing {pcap_file}: {e}")
            return None

    def add_labels(self, df, attack_type):
        """Add multi-class and binary labels to the dataframe"""
        df = df.copy()
        df['Label_Multi'] = self.multi_labels[attack_type]
        df['Label_Binary'] = self.binary_labels[attack_type]
        df['Attack_Type'] = attack_type
        return df

    def process_all_pcaps(self):
        """Process all PCAP files and combine into labeled datasets"""
        all_flows = []
        
        # Find PCAP files in the directory
        pcap_files = list(self.pcap_dir.glob("*.pcap"))
        
        if not pcap_files:
            logger.error(f"No PCAP files found in {self.pcap_dir}")
            return False
        
        logger.info(f"Found {len(pcap_files)} PCAP files")
        
        for pcap_file in pcap_files:
            # Determine attack type from filename
            attack_type = self.pcap_attack_mapping.get(pcap_file.name)
            
            if not attack_type:
                logger.warning(f"Unknown attack type for {pcap_file.name}, skipping...")
                continue
            
            # Extract features
            df = self.extract_features_from_pcap(pcap_file)
            
            if df is not None and len(df) > 0:
                # Add labels
                df_labeled = self.add_labels(df, attack_type)
                all_flows.append(df_labeled)
                logger.info(f"Added {len(df_labeled)} labeled flows for {attack_type}")
            else:
                logger.warning(f"No flows extracted from {pcap_file.name}")
        
        if not all_flows:
            logger.error("No flows were extracted from any PCAP files")
            return False
        
        # Combine all flows
        combined_df = pd.concat(all_flows, ignore_index=True)
        
        # Save combined dataset
        output_file = self.output_dir / "cicflow_features_all.csv"
        combined_df.to_csv(output_file, index=False)
        logger.info(f"Saved combined dataset with {len(combined_df)} flows to {output_file}")
        
        # Save summary statistics
        self.save_summary_stats(combined_df)
        
        return True

    def save_summary_stats(self, df):
        """Save summary statistics about the extracted features"""
        summary_file = self.output_dir / "feature_extraction_summary.txt"
        
        with open(summary_file, 'w') as f:
            f.write("CICFlowMeter Feature Extraction Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total flows extracted: {len(df)}\n")
            f.write(f"Total features: {len(df.columns)}\n\n")
            
            f.write("Flow distribution by attack type:\n")
            attack_counts = df['Attack_Type'].value_counts()
            for attack, count in attack_counts.items():
                f.write(f"  {attack}: {count} flows\n")
            f.write("\n")
            
            f.write("Multi-class label distribution:\n")
            multi_counts = df['Label_Multi'].value_counts().sort_index()
            for label, count in multi_counts.items():
                attack_name = [k for k, v in self.multi_labels.items() if v == label][0]
                f.write(f"  {label} ({attack_name}): {count} flows\n")
            f.write("\n")
            
            f.write("Binary label distribution:\n")
            binary_counts = df['Label_Binary'].value_counts().sort_index()
            for label, count in binary_counts.items():
                label_name = "Normal" if label == 0 else "Attack"
                f.write(f"  {label} ({label_name}): {count} flows\n")
            f.write("\n")
            
            f.write("Feature columns:\n")
            for i, col in enumerate(df.columns, 1):
                f.write(f"  {i:2d}. {col}\n")
        
        logger.info(f"Summary statistics saved to {summary_file}")

def main():
    parser = argparse.ArgumentParser(description='Extract CICFlowMeter features from PCAP files')
    parser.add_argument('--pcap-dir', default='.',
                       help='Directory containing PCAP files (default: current directory)')
    parser.add_argument('--output-dir', default='cicflow_output',
                       help='Output directory for extracted features (default: cicflow_output)')
    
    args = parser.parse_args()
    
    # Convert to absolute paths
    script_dir = Path(__file__).parent
    pcap_dir = script_dir / args.pcap_dir
    output_dir = script_dir / args.output_dir
    
    if not pcap_dir.exists():
        logger.error(f"PCAP directory not found: {pcap_dir}")
        sys.exit(1)
    
    extractor = CICFlowFeatureExtractor(pcap_dir, output_dir)
    
    # Check CICFlowMeter availability
    if not extractor.check_cicflowmeter():
        sys.exit(1)
    
    # Process all PCAP files
    success = extractor.process_all_pcaps()
    
    if success:
        logger.info("Feature extraction completed successfully!")
        logger.info(f"Output files saved to: {output_dir}")
    else:
        logger.error("Feature extraction failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()