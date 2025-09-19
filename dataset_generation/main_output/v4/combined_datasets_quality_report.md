# Combined Datasets Quality Investigation Report
Generated on: 2025-09-19 12:03:35

## Executive Summary
- **Data Integrity Score**: 100.0/100 (EXCELLENT ✅)
- **Files Processed**: 3/3 (100.0%)
- **Total Records**: 3,514,603
- **Total Size**: 530.4 MB
- **Dataset ID Consistency**: ✅ Consistent

## Quick Quality Check
### Issues Detected:
- ⚠️ Missing values: 24,014,779

## Dataset-Specific Analysis
### PACKET Dataset
- **File**: ../main_output/v4/packet_dataset.csv
- **Size**: 229.2 MB
- **Records**: 1,685,938
- **Features**: 33 columns
- **Memory Usage**: 982.6 MB
- **Source Datasets**: 95 datasets
- **Records per Dataset**: 3,919 - 34,743 (avg: 17,747)
- **Distribution**: ⚠️ Imbalanced (ratio: 8.87)
- **Quality Issues**: Missing: 17,775,667 (31.95%)
#### 🔍 Detailed Missing Values Analysis
| Column | Missing Count | % Missing | Data Type | Pattern |
|--------|---------------|-----------|-----------|---------|
| udp_sport | 1,486,855 | 88.19% | float64 | scattered |
| udp_dport | 1,486,855 | 88.19% | float64 | scattered |
| udp_len | 1,486,855 | 88.19% | float64 | scattered |
| udp_checksum | 1,486,855 | 88.19% | float64 | scattered |
| icmp_id | 1,448,369 | 85.91% | float64 | scattered |
| icmp_seq | 1,448,369 | 85.91% | float64 | scattered |
| icmp_type | 1,413,193 | 83.82% | float64 | scattered |
| icmp_code | 1,413,193 | 83.82% | float64 | scattered |
| eth_type | 1,413,191 | 83.82% | object | scattered |
| ip_flags | 917,308 | 54.41% | object | scattered |
| src_port | 471,828 | 27.99% | float64 | scattered |
| dst_port | 471,828 | 27.99% | float64 | scattered |
| tcp_flags | 471,828 | 27.99% | object | scattered |
| tcp_seq | 471,828 | 27.99% | float64 | scattered |
| tcp_ack | 471,828 | 27.99% | float64 | scattered |
| tcp_window | 471,828 | 27.99% | float64 | scattered |
| tcp_urgent | 471,828 | 27.99% | float64 | scattered |
| tcp_options_len | 471,828 | 27.99% | float64 | scattered |
#### 📊 Detailed Statistics for Problematic Columns
**ip_id** (int64):
- Total: 1,685,938, Finite: 1,685,938, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 6.55e+04
- Mean: 8.91e+03, Median: 1.00e+00, Std: 1.76e+04
- Zeros: 494,397, Negatives: 0
- Outliers (IQR): 359,008 (21.3%)
- Outlier fences: -8.55e+03 to 1.42e+04
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=5.34e+04, P99=6.33e+04

**ip_len** (int64):
- Total: 1,685,938, Finite: 1,685,938, Missing: 0, Infinity: 0
- Range: 2.80e+01 to 1.46e+04
- Mean: 1.52e+02, Median: 4.00e+01, Std: 3.42e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 272,451 (16.2%)
- Outlier fences: 1.00e+00 to 1.05e+02
- Percentiles: P1=2.80e+01, P5=4.00e+01, P95=8.14e+02, P99=1.38e+03

**src_port** (float64):
- Total: 1,685,938, Finite: 1,214,110, Missing: 471,828, Infinity: 0
- Range: 2.10e+01 to 6.55e+04
- Mean: 2.19e+04, Median: 1.06e+04, Std: 2.35e+04
- Zeros: 0, Negatives: 0
- Percentiles: P1=2.10e+01, P5=2.20e+01, P95=6.01e+04, P99=6.43e+04

**dst_port** (float64):
- Total: 1,685,938, Finite: 1,214,110, Missing: 471,828, Infinity: 0
- Range: 2.10e+01 to 6.55e+04
- Mean: 2.06e+04, Median: 8.08e+03, Std: 2.32e+04
- Zeros: 0, Negatives: 0
- Percentiles: P1=2.10e+01, P5=2.20e+01, P95=5.97e+04, P99=6.42e+04

**tcp_seq** (float64):
- Total: 1,685,938, Finite: 1,214,110, Missing: 471,828, Infinity: 0
- Range: 0.00e+00 to 4.29e+09
- Mean: 7.18e+08, Median: 5.59e+04, Std: 1.24e+09
- Zeros: 234,048, Negatives: 0
- Outliers (IQR): 148,566 (8.8%)
- Outlier fences: -1.63e+09 to 2.71e+09
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=3.66e+09, P99=4.17e+09

**tcp_ack** (float64):
- Total: 1,685,938, Finite: 1,214,110, Missing: 471,828, Infinity: 0
- Range: 0.00e+00 to 4.29e+09
- Mean: 6.49e+08, Median: 2.94e+04, Std: 1.20e+09
- Zeros: 498,178, Negatives: 0
- Outliers (IQR): 208,967 (12.4%)
- Outlier fences: -1.11e+09 to 1.84e+09
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=3.60e+09, P99=4.15e+09

**tcp_window** (float64):
- Total: 1,685,938, Finite: 1,214,110, Missing: 471,828, Infinity: 0
- Range: 0.00e+00 to 6.55e+04
- Mean: 7.39e+03, Median: 8.50e+01, Std: 1.28e+04
- Zeros: 442,177, Negatives: 0
- Outliers (IQR): 127,571 (7.6%)
- Outlier fences: -1.23e+04 to 2.05e+04
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=4.23e+04, P99=6.42e+04

**tcp_urgent** (float64):
- Total: 1,685,938, Finite: 1,214,110, Missing: 471,828, Infinity: 0
- Range: 0.00e+00 to 0.00e+00
- Mean: 0.00e+00, Median: 0.00e+00, Std: 0.00e+00
- Zeros: 1,214,110, Negatives: 0
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=0.00e+00, P99=0.00e+00

**udp_sport** (float64):
- Total: 1,685,938, Finite: 199,083, Missing: 1,486,855, Infinity: 0
- Range: 5.30e+01 to 6.55e+04
- Mean: 4.74e+04, Median: 4.83e+04, Std: 1.21e+04
- Zeros: 0, Negatives: 0
- Outliers (IQR): 4,845 (0.3%)
- Outlier fences: 1.41e+04 to 8.25e+04
- Percentiles: P1=3.27e+03, P5=3.28e+04, P95=6.38e+04, P99=6.52e+04

**udp_dport** (float64):
- Total: 1,685,938, Finite: 199,083, Missing: 1,486,855, Infinity: 0
- Range: 5.30e+01 to 6.10e+04
- Mean: 7.83e+02, Median: 5.30e+01, Std: 4.06e+03
- Zeros: 0, Negatives: 0
- Percentiles: P1=5.30e+01, P5=5.30e+01, P95=5.30e+01, P99=1.23e+04

#### 🏷️ Label Distribution Analysis
**Label_multi**: 7 classes, 1,685,938 records
- normal: 559,346 (33.2%)
- ad_udp: 255,615 (15.2%)
- ad_syn: 243,420 (14.4%)
- icmp_flood: 205,324 (12.2%)
- udp_flood: 200,196 (11.9%)
- syn_flood: 182,871 (10.8%)
- ad_slow: 39,166 (2.3%)

**Label_binary**: 2 classes, 1,685,938 records
- 1: 1,126,592 (66.8%)
- 0: 559,346 (33.2%)

- **Performance**: Medium loading, Memory efficiency: 4.3

### FLOW Dataset
- **File**: ../main_output/v4/flow_dataset.csv
- **Size**: 183.2 MB
- **Records**: 1,559,778
- **Features**: 19 columns
- **Memory Usage**: 370.7 MB
- **Source Datasets**: 95 datasets
- **Records per Dataset**: 4,023 - 30,322 (avg: 16,419)
- **Distribution**: ⚠️ Imbalanced (ratio: 7.54)
- **Quality Issues**: Missing: 6,239,112 (21.05%)
#### 🔍 Detailed Missing Values Analysis
| Column | Missing Count | % Missing | Data Type | Pattern |
|--------|---------------|-----------|-----------|---------|
| in_port | 1,559,778 | 100.00% | float64 | mostly_missing |
| eth_src | 1,559,778 | 100.00% | float64 | mostly_missing |
| eth_dst | 1,559,778 | 100.00% | float64 | mostly_missing |
| out_port | 1,559,778 | 100.00% | float64 | mostly_missing |
#### 📊 Detailed Statistics for Problematic Columns
**in_port** (float64):
- Total: 1,559,778, Finite: 0, Missing: 1,559,778, Infinity: 0

**eth_src** (float64):
- Total: 1,559,778, Finite: 0, Missing: 1,559,778, Infinity: 0

**eth_dst** (float64):
- Total: 1,559,778, Finite: 0, Missing: 1,559,778, Infinity: 0

**out_port** (float64):
- Total: 1,559,778, Finite: 0, Missing: 1,559,778, Infinity: 0

**packet_count** (int64):
- Total: 1,559,778, Finite: 1,559,778, Missing: 0, Infinity: 0
- Range: 9.00e+00 to 5.88e+03
- Mean: 9.96e+02, Median: 1.67e+02, Std: 1.43e+03
- Zeros: 0, Negatives: 0
- Outliers (IQR): 80,448 (5.2%)
- Outlier fences: -2.58e+03 to 4.33e+03
- Percentiles: P1=9.00e+00, P5=9.00e+00, P95=4.41e+03, P99=5.70e+03

**byte_count** (int64):
- Total: 1,559,778, Finite: 1,559,778, Missing: 0, Infinity: 0
- Range: 8.82e+02 to 6.78e+05
- Mean: 9.08e+04, Median: 1.64e+04, Std: 1.38e+05
- Zeros: 0, Negatives: 0
- Outliers (IQR): 124,935 (8.0%)
- Outlier fences: -2.14e+05 to 3.58e+05
- Percentiles: P1=8.82e+02, P5=8.82e+02, P95=4.57e+05, P99=5.22e+05

**avg_pkt_size** (float64):
- Total: 1,559,778, Finite: 1,559,778, Missing: 0, Infinity: 0
- Range: 4.25e+01 to 5.58e+02
- Mean: 1.02e+02, Median: 9.80e+01, Std: 5.50e+01
- Zeros: 0, Negatives: 0
- Outliers (IQR): 244,030 (15.6%)
- Outlier fences: 2.77e+01 to 1.40e+02
- Percentiles: P1=4.26e+01, P5=4.29e+01, P95=1.92e+02, P99=3.90e+02

#### 🏷️ Label Distribution Analysis
**Label_multi**: 7 classes, 1,559,778 records
- normal: 1,160,015 (74.4%)
- udp_flood: 131,215 (8.4%)
- icmp_flood: 69,636 (4.5%)
- syn_flood: 68,159 (4.4%)
- ad_syn: 55,167 (3.5%)
- ad_slow: 53,963 (3.5%)
- ad_udp: 21,623 (1.4%)

**Label_binary**: 2 classes, 1,559,778 records
- 0: 1,160,015 (74.4%)
- 1: 399,763 (25.6%)

- **Performance**: Medium loading, Memory efficiency: 2.0

### CICFLOW Dataset
- **File**: ../main_output/v4/cicflow_dataset.csv
- **Size**: 118.0 MB
- **Records**: 268,887
- **Features**: 86 columns
- **Memory Usage**: 257.2 MB
- **Source Datasets**: 95 datasets
- **Records per Dataset**: 604 - 5,562 (avg: 2,830)
- **Distribution**: ⚠️ Imbalanced (ratio: 9.21)
- **Quality Issues**: None detected ✅
#### 📊 Detailed Statistics for Problematic Columns
**src_port** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: -1.00e+00 to 6.55e+04
- Mean: 4.22e+04, Median: 4.60e+04, Std: 1.83e+04
- Zeros: 0, Negatives: 25,336
- Outliers (IQR): 30,508 (11.3%)
- Outlier fences: 7.38e+03 to 8.45e+04
- Percentiles: P1=-1.00e+00, P5=-1.00e+00, P95=6.34e+04, P99=6.51e+04

**dst_port** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: -1.00e+00 to 6.06e+04
- Mean: 1.09e+03, Median: 5.30e+01, Std: 2.98e+03
- Zeros: 0, Negatives: 25,336
- Outliers (IQR): 69,818 (26.0%)
- Outlier fences: 1.25e+01 to 1.20e+02
- Percentiles: P1=-1.00e+00, P5=-1.00e+00, P95=8.44e+03, P99=1.23e+04

**flow_duration** (float64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.83e+02
- Mean: 1.55e+00, Median: 2.10e-05, Std: 1.11e+01
- Zeros: 549, Negatives: 0
- Outliers (IQR): 63,855 (23.7%)
- Outlier fences: -2.65e-05 to 7.35e-05
- Percentiles: P1=8.00e-06, P5=9.00e-06, P95=2.53e+00, P99=6.12e+01

**tot_bwd_pkts** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 8.03e+02
- Mean: 2.76e+00, Median: 2.00e+00, Std: 8.40e+00
- Zeros: 106,906, Negatives: 0
- Outliers (IQR): 54,292 (20.2%)
- Outlier fences: -3.00e+00 to 5.00e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=1.00e+01, P99=1.40e+01

**totlen_fwd_pkts** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 1.12e+02 to 3.88e+04
- Mean: 6.76e+02, Median: 2.40e+02, Std: 1.25e+03
- Zeros: 0, Negatives: 0
- Outliers (IQR): 57,611 (21.4%)
- Outlier fences: -3.45e+01 to 5.06e+02
- Percentiles: P1=1.68e+02, P5=1.68e+02, P95=3.04e+03, P99=6.46e+03

**totlen_bwd_pkts** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.98e+06
- Mean: 5.00e+02, Median: 1.12e+02, Std: 5.39e+03
- Zeros: 106,906, Negatives: 0
- Outliers (IQR): 55,194 (20.5%)
- Outlier fences: -1.80e+02 to 3.00e+02
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=2.36e+03, P99=7.25e+03

**fwd_pkt_len_max** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 5.07e+03
- Mean: 2.22e+02, Median: 7.90e+01, Std: 4.47e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 53,186 (19.8%)
- Outlier fences: -1.00e+01 to 1.66e+02
- Percentiles: P1=5.60e+01, P5=5.60e+01, P95=1.08e+03, P99=1.80e+03

**fwd_pkt_len_min** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.20e+02, Median: 7.30e+01, Std: 2.11e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 19,008 (7.1%)
- Outlier fences: 1.55e+01 to 1.24e+02
- Percentiles: P1=5.60e+01, P5=5.60e+01, P95=4.95e+02, P99=1.27e+03

**fwd_pkt_len_mean** (float64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.39e+02, Median: 7.90e+01, Std: 2.17e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 36,359 (13.5%)
- Outlier fences: -7.46e+00 to 1.62e+02
- Percentiles: P1=5.60e+01, P5=5.60e+01, P95=5.91e+02, P99=1.27e+03

**bwd_pkt_len_max** (int64):
- Total: 268,887, Finite: 268,887, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.47e+04
- Mean: 1.06e+02, Median: 5.60e+01, Std: 2.69e+02
- Zeros: 106,906, Negatives: 0
- Outliers (IQR): 28,326 (10.5%)
- Outlier fences: -8.40e+01 to 1.40e+02
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=5.65e+02, P99=1.27e+03

#### 🏷️ Label Distribution Analysis
**Label_multi**: 7 classes, 268,887 records
- udp_flood: 88,699 (33.0%)
- ad_syn: 62,188 (23.1%)
- syn_flood: 45,186 (16.8%)
- normal: 44,201 (16.4%)
- icmp_flood: 16,028 (6.0%)
- ad_udp: 10,618 (3.9%)
- ad_slow: 1,967 (0.7%)

**Label_binary**: 2 classes, 268,887 records
- 1: 224,686 (83.6%)
- 0: 44,201 (16.4%)

- **Performance**: Medium loading, Memory efficiency: 2.2

## Cross-Dataset Consistency
✅ **All datasets contain the same source dataset IDs**
- Common dataset IDs: 120925-1, 120925-10, 120925-11, 120925-12, 120925-13, 120925-14, 120925-15, 120925-16, 120925-17, 120925-18, 120925-19, 120925-2, 120925-20, 120925-21, 120925-22, 120925-23, 120925-24, 120925-25, 120925-26, 120925-27, 120925-28, 120925-29, 120925-3, 120925-30, 120925-31, 120925-32, 120925-33, 120925-34, 120925-35, 120925-36, 120925-37, 120925-38, 120925-39, 120925-4, 120925-40, 120925-41, 120925-42, 120925-43, 120925-44, 120925-45, 120925-46, 120925-47, 120925-48, 120925-49, 120925-5, 120925-50, 120925-51, 120925-52, 120925-53, 120925-54, 120925-55, 120925-6, 120925-7, 120925-8, 120925-9, 130925-1, 130925-10, 130925-11, 130925-12, 130925-13, 130925-14, 130925-15, 130925-16, 130925-17, 130925-18, 130925-19, 130925-2, 130925-20, 130925-3, 130925-4, 130925-5, 130925-6, 130925-7, 130925-8, 130925-9, 180925-1, 180925-10, 180925-11, 180925-12, 180925-13, 180925-14, 180925-15, 180925-16, 180925-17, 180925-18, 180925-19, 180925-2, 180925-20, 180925-3, 180925-4, 180925-5, 180925-6, 180925-7, 180925-8, 180925-9

## 🧹 Detailed Data Cleaning Recommendations
### Missing Values Treatment
#### PACKET Dataset:
- **udp_sport** (88.2% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **udp_dport** (88.2% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **udp_len** (88.2% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **udp_checksum** (88.2% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **icmp_id** (85.9% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **icmp_seq** (85.9% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **icmp_type** (83.8% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **icmp_code** (83.8% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **eth_type** (83.8% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **ip_flags** (54.4% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **src_port** (28.0% missing): Use median/mean imputation or advanced techniques
- **dst_port** (28.0% missing): Use median/mean imputation or advanced techniques
- **tcp_flags** (28.0% missing): Use mode imputation or 'unknown' category
- **tcp_seq** (28.0% missing): Use median/mean imputation or advanced techniques
- **tcp_ack** (28.0% missing): Use median/mean imputation or advanced techniques
- **tcp_window** (28.0% missing): Use median/mean imputation or advanced techniques
- **tcp_urgent** (28.0% missing): Use median/mean imputation or advanced techniques
- **tcp_options_len** (28.0% missing): Use median/mean imputation or advanced techniques
#### FLOW Dataset:
- **in_port** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation
- **eth_src** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation
- **eth_dst** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation
- **out_port** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation

### Outlier Treatment
#### PACKET Dataset:
- **ip_id** (21.3% outliers, 17.6% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-8.55e+03, 1.42e+04]
- **ip_len** (16.2% outliers, 15.3% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.00e+00, 1.05e+02]
- **tcp_seq** (8.8% outliers, 0.0% extreme):
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [-1.63e+09, 2.71e+09]
- **tcp_ack** (12.4% outliers, 6.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-1.11e+09, 1.84e+09]
- **tcp_window** (7.6% outliers, 4.6% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [-1.23e+04, 2.05e+04]
#### FLOW Dataset:
- **packet_count** (5.2% outliers, 0.0% extreme):
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [-2.58e+03, 4.33e+03]
- **byte_count** (8.0% outliers, 0.4% extreme):
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [-2.14e+05, 3.58e+05]
- **avg_pkt_size** (15.6% outliers, 13.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [2.77e+01, 1.40e+02]
#### CICFLOW Dataset:
- **src_port** (11.3% outliers, 0.0% extreme):
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [7.38e+03, 8.45e+04]
- **dst_port** (26.0% outliers, 16.5% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.25e+01, 1.20e+02]
- **flow_duration** (23.7% outliers, 23.7% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-2.65e-05, 7.35e-05]
- **tot_bwd_pkts** (20.2% outliers, 10.9% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-3.00e+00, 5.00e+00]
- **totlen_fwd_pkts** (21.4% outliers, 20.9% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-3.45e+01, 5.06e+02]

### Dataset-Specific Cleaning Strategies
#### PACKET Dataset Cleaning Plan:
   3. **Impute missing**: Apply appropriate imputation for 17,775,667 missing values
   4. **Packet-specific**: Validate timestamp sequences and packet ordering
   5. **Network validation**: Check for impossible protocol combinations
   6. **Normalization**: Apply appropriate scaling based on outlier analysis
   7. **Validation**: Cross-check cleaned data maintains attack patterns

#### FLOW Dataset Cleaning Plan:
   3. **Impute missing**: Apply appropriate imputation for 6,239,112 missing values
   4. **Flow-specific**: Consider time-based interpolation for flow statistics
   5. **Feature engineering**: Create flow duration and rate features from existing data
   6. **Normalization**: Apply appropriate scaling based on outlier analysis
   7. **Validation**: Cross-check cleaned data maintains attack patterns

#### CICFLOW Dataset Cleaning Plan:
   4. **CICFlow-specific**: Many features are derived - verify calculation consistency
   5. **Feature selection**: Consider removing highly correlated CICFlow features
   6. **Normalization**: Apply appropriate scaling based on outlier analysis
   7. **Validation**: Cross-check cleaned data maintains attack patterns

### 🐍 Python Code Templates for Data Cleaning
#### Missing Values Imputation
```python
import pandas as pd
from sklearn.impute import SimpleImputer, IterativeImputer

# For columns with <20% missing - simple imputation
numeric_imputer = SimpleImputer(strategy='median')
categorical_imputer = SimpleImputer(strategy='most_frequent')

# For columns with 20-50% missing - advanced imputation
advanced_imputer = IterativeImputer(random_state=42)

# For columns with >50% missing - consider dropping
high_missing_cols = df.isnull().sum()[df.isnull().sum() > len(df) * 0.5].index
df_cleaned = df.drop(columns=high_missing_cols)
```

#### Infinity Values Replacement
```python
import numpy as np

def replace_infinity(df, strategy='percentile'):
    df_clean = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        if np.isinf(df[col]).any():
            if strategy == 'percentile':
                finite_vals = df[col][np.isfinite(df[col])]
                p99 = finite_vals.quantile(0.99)
                p1 = finite_vals.quantile(0.01)
                df_clean[col] = df[col].replace([np.inf, -np.inf], [p99, p1])
            elif strategy == 'nan':
                df_clean[col] = df[col].replace([np.inf, -np.inf], np.nan)
    return df_clean
```

#### Outlier Treatment
```python
def cap_outliers_iqr(df, multiplier=1.5):
    df_clean = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        df_clean[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
    return df_clean
```

## General ML Preparation Recommendations
### ✅ Excellent Data Quality
- Data is ready for ML training with minimal preprocessing
- Focus on feature engineering and normalization
- Implement automated quality monitoring

### ML Pipeline Steps:
1. **Data Cleaning**: Apply strategies above based on column-specific analysis
2. **Feature Engineering**: Create temporal and behavioral features from network data
3. **Data Splitting**: Use dataset_id for temporal/cross-dataset validation
4. **Preprocessing**: Apply scaling after cleaning to avoid leakage
5. **Validation**: Ensure attack patterns remain detectable after preprocessing
6. **Monitoring**: Implement drift detection for production deployment