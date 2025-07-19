# Combined Datasets Quality Investigation Report
Generated on: 2025-07-19 12:19:39

## Executive Summary
- **Data Integrity Score**: 100.0/100 (EXCELLENT ✅)
- **Files Processed**: 3/3 (100.0%)
- **Total Records**: 3,997,852
- **Total Size**: 534.8 MB
- **Dataset ID Consistency**: ✅ Consistent

## Quick Quality Check
### ✅ No Major Issues Detected

## Dataset-Specific Analysis
### PACKET Dataset
- **File**: main_output/packet_dataset.csv
- **Size**: 22.5 MB
- **Records**: 266,986
- **Features**: 16 columns
- **Memory Usage**: 115.5 MB
- **Source Datasets**: 6 datasets
- **Records per Dataset**: 44,323 - 44,792 (avg: 44,498)
- **Distribution**: ✅ Well balanced
- **Quality Issues**: None detected ✅
#### 📊 Detailed Statistics for Problematic Columns
**packet_length** (int64):
- Total: 266,986, Finite: 266,986, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.01e+02, Median: 5.60e+01, Std: 1.80e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 16,736 (6.3%)
- Outlier fences: 2.60e+01 to 1.06e+02
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=3.57e+02, P99=1.17e+03

**ip_id** (int64):
- Total: 266,986, Finite: 266,986, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 6.55e+04
- Mean: 7.28e+03, Median: 1.00e+00, Std: 1.58e+04
- Zeros: 80,333, Negatives: 0
- Outliers (IQR): 61,215 (22.9%)
- Outlier fences: -1.50e+00 to 2.50e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=4.83e+04, P99=6.23e+04

**ip_len** (int64):
- Total: 266,986, Finite: 266,986, Missing: 0, Infinity: 0
- Range: 2.80e+01 to 1.50e+03
- Mean: 8.48e+01, Median: 4.00e+01, Std: 1.80e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 16,736 (6.3%)
- Outlier fences: 1.00e+01 to 9.00e+01
- Percentiles: P1=2.80e+01, P5=2.80e+01, P95=3.41e+02, P99=1.15e+03

**dst_port** (int64):
- Total: 266,986, Finite: 266,986, Missing: 0, Infinity: 0
- Range: -1.00e+00 to 6.55e+04
- Mean: 1.23e+04, Median: 8.00e+01, Std: 1.99e+04
- Zeros: 0, Negatives: 49,246
- Outliers (IQR): 31,496 (11.8%)
- Outlier fences: -2.76e+04 to 4.61e+04
- Percentiles: P1=-1.00e+00, P5=-1.00e+00, P95=5.70e+04, P99=6.36e+04

#### 🏷️ Label Distribution Analysis
**Label_multi**: 8 classes, 266,986 records
- normal: 144,757 (54.2%)
- syn_flood: 33,111 (12.4%)
- icmp_flood: 32,827 (12.3%)
- udp_flood: 20,462 (7.7%)
- ad_slow: 14,631 (5.5%)
- ad_udp: 10,986 (4.1%)
- ad_syn: 7,123 (2.7%)
- unknown: 3,089 (1.2%)

**Label_binary**: 2 classes, 266,986 records
- 0: 144,757 (54.2%)
- 1: 122,229 (45.8%)

- **Performance**: Fast loading, Memory efficiency: 5.1

### FLOW Dataset
- **File**: main_output/flow_dataset.csv
- **Size**: 492.1 MB
- **Records**: 3,681,215
- **Features**: 16 columns
- **Memory Usage**: 1342.5 MB
- **Source Datasets**: 6 datasets
- **Records per Dataset**: 412,385 - 655,800 (avg: 613,536)
- **Distribution**: ⚠️ Imbalanced (ratio: 1.59)
- **Quality Issues**: None detected ✅
#### 📊 Detailed Statistics for Problematic Columns
**pkt_rate** (float64):
- Total: 3,681,215, Finite: 3,681,215, Missing: 0, Infinity: 0
- Range: 4.20e-05 to 2.66e+00
- Mean: 9.41e-02, Median: 1.23e-04, Std: 3.45e-01
- Zeros: 0, Negatives: 0
- Outliers (IQR): 763,154 (20.7%)
- Outlier fences: -7.49e-04 to 1.42e-03
- Percentiles: P1=4.26e-05, P5=4.52e-05, P95=5.35e-01, P99=2.25e+00

**byte_rate** (float64):
- Total: 3,681,215, Finite: 3,681,215, Missing: 0, Infinity: 0
- Range: 4.12e-03 to 3.57e+02
- Mean: 8.85e+00, Median: 1.21e-02, Std: 3.74e+01
- Zeros: 0, Negatives: 0
- Outliers (IQR): 763,144 (20.7%)
- Outlier fences: -7.34e-02 to 1.39e-01
- Percentiles: P1=4.18e-03, P5=4.43e-03, P95=5.22e+01, P99=1.95e+02

#### 🏷️ Label Distribution Analysis
**Label_multi**: 7 classes, 3,681,215 records
- ad_syn: 1,148,880 (31.2%)
- ad_slow: 992,100 (27.0%)
- ad_udp: 729,545 (19.8%)
- normal: 646,920 (17.6%)
- udp_flood: 55,020 (1.5%)
- icmp_flood: 54,390 (1.5%)
- syn_flood: 54,360 (1.5%)

**Label_binary**: 2 classes, 3,681,215 records
- 1: 3,034,295 (82.4%)
- 0: 646,920 (17.6%)

- **Performance**: Medium loading, Memory efficiency: 2.7

### CICFLOW Dataset
- **File**: main_output/cicflow_dataset.csv
- **Size**: 20.2 MB
- **Records**: 49,651
- **Features**: 86 columns
- **Memory Usage**: 44.1 MB
- **Source Datasets**: 6 datasets
- **Records per Dataset**: 8,151 - 8,346 (avg: 8,275)
- **Distribution**: ✅ Well balanced
- **Quality Issues**: None detected ✅
#### 📊 Detailed Statistics for Problematic Columns
**dst_port** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: -1.00e+00 to 5.91e+04
- Mean: 5.96e+02, Median: 8.00e+01, Std: 2.57e+03
- Zeros: 0, Negatives: 8,963
- Outliers (IQR): 12,332 (24.8%)
- Outlier fences: 1.25e+01 to 1.20e+02
- Percentiles: P1=-1.00e+00, P5=-1.00e+00, P95=4.43e+02, P99=1.23e+04

**flow_duration** (float64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 2.40e+02
- Mean: 5.72e+00, Median: 1.30e-05, Std: 1.64e+01
- Zeros: 7,208, Negatives: 0
- Outliers (IQR): 9,181 (18.5%)
- Outlier fences: -3.74e+00 to 6.24e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=2.10e+01, P99=1.03e+02

**fwd_pkts_s** (float64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.50e+06
- Mean: 2.08e+05, Median: 1.58e+05, Std: 2.66e+05
- Zeros: 7,208, Negatives: 0
- Outliers (IQR): 5,775 (11.6%)
- Outlier fences: -3.75e+05 to 6.25e+05
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=7.50e+05, P99=1.00e+06

**tot_bwd_pkts** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 2.60e+01
- Mean: 2.14e+00, Median: 1.00e+00, Std: 3.20e+00
- Zeros: 17,830, Negatives: 0
- Outliers (IQR): 6,775 (13.6%)
- Outlier fences: -3.00e+00 to 5.00e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=1.00e+01, P99=1.00e+01

**totlen_fwd_pkts** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 1.12e+02 to 1.93e+04
- Mean: 4.99e+02, Median: 2.28e+02, Std: 8.59e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 7,889 (15.9%)
- Outlier fences: -1.26e+02 to 5.62e+02
- Percentiles: P1=1.12e+02, P5=1.12e+02, P95=2.39e+03, P99=3.52e+03

**totlen_bwd_pkts** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.46e+03
- Mean: 1.21e+02, Median: 6.20e+01, Std: 1.80e+02
- Zeros: 17,830, Negatives: 0
- Outliers (IQR): 6,775 (13.6%)
- Outlier fences: -1.68e+02 to 2.80e+02
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=5.60e+02, P99=5.60e+02

**fwd_pkt_len_max** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.67e+02, Median: 7.60e+01, Std: 2.77e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 7,571 (15.2%)
- Outlier fences: 2.60e+01 to 1.06e+02
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=8.48e+02, P99=1.39e+03

**fwd_pkt_len_mean** (float64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 9.90e+01, Median: 7.60e+01, Std: 1.28e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 6,757 (13.6%)
- Outlier fences: 2.60e+01 to 1.06e+02
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=2.53e+02, P99=8.13e+02

**pkt_len_max** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.67e+02, Median: 7.60e+01, Std: 2.77e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 7,571 (15.2%)
- Outlier fences: 2.60e+01 to 1.06e+02
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=8.48e+02, P99=1.39e+03

**pkt_len_min** (int64):
- Total: 49,651, Finite: 49,651, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 7.60e+01, Median: 5.60e+01, Std: 1.22e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 3,459 (7.0%)
- Outlier fences: 3.35e+01 to 9.35e+01
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=1.00e+02, P99=8.13e+02

#### 🏷️ Label Distribution Analysis
**Label_multi**: 7 classes, 49,651 records
- normal: 11,262 (22.7%)
- udp_flood: 8,315 (16.7%)
- syn_flood: 8,219 (16.6%)
- ad_syn: 7,128 (14.4%)
- icmp_flood: 6,546 (13.2%)
- ad_slow: 4,185 (8.4%)
- ad_udp: 3,996 (8.0%)

**Label_binary**: 2 classes, 49,651 records
- 1: 38,389 (77.3%)
- 0: 11,262 (22.7%)

- **Performance**: Fast loading, Memory efficiency: 2.2

## Cross-Dataset Consistency
✅ **All datasets contain the same source dataset IDs**
- Common dataset IDs: 1607-1, 1607-2, 1707-1, 1707-2, 1807-1, 1907-1

## 🧹 Detailed Data Cleaning Recommendations
### Outlier Treatment
#### PACKET Dataset:
- **packet_length** (6.3% outliers, 6.2% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [2.60e+01, 1.06e+02]
- **ip_id** (22.9% outliers, 22.9% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-1.50e+00, 2.50e+00]
- **ip_len** (6.3% outliers, 6.2% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [1.00e+01, 9.00e+01]
- **dst_port** (11.8% outliers, 0.0% extreme):
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-2.76e+04, 4.61e+04]
#### FLOW Dataset:
- **pkt_rate** (20.7% outliers, 19.6% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-7.49e-04, 1.42e-03]
- **byte_rate** (20.7% outliers, 19.6% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-7.34e-02, 1.39e-01]
#### CICFLOW Dataset:
- **dst_port** (24.8% outliers, 6.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.25e+01, 1.20e+02]
- **flow_duration** (18.5% outliers, 18.5% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-3.74e+00, 6.24e+00]
- **fwd_pkts_s** (11.6% outliers, 2.4% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-3.75e+05, 6.25e+05]
- **tot_bwd_pkts** (13.6% outliers, 9.1% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-3.00e+00, 5.00e+00]
- **totlen_fwd_pkts** (15.9% outliers, 14.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-1.26e+02, 5.62e+02]

### Dataset-Specific Cleaning Strategies
#### PACKET Dataset Cleaning Plan:
   4. **Packet-specific**: Validate timestamp sequences and packet ordering
   5. **Network validation**: Check for impossible protocol combinations
   6. **Normalization**: Apply appropriate scaling based on outlier analysis
   7. **Validation**: Cross-check cleaned data maintains attack patterns

#### FLOW Dataset Cleaning Plan:
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