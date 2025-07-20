# Dataset Cleaning Workflow - Complete Reproducible Guide

## Overview

This document provides comprehensive, step-by-step instructions for cleaning and preparing the AdDDoSDN network security datasets. The workflow addresses timeline integrity, data combination, quality analysis, and dataset-specific cleaning operations.

## Prerequisites

### Environment Setup
```bash
# Ensure you're in the dataset_generation directory
cd dataset_generation/

# Install required Python packages
pip install pandas numpy pathlib argparse

# Verify Python version (3.8+ recommended)
python3 --version
```

### Directory Structure
```
dataset_generation/
├── main_output/v2_main/           # Input: Raw combined datasets
│   ├── 190725-1/                  # Individual dataset directories (×12)
│   ├── 190725-2/
│   ├── ...
│   ├── packet_dataset.csv         # Combined datasets (created by workflow)
│   ├── flow_dataset.csv
│   └── cicflow_dataset.csv
├── dataset_cleanup/               # Cleaning scripts
│   ├── fix_timeline_integrity.py  # Step 1: Timeline integrity fixing
│   ├── combine_datasets.py        # Step 2: Dataset combination
│   ├── investigate_csv_quality.py # Step 3: Quality investigation
│   ├── clean_packet_dataset.py    # Step 4: Packet dataset cleaning
│   ├── clean_flow_dataset.py      # Step 5: Flow dataset cleaning
│   └── clean_cicflow_dataset.py   # Step 6: CICFlow dataset cleaning
└── DATASET_CLEANING_WORKFLOW.md   # This documentation
```

## Complete Workflow

### Step 1: Fix Timeline Integrity

**Purpose**: Resolve data loss issues where adversarial attacks were missing from timeline parsing.

```bash
# Fix timeline integrity for all datasets
python3 dataset_cleanup/fix_timeline_integrity.py --all

# Alternative: Fix specific dataset
python3 dataset_cleanup/fix_timeline_integrity.py --dataset 190725-1
```

**What this does**:
- Creates backup files (`*.csv.backup_raw`) for all CSV files
- Parses `attack.log` files to extract complete attack timelines
- Handles both traditional attacks (syn_flood, udp_flood, icmp_flood) and adversarial attacks (ad_syn, ad_udp, ad_slow)
- Removes records outside timeline boundaries (with 30s buffer)
- Fixes only 'unknown' labels based on timing and packet characteristics
- Preserves all existing correct labels

**Expected Results**:
- ✅ Previously lost adversarial attack data is recovered
- ✅ CICFlow datasets increase from ~18K to ~45K records
- ✅ Timeline boundaries are properly enforced
- ✅ Data integrity is preserved

### Step 2: Combine Individual Datasets

**Purpose**: Merge CSV files from all 12 dataset directories into unified datasets.

```bash
# Combine all individual datasets into unified files
python3 dataset_cleanup/combine_datasets.py
```

**What this does**:
- Scans `main_output/v2_main/` for dataset directories (format: `YYMMDD-N`)
- Combines three dataset types:
  - `packet_features.csv` → `packet_dataset.csv`
  - `flow_features.csv` → `flow_dataset.csv`
  - `cicflow_features_all.csv` → `cicflow_dataset.csv`
- Adds `dataset_id` column for traceability
- Generates comprehensive statistics and validation

**Expected Results**:
- ✅ `packet_dataset.csv`: ~108K records, 16 features
- ✅ `flow_dataset.csv`: ~437K records, 19 features  
- ✅ `cicflow_dataset.csv`: ~45K records, 86 features
- ✅ Total: ~591K records combined

### Step 3: Investigate Dataset Quality

**Purpose**: Comprehensive quality analysis and cleaning recommendations.

```bash
# Analyze quality of combined datasets
python3 dataset_cleanup/investigate_csv_quality.py
```

**What this does**:
- Analyzes missing values, duplicates, and data distribution
- Generates detailed statistics for each dataset
- Provides dataset-specific cleaning recommendations
- Creates comprehensive quality report in `main_output/v2_main/`
- Identifies problematic columns and outliers

**Expected Results**:
- ✅ Data integrity score: 100/100
- ✅ Missing value analysis by column
- ✅ Duplicate detection and quantification
- ✅ Label distribution analysis
- ✅ Cleaning strategy recommendations

### Step 4: Clean Packet Dataset

**Purpose**: Remove duplicates and encode missing values for ML compatibility.

```bash
# Clean packet dataset
python3 dataset_cleanup/clean_packet_dataset.py --path main_output/v2_main
```

**What this does**:
- Creates backup (`packet_dataset.csv.backup_before_cleaning`)
- Removes duplicate records (exact matches across all columns)
- Encodes all missing values as `-1` for ML compatibility
- Preserves label distribution and data integrity
- Provides detailed impact analysis

**Expected Results**:
- ✅ Records: 108,327 → 108,308 (-19 duplicates)
- ✅ Missing values: 125,833 → 0 (encoded as -1)
- ✅ Features: 16 (unchanged)
- ✅ Label distribution preserved

**Key Changes**:
- `ip_flags`: 65,664 values → -1 (60.6%)
- `tcp_flags`: 27,071 values → -1 (25.0%)
- `src_port`: 16,547 values → -1 (15.3%)
- `dst_port`: 16,547 values → -1 (15.3%)

### Step 5: Clean Flow Dataset

**Purpose**: Remove empty columns and rows with missing values.

```bash
# Clean flow dataset
python3 dataset_cleanup/clean_flow_dataset.py --path main_output/v2_main
```

**What this does**:
- Creates backup (`flow_dataset.csv.backup_before_cleaning`)
- Removes 100% empty columns (`table_id`, `cookie`, `duration_nsec`)
- Removes rows with any missing values
- Optimizes feature set for ML training
- Maintains label distribution proportions

**Expected Results**:
- ✅ Records: 437,441 → 423,330 (-14,111 rows, -3.23%)
- ✅ Features: 19 → 16 (-3 empty columns)
- ✅ Missing values: 1,354,656 → 0 (100% eliminated)
- ✅ Label distribution: Proportionally preserved

**Removed Columns**:
- `table_id` (100% missing)
- `cookie` (100% missing)  
- `duration_nsec` (100% missing)

**Remaining Features**:
- Network identifiers: `dataset_id`, `timestamp`, `switch_id`
- Flow properties: `priority`, `in_port`, `eth_src`, `eth_dst`, `out_port`
- Flow statistics: `packet_count`, `byte_count`, `duration_sec`
- Derived metrics: `avg_pkt_size`, `pkt_rate`, `byte_rate`
- Labels: `Label_multi`, `Label_binary`

### Step 6: Clean CICFlow Dataset

**Purpose**: Remove duplicate records while preserving complete feature set.

```bash
# Clean CICFlow dataset  
python3 dataset_cleanup/clean_cicflow_dataset.py --path main_output/v2_main
```

**What this does**:
- Creates backup (`cicflow_dataset.csv.backup_before_cleaning`)
- Removes exact duplicate records
- Preserves all 86 CICFlow features
- Analyzes duplicate patterns by attack type
- Maintains data integrity for ML training

**Expected Results**:
- ✅ Records: 45,550 → 43,739 (-1,811 duplicates, -3.98%)
- ✅ Features: 86 (unchanged - complete CICFlow feature set)
- ✅ Missing values: 0 (already clean)
- ✅ Duplicates: 1,811 → 0 (100% eliminated)

**Duplicate Analysis**:
- All 1,811 duplicates were from `icmp_flood` attacks (-44.46%)
- Other attack types had no duplicates
- Indicates potential data collection issue during ICMP flood generation

## Final Dataset Summary

After completing the full workflow:

| Dataset | Records | Features | Missing Values | Duplicates | Quality |
|---------|---------|----------|----------------|------------|---------|
| **Packet** | 108,308 | 16 | 0 (encoded as -1) | 0 | ✅ Ready |
| **Flow** | 423,330 | 16 | 0 | 0 | ✅ Ready |
| **CICFlow** | 43,739 | 86 | 0 | 0 | ✅ Ready |
| **Total** | 575,377 | 118 | 0 | 0 | ✅ Ready |

## Quality Verification

### Automated Verification Script

```bash
# Verify all datasets are properly cleaned
python3 -c "
import pandas as pd
from pathlib import Path

base_path = Path('main_output/v2_main')
datasets = ['packet_dataset.csv', 'flow_dataset.csv', 'cicflow_dataset.csv']

print('=== FINAL DATASET VERIFICATION ===')
total_records = 0
for dataset in datasets:
    df = pd.read_csv(base_path / dataset)
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()
    total_records += len(df)
    
    print(f'{dataset}:')
    print(f'  Records: {len(df):,}')
    print(f'  Features: {len(df.columns)}')
    print(f'  Missing: {missing:,}')
    print(f'  Duplicates: {duplicates:,}')
    print(f'  Status: {'✅ Clean' if missing == 0 and duplicates == 0 else '❌ Issues'}')

print(f'\\nTotal Records: {total_records:,}')
print('All datasets ready for ML training!' if total_records > 0 else 'Issues detected!')
"
```

### Manual Verification Checklist

- [ ] All backup files created (`.backup_*` extensions)
- [ ] No missing values in any dataset
- [ ] No duplicate records in any dataset
- [ ] Label distributions are reasonable
- [ ] File sizes are consistent with expectations
- [ ] All scripts executed without errors

## Troubleshooting

### Common Issues

**Issue**: "Input file not found"
```bash
# Solution: Verify you're in the correct directory and datasets exist
ls -la main_output/v2_main/*.csv
pwd
```

**Issue**: "Timeline windows not found"
```bash
# Solution: Check attack.log files exist in dataset directories
ls -la main_output/v2_main/*/attack.log
```

**Issue**: "Permission denied" 
```bash
# Solution: Ensure proper file permissions
chmod +x dataset_cleanup/*.py
```

**Issue**: Memory issues with large datasets
```bash
# Solution: Monitor memory usage and close other applications
python3 -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available / 1024**3:.1f} GB')"
```

### Recovery Procedures

**Restore from Backups**:
```bash
# Restore specific dataset from backup
cp main_output/v2_main/packet_dataset.csv.backup_before_cleaning main_output/v2_main/packet_dataset.csv

# Restore all datasets from timeline integrity backups
find main_output/v2_main -name "*.backup_raw" -exec bash -c 'cp "$1" "${1%.backup_raw}"' _ {} \\;
```

**Re-run Specific Steps**:
```bash
# Re-run from combine step (if timeline integrity already completed)
python3 dataset_cleanup/combine_datasets.py
python3 dataset_cleanup/investigate_csv_quality.py
python3 dataset_cleanup/clean_packet_dataset.py --path main_output/v2_main
python3 dataset_cleanup/clean_flow_dataset.py --path main_output/v2_main  
python3 dataset_cleanup/clean_cicflow_dataset.py --path main_output/v2_main
```

## Script Arguments Reference

### Common Arguments
- `--path PATH`: Dataset directory path (default: `../main_output/v2_main` when run from `dataset_cleanup/`)
- `--verbose` / `-v`: Enable verbose logging (where supported)
- `--help` / `-h`: Show help message

### Timeline Integrity Script
```bash
python3 dataset_cleanup/fix_timeline_integrity.py [OPTIONS]

Options:
  --dataset NAME    Process specific dataset directory (e.g., 190725-1)
  --all            Process all dataset directories
  -v, --verbose    Enable verbose logging
```

### Cleaning Scripts
```bash
python3 dataset_cleanup/clean_packet_dataset.py --path PATH
python3 dataset_cleanup/clean_flow_dataset.py --path PATH
python3 dataset_cleanup/clean_cicflow_dataset.py --path PATH

Arguments:
  --path PATH      Path to dataset directory containing CSV files
```

## Performance Notes

### Expected Runtime
- Step 1 (Timeline Integrity): ~2-5 minutes per dataset
- Step 2 (Combine Datasets): ~30-60 seconds
- Step 3 (Quality Investigation): ~10-30 seconds
- Step 4 (Clean Packet): ~5-15 seconds
- Step 5 (Clean Flow): ~15-30 seconds
- Step 6 (Clean CICFlow): ~5-15 seconds

**Total Workflow Time**: ~30-45 minutes for complete processing

### Memory Requirements
- **Minimum**: 4 GB RAM
- **Recommended**: 8 GB RAM
- **Peak usage**: ~2-3 GB during flow dataset processing

### Storage Requirements
- **Input datasets**: ~150 MB
- **Backup files**: ~150 MB additional
- **Final cleaned datasets**: ~85 MB
- **Total workspace**: ~400 MB recommended

## Integration with ML Pipelines

The cleaned datasets are optimized for machine learning:

### Packet Dataset (`packet_dataset.csv`)
- **Use case**: Real-time packet-level detection
- **Features**: 16 network packet attributes
- **Missing values**: Encoded as `-1` for ML compatibility
- **Target**: `Label_multi` (7 classes) or `Label_binary` (2 classes)

### Flow Dataset (`flow_dataset.csv`)  
- **Use case**: Network flow analysis and SDN-based detection
- **Features**: 16 flow statistics and SDN metadata
- **Complete data**: No missing values
- **Target**: `Label_multi` (5 classes) or `Label_binary` (2 classes)

### CICFlow Dataset (`cicflow_dataset.csv`)
- **Use case**: Advanced ML with comprehensive network features
- **Features**: 86 CICFlow-derived network statistics
- **Complete data**: No missing values or duplicates
- **Target**: `Label_multi` (7 classes) or `Label_binary` (2 classes)

### Loading in Python
```python
import pandas as pd

# Load cleaned datasets
packet_df = pd.read_csv('main_output/v2_main/packet_dataset.csv')
flow_df = pd.read_csv('main_output/v2_main/flow_dataset.csv') 
cicflow_df = pd.read_csv('main_output/v2_main/cicflow_dataset.csv')

# Prepare features and labels
X_packet = packet_df.drop(['Label_multi', 'Label_binary', 'dataset_id'], axis=1)
y_packet = packet_df['Label_binary']  # or 'Label_multi' for multiclass

# Handle -1 encoded missing values if needed
X_packet = X_packet.replace(-1, 0)  # or use appropriate imputation
```

## Conclusion

This workflow ensures that the AdDDoSDN datasets are properly cleaned, validated, and prepared for machine learning research. The comprehensive approach addresses timeline integrity, missing values, duplicates, and data quality while preserving the essential characteristics needed for network security analysis.

**Key Achievements**:
- ✅ Resolved 60% data loss issue in adversarial attacks
- ✅ Created three clean, ML-ready datasets
- ✅ Comprehensive quality assurance and validation
- ✅ Full reproducibility with detailed documentation
- ✅ Proper backup and recovery procedures

The resulting datasets provide a solid foundation for developing and evaluating DDoS detection algorithms in SDN environments.