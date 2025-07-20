#!/usr/bin/env python3
"""
Batch CICFlow Analyzer for v2_main Dataset Folders

This script runs the CICFlow analyzer on all subdirectories within v2_main
and saves the analysis results to cicflow_output/v2_main/.

Usage:
    python run_cicflow_v2_main.py
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cicflow_batch_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Define paths
    v2_main_dir = Path("/mnt/c/Users/Intel/Desktop/adddosdn/dataset_generation/main_output/v2_main")
    cicflow_analyzer_script = Path("/mnt/c/Users/Intel/Desktop/adddosdn/test/cicflow_analyzer.py")
    output_base_dir = Path("/mnt/c/Users/Intel/Desktop/adddosdn/cicflow_output/v2_main")
    
    # Verify paths exist
    if not v2_main_dir.exists():
        logger.error(f"v2_main directory not found: {v2_main_dir}")
        sys.exit(1)
    
    if not cicflow_analyzer_script.exists():
        logger.error(f"CICFlow analyzer script not found: {cicflow_analyzer_script}")
        sys.exit(1)
    
    # Create output directory
    output_base_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all subdirectories in v2_main (excluding files like flow_dataset.csv)
    subdirs = [d for d in v2_main_dir.iterdir() if d.is_dir()]
    
    if not subdirs:
        logger.error(f"No subdirectories found in {v2_main_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(subdirs)} directories to process in v2_main")
    
    # Process each subdirectory
    successful = 0
    failed = 0
    
    for subdir in sorted(subdirs):
        logger.info(f"Processing directory: {subdir.name}")
        
        # Create output directory for this specific analysis
        output_dir = output_base_dir / subdir.name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Run CICFlow analyzer in complete mode (extract and validate)
            cmd = [
                sys.executable,
                str(cicflow_analyzer_script),
                "complete",
                "--pcap-dir", str(subdir),
                "--output-dir", str(output_dir)
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully processed {subdir.name}")
                successful += 1
                
                # Log the output for debugging
                if result.stdout:
                    logger.debug(f"STDOUT for {subdir.name}: {result.stdout}")
            else:
                logger.error(f"❌ Failed to process {subdir.name}")
                logger.error(f"Return code: {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                failed += 1
                
                # Save error log
                error_file = output_dir / "error.log"
                with open(error_file, 'w') as f:
                    f.write(f"Command: {' '.join(cmd)}\n")
                    f.write(f"Return code: {result.returncode}\n")
                    f.write(f"STDERR:\n{result.stderr}\n")
                    f.write(f"STDOUT:\n{result.stdout}\n")
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout processing {subdir.name} (30 minutes)")
            failed += 1
        except Exception as e:
            logger.error(f"❌ Exception processing {subdir.name}: {e}")
            failed += 1
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"BATCH PROCESSING SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total directories: {len(subdirs)}")
    logger.info(f"Successfully processed: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Output directory: {output_base_dir}")
    logger.info(f"Log file: cicflow_batch_analysis.log")
    
    if successful > 0:
        logger.info(f"\n✅ Batch processing completed with {successful} successes")
        logger.info(f"📁 Results saved to: {output_base_dir}")
        
        # List generated outputs
        logger.info(f"\nGenerated analysis directories:")
        for output_dir in sorted(output_base_dir.iterdir()):
            if output_dir.is_dir():
                files = list(output_dir.glob("*"))
                logger.info(f"  {output_dir.name}: {len(files)} files")
    
    if failed > 0:
        logger.warning(f"\n⚠️ {failed} directories failed processing")
        logger.warning(f"Check error logs in individual output directories")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())