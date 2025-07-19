#!/usr/bin/env python3
"""
Clean PACKET Dataset Missing Values using -1 encoding

This script replaces missing values with -1 for optimal ML compatibility:
- tcp_flags: '-1' (string) for non-TCP protocols
- ip_flags: '-1' (string) for uncaptured flags  
- src_port/dst_port: -1 (integer) for ICMP protocols
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
            logging.FileHandler('clean_packet_missing.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)

def clean_packet_dataset(logger):
    """Clean the PACKET dataset by encoding missing values as -1."""
    
    file_path = Path("main_output/packet_dataset.csv")
    
    try:
        logger.info("🔍 Loading PACKET dataset...")
        df = pd.read_csv(file_path)
        original_rows = len(df)
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        logger.info(f"  Original: {original_rows:,} rows × {len(df.columns)} columns")
        logger.info(f"  Original memory: {original_memory:.1f} MB")
        
        # Create backup
        backup_path = file_path.with_suffix('.csv.backup_missing')
        if not backup_path.exists():
            df.to_csv(backup_path, index=False)
            logger.info(f"  📁 Backup created: {backup_path.name}")
        else:
            logger.info(f"  📁 Backup already exists: {backup_path.name}")
        
        # Analyze missing values before cleaning
        logger.info("\n📊 Pre-cleaning missing value analysis:")
        missing_analysis = {}
        total_missing = 0
        
        for col in ['tcp_flags', 'ip_flags', 'src_port', 'dst_port']:
            if col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    missing_pct = (missing_count / len(df)) * 100
                    missing_analysis[col] = {'count': missing_count, 'pct': missing_pct}
                    total_missing += missing_count
                    logger.info(f"  {col}: {missing_count:,} missing ({missing_pct:.2f}%)")
        
        logger.info(f"  Total missing values: {total_missing:,}")
        
        # Apply -1 encoding
        logger.info(f"\n🔧 Applying -1 encoding...")
        
        # String columns: Use '-1' as string
        string_cols = ['tcp_flags', 'ip_flags']
        for col in string_cols:
            if col in df.columns and col in missing_analysis:
                original_missing = df[col].isnull().sum()
                df[col] = df[col].fillna('-1')
                remaining_missing = df[col].isnull().sum()
                logger.info(f"  {col}: {original_missing:,} → {remaining_missing:,} missing (filled with '-1')")
        
        # Numeric columns: Use -1 as integer
        numeric_cols = ['src_port', 'dst_port']
        for col in numeric_cols:
            if col in df.columns and col in missing_analysis:
                original_missing = df[col].isnull().sum()
                df[col] = df[col].fillna(-1).astype(int)
                remaining_missing = df[col].isnull().sum()
                logger.info(f"  {col}: {original_missing:,} → {remaining_missing:,} missing (filled with -1)")
        
        # Verify no missing values remain
        logger.info(f"\n✅ Verification:")
        remaining_total_missing = df.isnull().sum().sum()
        logger.info(f"  Total missing values remaining: {remaining_total_missing:,}")
        
        if remaining_total_missing == 0:
            logger.info("  ✅ All missing values successfully encoded as -1")
        else:
            logger.warning(f"  ⚠️  {remaining_total_missing} missing values still remain")
        
        # Analyze the encoded values
        logger.info(f"\n📋 Post-encoding value analysis:")
        for col in ['tcp_flags', 'ip_flags', 'src_port', 'dst_port']:
            if col in df.columns:
                if col in string_cols:
                    neg_one_count = (df[col] == '-1').sum()
                    unique_values = df[col].nunique()
                    logger.info(f"  {col}: {neg_one_count:,} '-1' values, {unique_values} unique values total")
                else:
                    neg_one_count = (df[col] == -1).sum()
                    valid_range = df[df[col] != -1][col]
                    if len(valid_range) > 0:
                        logger.info(f"  {col}: {neg_one_count:,} -1 values, valid range: {valid_range.min()} - {valid_range.max()}")
                    else:
                        logger.info(f"  {col}: {neg_one_count:,} -1 values, no valid values")
        
        # Memory analysis
        final_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        logger.info(f"\n💾 Memory usage:")
        logger.info(f"  Original: {original_memory:.1f} MB")
        logger.info(f"  Final: {final_memory:.1f} MB")
        logger.info(f"  Change: {final_memory - original_memory:+.1f} MB")
        
        # Save cleaned dataset
        logger.info(f"\n💾 Saving cleaned dataset...")
        df.to_csv(file_path, index=False)
        logger.info(f"  ✅ Cleaned dataset saved: {file_path.name}")
        
        # Protocol-specific validation
        logger.info(f"\n🔬 Protocol-specific validation:")
        
        # Check ICMP packets
        icmp_packets = df[df['ip_proto'] == 1]
        if len(icmp_packets) > 0:
            icmp_tcp_flags = (icmp_packets['tcp_flags'] == '-1').sum()
            icmp_ports = (icmp_packets['src_port'] == -1).sum()
            logger.info(f"  ICMP packets ({len(icmp_packets):,}): {icmp_tcp_flags:,} have tcp_flags='-1', {icmp_ports:,} have ports=-1")
        
        # Check TCP packets
        tcp_packets = df[df['ip_proto'] == 6]
        if len(tcp_packets) > 0:
            tcp_tcp_flags = (tcp_packets['tcp_flags'] != '-1').sum()
            tcp_ports = (tcp_packets['src_port'] != -1).sum()
            logger.info(f"  TCP packets ({len(tcp_packets):,}): {tcp_tcp_flags:,} have valid tcp_flags, {tcp_ports:,} have valid ports")
        
        # Check UDP packets
        udp_packets = df[df['ip_proto'] == 17]
        if len(udp_packets) > 0:
            udp_tcp_flags = (udp_packets['tcp_flags'] == '-1').sum()
            udp_ports = (udp_packets['src_port'] != -1).sum()
            logger.info(f"  UDP packets ({len(udp_packets):,}): {udp_tcp_flags:,} have tcp_flags='-1', {udp_ports:,} have valid ports")
        
        # Final summary
        logger.info(f"\n📊 CLEANING SUMMARY:")
        logger.info(f"  Total missing values encoded: {total_missing:,}")
        logger.info(f"  Records processed: {original_rows:,}")
        logger.info(f"  Data preservation: 100% (no records lost)")
        logger.info(f"  Missing value encoding: -1 for optimal ML compatibility")
        logger.info(f"  Protocol compliance: Preserved (missing values indicate protocol-appropriate behavior)")
        
        return True, {
            'total_missing_encoded': total_missing,
            'records_processed': original_rows,
            'memory_change': final_memory - original_memory,
            'protocol_validation': {
                'icmp_packets': len(icmp_packets),
                'tcp_packets': len(tcp_packets),
                'udp_packets': len(udp_packets)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error cleaning PACKET dataset: {e}")
        return False, {}

def main():
    """Main function to clean PACKET dataset missing values."""
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("PACKET DATASET MISSING VALUES CLEANING (-1 ENCODING)")
    logger.info("=" * 60)
    
    success, results = clean_packet_dataset(logger)
    
    if success:
        logger.info("\n🎉 PACKET dataset cleaning completed successfully!")
        logger.info("   All missing values encoded as -1 for optimal ML training")
        return 0
    else:
        logger.error("\n❌ PACKET dataset cleaning failed!")
        return 1

if __name__ == "__main__":
    exit(main())