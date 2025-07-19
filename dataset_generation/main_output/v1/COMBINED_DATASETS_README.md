# Combined Datasets Summary

This directory contains three consolidated datasets created by combining all individual dataset directories (1607-1, 1607-2, 1707-1, 1707-2, 1807-1, 1907-1) into unified CSV files.

## Dataset Files

### 1. packet_dataset.csv
- **Description**: Combined packet-level data from all 6 datasets (fully cleaned)
- **Size**: 22.5 MB (266,986 records + header)  
- **Features**: 16 columns (15 original + dataset_id)
- **Source**: All `packet_features.csv` files combined
- **Cleaning**: 865 duplicates removed + 330,599 missing values encoded as -1
- **ML Ready**: Zero missing values, all protocol-appropriate -1 encoding
- **Records per dataset**:
  - 1607-1: 44,597 records
  - 1607-2: 44,720 records
  - 1707-1: 44,752 records
  - 1707-2: 44,404 records
  - 1807-1: 44,831 records
  - 1907-1: 44,547 records

### 2. flow_dataset.csv
- **Description**: Combined SDN flow data from all 6 datasets (missing values cleaned)
- **Size**: 516 MB (3,681,215 records + header)
- **Features**: 16 columns (15 original + dataset_id)
- **Source**: All `flow_features.csv` files combined
- **Cleaning**: 3 empty columns dropped + 372,469 rows with missing network metadata removed (9.2% reduction)
- **ML Optimization**: Removed unusable records lacking critical network features (in_port, eth_src, eth_dst)
- **Records per dataset**:
  - 1607-1: 674,777 records
  - 1607-2: 675,459 records
  - 1707-1: 676,110 records
  - 1707-2: 673,785 records
  - 1807-1: 677,660 records
  - 1907-1: 675,893 records

### 3. cicflow_dataset.csv
- **Description**: Combined CICFlow aggregated data from all 6 datasets (duplicates removed)
- **Size**: 20 MB (49,651 records + header)
- **Features**: 86 columns (85 original + dataset_id)
- **Source**: All `cicflow_features_all.csv` files combined
- **Cleaning**: 1,776 duplicate rows removed (3.45% reduction)
- **Records per dataset**:
  - 1607-1: 8,564 records
  - 1607-2: 8,572 records
  - 1707-1: 8,664 records
  - 1707-2: 8,446 records
  - 1807-1: 8,634 records
  - 1907-1: 8,547 records

## Dataset Structure

Each combined dataset includes:
- **dataset_id**: First column identifying the source dataset (1607-1, 1607-2, etc.)
- **All original features**: Preserved from individual dataset files
- **Consistent ordering**: Records maintain chronological order within each dataset

## Usage Notes

### Data Format
- All datasets are in CSV format with headers
- The `dataset_id` column allows tracking the source of each record
- No data transformation was performed - original values preserved

### Quality Assurance
- **Total Records**: 3,997,852 across all three formats (after comprehensive cleaning)
- **Data Integrity**: All original data preserved with source tracking and comprehensive cleaning
- **Timeline Consistency**: Attack phases and labeling maintained across datasets
- **No Missing Data**: Zero missing values across all datasets (FLOW rows removed, PACKET -1 encoded)
- **ML Ready**: All datasets optimized for machine learning with proper encoding
- **Data Cleaning**: 2,641 duplicates + 372,469 FLOW rows + 330,599 PACKET missing values processed

### Attack Distribution
The combined datasets span 4 days (July 16-19, 2025) with:
- **7 Attack Types**: normal, syn_flood, udp_flood, icmp_flood, ad_syn, ad_udp, ad_slow
- **Multi-Granularity**: Packet-level, SDN flow-level, and CICFlow aggregated data
- **Temporal Diversity**: Different time patterns across multiple days

## ML Training Applications

### Recommended Usage
1. **Cross-Dataset Validation**: Use `dataset_id` for train/test splits across different days
2. **Temporal Analysis**: Leverage multi-day data for time-series and circadian pattern analysis
3. **Multi-Format Learning**: Train models on different granularities of the same underlying data
4. **Attack Detection**: Use balanced attack distribution across traditional and adversarial scenarios

### Performance Characteristics
- **Packet Dataset**: Suitable for real-time packet classification
- **Flow Dataset**: Ideal for SDN controller-based detection systems
- **CICFlow Dataset**: Optimized for flow-based behavioral analysis

## File Generation Details

- **Created**: July 19, 2025
- **Generation Tool**: `combine_datasets.py`
- **Cleaning Tool**: `remove_duplicates.py`
- **Source Datasets**: 6 complete datasets with timeline integrity
- **Processing Success**: 100% (18/18 source CSV files successfully combined)
- **Data Preservation**: Conservative approach with full audit trail
- **Duplicate Removal**: 2,641 exact duplicates removed with backup preservation

## Related Files

- `analysis.md`: Comprehensive analysis of all datasets and framework
- Individual dataset directories (1607-1 through 1907-1): Original source data
- `combine_datasets.log`: Complete processing log with detailed statistics
- `remove_duplicates.log`: Duplicate removal processing log
- `clean_flow_missing.log`: Missing values cleaning log for FLOW dataset
- `*.backup_duplicates`: Original files before duplicate removal
- `*.backup_missing`: Original files before missing value cleaning

---

*Combined datasets ready for immediate use in DDoS detection research and ML model development*