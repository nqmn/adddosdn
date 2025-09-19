# Dataset Chunks Information

This directory contains split versions of the large dataset CSV files for GitHub upload.

## Original Files Location
/mnt/c/Users/Intel/Desktop/adddosdn/dataset_generation/dataset_cleanup/../main_output/v4/

## Chunk Information
Generated on: 2025-09-19 12:37:37
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
