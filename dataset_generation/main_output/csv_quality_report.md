# CSV Data Quality Investigation Report
Generated on: 2025-07-18 13:13:13

## Summary Statistics
- **Total CSV files analyzed**: 12
- **Successfully processed**: 12 (100.0%)
- **Total data rows**: 2,912,850
- **Total file size**: 377.63 MB
- **Total missing values**: 8,583,906
- **Total infinity values**: 0
- **Total duplicate rows**: 1,971

## CSV Type Breakdown
### packet_features.csv
- Files: 4
- Total rows: 178,473
- Total size: 14.00 MB
- Average columns: 15.0

### flow_features.csv
- Files: 4
- Total rows: 2,700,131
- Total size: 349.93 MB
- Average columns: 18.0

### cicflow_features_all.csv
- Files: 4
- Total rows: 34,246
- Total size: 13.70 MB
- Average columns: 85.0

## Dataset-Specific Analysis
### Dataset: 1607-1
#### packet_features.csv
- **Rows**: 44,597
- **Columns**: 15
- **File size**: 3.5 MB
- **Memory usage**: 16.25 MB
- **Issues**: Missing values: 55,560 (8.31%), Duplicates: 148 (0.33%)
- **Columns with missing values**:
  - ip_flags: 27092 (60.75%)
  - src_port: 8316 (18.65%)
  - dst_port: 8316 (18.65%)
  - tcp_flags: 11836 (26.54%)

#### flow_features.csv
- **Rows**: 674,777
- **Columns**: 18
- **File size**: 87.46 MB
- **Memory usage**: 224.75 MB
- **Issues**: Missing values: 2,089,632 (17.2%)
- **Columns with missing values**:
  - table_id: 674777 (100.0%)
  - cookie: 674777 (100.0%)
  - in_port: 21767 (3.23%)
  - eth_src: 21767 (3.23%)
  - eth_dst: 21767 (3.23%)
  - duration_nsec: 674777 (100.0%)

#### cicflow_features_all.csv
- **Rows**: 8,564
- **Columns**: 85
- **File size**: 3.42 MB
- **Memory usage**: 7.16 MB
- **Issues**: Duplicates: 321 (3.75%)

### Dataset: 1607-2
#### packet_features.csv
- **Rows**: 44,720
- **Columns**: 15
- **File size**: 3.51 MB
- **Memory usage**: 16.29 MB
- **Issues**: Missing values: 55,762 (8.31%), Duplicates: 371 (0.83%)
- **Columns with missing values**:
  - ip_flags: 27116 (60.64%)
  - src_port: 8378 (18.73%)
  - dst_port: 8378 (18.73%)
  - tcp_flags: 11890 (26.59%)

#### flow_features.csv
- **Rows**: 675,459
- **Columns**: 18
- **File size**: 87.5 MB
- **Memory usage**: 224.98 MB
- **Issues**: Missing values: 2,091,744 (17.2%)
- **Columns with missing values**:
  - table_id: 675459 (100.0%)
  - cookie: 675459 (100.0%)
  - in_port: 21789 (3.23%)
  - eth_src: 21789 (3.23%)
  - eth_dst: 21789 (3.23%)
  - duration_nsec: 675459 (100.0%)

#### cicflow_features_all.csv
- **Rows**: 8,572
- **Columns**: 85
- **File size**: 3.43 MB
- **Memory usage**: 7.17 MB
- **Issues**: Duplicates: 281 (3.28%)

### Dataset: 1707-1
#### packet_features.csv
- **Rows**: 44,752
- **Columns**: 15
- **File size**: 3.51 MB
- **Memory usage**: 16.3 MB
- **Issues**: Missing values: 55,691 (8.3%), Duplicates: 140 (0.31%)
- **Columns with missing values**:
  - ip_flags: 27181 (60.74%)
  - src_port: 8336 (18.63%)
  - dst_port: 8336 (18.63%)
  - tcp_flags: 11838 (26.45%)

#### flow_features.csv
- **Rows**: 676,110
- **Columns**: 18
- **File size**: 87.64 MB
- **Memory usage**: 225.19 MB
- **Issues**: Missing values: 2,093,760 (17.2%)
- **Columns with missing values**:
  - table_id: 676110 (100.0%)
  - cookie: 676110 (100.0%)
  - in_port: 21810 (3.23%)
  - eth_src: 21810 (3.23%)
  - eth_dst: 21810 (3.23%)
  - duration_nsec: 676110 (100.0%)

#### cicflow_features_all.csv
- **Rows**: 8,664
- **Columns**: 85
- **File size**: 3.46 MB
- **Memory usage**: 7.25 MB
- **Issues**: Duplicates: 334 (3.86%)

### Dataset: 1707-2
#### packet_features.csv
- **Rows**: 44,404
- **Columns**: 15
- **File size**: 3.48 MB
- **Memory usage**: 16.18 MB
- **Issues**: Missing values: 55,197 (8.29%), Duplicates: 81 (0.18%)
- **Columns with missing values**:
  - ip_flags: 26897 (60.57%)
  - src_port: 8260 (18.6%)
  - dst_port: 8260 (18.6%)
  - tcp_flags: 11780 (26.53%)

#### flow_features.csv
- **Rows**: 673,785
- **Columns**: 18
- **File size**: 87.33 MB
- **Memory usage**: 224.42 MB
- **Issues**: Missing values: 2,086,560 (17.2%)
- **Columns with missing values**:
  - table_id: 673785 (100.0%)
  - cookie: 673785 (100.0%)
  - in_port: 21735 (3.23%)
  - eth_src: 21735 (3.23%)
  - eth_dst: 21735 (3.23%)
  - duration_nsec: 673785 (100.0%)

#### cicflow_features_all.csv
- **Rows**: 8,446
- **Columns**: 85
- **File size**: 3.39 MB
- **Memory usage**: 7.07 MB
- **Issues**: Duplicates: 295 (3.49%)

## Data Preprocessing Recommendations
### Issues Found:
1. **Missing Values**: Consider imputation strategies:
   - Numerical columns: Mean/median imputation or forward fill
   - Categorical columns: Mode imputation or 'unknown' category
   - Time series: Forward fill or interpolation

3. **Duplicate Rows**: Address duplicates:
   - Review if duplicates are legitimate (e.g., identical packets)
   - Consider keeping first occurrence or aggregating
   - Analyze impact on temporal sequences

### General Recommendations:
1. **Data Validation**: Implement automated data quality checks
2. **Feature Engineering**: Consider creating derived features from timestamps
3. **Normalization**: Apply scaling to numerical features for ML models
4. **Temporal Integrity**: Verify timestamp ordering and gaps
5. **Label Consistency**: Ensure consistent labeling across all datasets