#!/usr/bin/env python3
"""
Split Dataset CSV Files for GitHub Upload

This script splits large CSV dataset files into smaller chunks (< 100MB)
suitable for GitHub upload while preserving the original files.

Splits the three main dataset files:
- packet_dataset.csv
- flow_dataset.csv
- cicflow_dataset.csv

Usage:
    python3 split_datasets_for_github.py [--path PATH] [--chunk-size SIZE]

Arguments:
    --path PATH         Path to dataset directory (default: ../main_output/v4)
    --chunk-size SIZE   Maximum chunk size in MB (default: 95)
"""

import csv
import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('split_datasets.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)

def get_file_size_mb(file_path):
    """Get file size in megabytes."""
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path) / (1024 * 1024)

def estimate_rows_per_chunk(csv_file, max_size_mb):
    """Estimate how many rows can fit in a chunk of specified size."""
    if not os.path.exists(csv_file):
        return 0

    file_size_mb = get_file_size_mb(csv_file)

    # Count total rows (excluding header)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        total_rows = sum(1 for _ in reader)

    if total_rows == 0:
        return 0

    # Calculate rows per MB
    rows_per_mb = total_rows / file_size_mb

    # Estimate rows per chunk (with 10% safety margin)
    estimated_rows = int((max_size_mb * rows_per_mb) * 0.9)

    return max(1, estimated_rows)

def split_csv_file(input_file, output_dir, max_size_mb, logger):
    """Split a CSV file into chunks smaller than max_size_mb."""
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return False

    file_size_mb = get_file_size_mb(input_file)
    logger.info(f"Processing {input_file} ({file_size_mb:.1f} MB)")

    if file_size_mb <= max_size_mb:
        logger.info(f"File is already under {max_size_mb}MB, skipping split")
        return True

    # Estimate rows per chunk
    rows_per_chunk = estimate_rows_per_chunk(input_file, max_size_mb)
    logger.info(f"Estimated rows per chunk: {rows_per_chunk:,}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get base filename without extension
    base_name = Path(input_file).stem

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Read header

            chunk_num = 1
            row_count = 0
            current_chunk_rows = 0
            outfile = None
            writer = None

            for row in reader:
                # Start new chunk if needed
                if current_chunk_rows == 0:
                    if outfile:
                        outfile.close()
                        # Check actual file size
                        actual_size = get_file_size_mb(chunk_filename)
                        logger.info(f"  Chunk {chunk_num-1}: {current_chunk_rows:,} rows, {actual_size:.1f} MB")

                    chunk_filename = os.path.join(output_dir, f"{base_name}_part_{chunk_num:03d}.csv")
                    outfile = open(chunk_filename, 'w', newline='', encoding='utf-8')
                    writer = csv.writer(outfile)
                    writer.writerow(header)  # Write header to each chunk
                    chunk_num += 1

                # Write row to current chunk
                writer.writerow(row)
                current_chunk_rows += 1
                row_count += 1

                # Check if chunk is complete
                if current_chunk_rows >= rows_per_chunk:
                    current_chunk_rows = 0

            # Close last file
            if outfile:
                outfile.close()
                actual_size = get_file_size_mb(chunk_filename)
                logger.info(f"  Chunk {chunk_num-1}: {current_chunk_rows:,} rows, {actual_size:.1f} MB")

            total_chunks = chunk_num - 1
            logger.info(f"Split complete: {row_count:,} rows into {total_chunks} chunks")

            return True

    except Exception as e:
        logger.error(f"Error splitting {input_file}: {e}")
        return False

def create_chunk_info_file(dataset_path, chunk_dir, logger):
    """Create an info file explaining the chunks."""
    info_content = f"""# Dataset Chunks Information

This directory contains split versions of the large dataset CSV files for GitHub upload.

## Original Files Location
{dataset_path}/

## Chunk Information
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Maximum chunk size: 95 MB (GitHub limit: 100 MB)

## Files Split:
- packet_dataset.csv → packet_dataset_part_*.csv
- flow_dataset.csv → flow_dataset_part_*.csv
- cicflow_dataset.csv → cicflow_dataset_part_*.csv

## Reconstruction Instructions

To reconstruct the original files from chunks:

### Linux/Mac:
```bash
# Reconstruct packet dataset
head -n 1 packet_dataset_part_001.csv > packet_dataset.csv
tail -n +2 -q packet_dataset_part_*.csv >> packet_dataset.csv

# Reconstruct flow dataset
head -n 1 flow_dataset_part_001.csv > flow_dataset.csv
tail -n +2 -q flow_dataset_part_*.csv >> flow_dataset.csv

# Reconstruct cicflow dataset
head -n 1 cicflow_dataset_part_001.csv > cicflow_dataset.csv
tail -n +2 -q cicflow_dataset_part_*.csv >> cicflow_dataset.csv
```

### Windows (PowerShell):
```powershell
# Reconstruct packet dataset
Get-Content packet_dataset_part_001.csv | Select-Object -First 1 | Out-File packet_dataset.csv
Get-Content packet_dataset_part_*.csv | Select-Object -Skip 1 | Add-Content packet_dataset.csv

# Reconstruct flow dataset
Get-Content flow_dataset_part_001.csv | Select-Object -First 1 | Out-File flow_dataset.csv
Get-Content flow_dataset_part_*.csv | Select-Object -Skip 1 | Add-Content flow_dataset.csv

# Reconstruct cicflow dataset
Get-Content cicflow_dataset_part_001.csv | Select-Object -First 1 | Out-File cicflow_dataset.csv
Get-Content cicflow_dataset_part_*.csv | Select-Object -Skip 1 | Add-Content cicflow_dataset.csv
```

### Python Script:
```python
import pandas as pd
import glob

def reconstruct_dataset(pattern, output_file):
    chunks = sorted(glob.glob(pattern))
    dfs = [pd.read_csv(chunk) for chunk in chunks]
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(output_file, index=False)

# Reconstruct all datasets
reconstruct_dataset('packet_dataset_part_*.csv', 'packet_dataset.csv')
reconstruct_dataset('flow_dataset_part_*.csv', 'flow_dataset.csv')
reconstruct_dataset('cicflow_dataset_part_*.csv', 'cicflow_dataset.csv')
```

## Verification

After reconstruction, verify file integrity:
```bash
# Check line counts match
wc -l original_packet_dataset.csv reconstructed_packet_dataset.csv
wc -l original_flow_dataset.csv reconstructed_flow_dataset.csv
wc -l original_cicflow_dataset.csv reconstructed_cicflow_dataset.csv

# Check file sizes
ls -lh *_dataset.csv
```

## Notes
- Each chunk includes the CSV header row
- Chunks are numbered sequentially (001, 002, 003, ...)
- Original files are preserved in the main dataset directory
- All chunks should be downloaded before reconstruction
"""

    info_file = os.path.join(chunk_dir, "README_CHUNKS.md")
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(info_content)

    logger.info(f"Created chunk information file: {info_file}")

def main():
    """Main function to split dataset files."""
    parser = argparse.ArgumentParser(description='Split large CSV datasets for GitHub upload')
    parser.add_argument('--path', default='../main_output/v4',
                       help='Path to dataset directory (default: ../main_output/v4)')
    parser.add_argument('--chunk-size', type=int, default=95,
                       help='Maximum chunk size in MB (default: 95)')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()

    # Resolve dataset path
    dataset_path = Path(args.path)
    if not dataset_path.exists():
        logger.error(f"Dataset directory not found: {dataset_path}")
        return 1

    dataset_path = dataset_path.absolute()
    logger.info(f"Dataset directory: {dataset_path}")
    logger.info(f"Maximum chunk size: {args.chunk_size} MB")

    # Create chunks directory
    chunk_dir = dataset_path / "github_chunks"
    chunk_dir.mkdir(exist_ok=True)
    logger.info(f"Chunks will be saved to: {chunk_dir}")

    # Files to split
    files_to_split = [
        'packet_dataset.csv',
        'flow_dataset.csv',
        'cicflow_dataset.csv'
    ]

    success_count = 0
    total_files = len(files_to_split)

    # Process each file
    for filename in files_to_split:
        file_path = dataset_path / filename
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {filename}")
        logger.info(f"{'='*60}")

        if split_csv_file(file_path, chunk_dir, args.chunk_size, logger):
            success_count += 1
        else:
            logger.error(f"Failed to process {filename}")

    # Create information file
    create_chunk_info_file(dataset_path, chunk_dir, logger)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SPLITTING SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Files processed successfully: {success_count}/{total_files}")
    logger.info(f"Chunks saved to: {chunk_dir}")

    if success_count == total_files:
        logger.info("✅ All files split successfully!")
        logger.info(f"📁 Upload the contents of '{chunk_dir}' to GitHub")
        logger.info("📖 See README_CHUNKS.md for reconstruction instructions")
        return 0
    else:
        logger.error("❌ Some files failed to split")
        return 1

if __name__ == "__main__":
    exit(main())