# Combined Datasets Quality Investigation Report
Generated on: 2025-07-21 00:17:35

## Executive Summary
- **Data Integrity Score**: 100.0/100 (EXCELLENT ✅)
- **Files Processed**: 3/3 (100.0%)
- **Total Records**: 591,318
- **Total Size**: 84.2 MB
- **Dataset ID Consistency**: ✅ Consistent

## Quick Quality Check
### Issues Detected:
- ⚠️ Missing values: 1,480,489
- ⚠️ Duplicate rows: 1,830

## Dataset-Specific Analysis
### PACKET Dataset
- **File**: main_output/v2_main/packet_dataset.csv
- **Size**: 9.3 MB
- **Records**: 108,327
- **Features**: 16 columns
- **Memory Usage**: 45.3 MB
- **Source Datasets**: 12 datasets
- **Records per Dataset**: 8,949 - 9,167 (avg: 9,027)
- **Distribution**: ✅ Well balanced
- **Quality Issues**: Missing: 125,833 (7.26%), Duplicates: 19 (0.02%)
#### 🔍 Detailed Missing Values Analysis
| Column | Missing Count | % Missing | Data Type | Pattern |
|--------|---------------|-----------|-----------|---------|
| ip_flags | 65,665 | 60.62% | object | scattered |
| tcp_flags | 27,072 | 24.99% | object | scattered |
| src_port | 16,548 | 15.28% | float64 | scattered |
| dst_port | 16,548 | 15.28% | float64 | scattered |
#### 📊 Detailed Statistics for Problematic Columns
**timestamp** (float64):
- Total: 108,327, Finite: 108,327, Missing: 0, Infinity: 0
- Range: 1.75e+09 to 1.75e+09
- Mean: 1.75e+09, Median: 1.75e+09, Std: 4.34e+04
- Zeros: 0, Negatives: 0
- Outliers (IQR): 27,069 (25.0%)
- Outlier fences: 1.75e+09 to 1.75e+09
- Percentiles: P1=1.75e+09, P5=1.75e+09, P95=1.75e+09, P99=1.75e+09

**packet_length** (int64):
- Total: 108,327, Finite: 108,327, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.12e+02, Median: 5.60e+01, Std: 2.01e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 15,848 (14.6%)
- Outlier fences: 3.05e+01 to 9.85e+01
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=5.29e+02, P99=1.24e+03

**ip_id** (int64):
- Total: 108,327, Finite: 108,327, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 6.55e+04
- Mean: 2.56e+03, Median: 1.00e+00, Std: 1.03e+04
- Zeros: 40,490, Negatives: 0
- Outliers (IQR): 8,400 (7.8%)
- Outlier fences: -1.50e+00 to 2.50e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=2.27e+04, P99=5.82e+04

**ip_len** (int64):
- Total: 108,327, Finite: 108,327, Missing: 0, Infinity: 0
- Range: 2.80e+01 to 1.50e+03
- Mean: 9.55e+01, Median: 4.00e+01, Std: 2.01e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 15,848 (14.6%)
- Outlier fences: 1.45e+01 to 8.25e+01
- Percentiles: P1=2.80e+01, P5=2.80e+01, P95=5.13e+02, P99=1.22e+03

**src_port** (float64):
- Total: 108,327, Finite: 91,779, Missing: 16,548, Infinity: 0
- Range: 2.00e+01 to 6.55e+04
- Mean: 2.10e+04, Median: 1.23e+04, Std: 2.28e+04
- Zeros: 0, Negatives: 0
- Percentiles: P1=2.10e+01, P5=2.10e+01, P95=6.10e+04, P99=6.46e+04

**dst_port** (float64):
- Total: 108,327, Finite: 91,779, Missing: 16,548, Infinity: 0
- Range: 2.10e+01 to 6.55e+04
- Mean: 1.58e+04, Median: 4.43e+02, Std: 2.11e+04
- Zeros: 0, Negatives: 0
- Percentiles: P1=2.10e+01, P5=2.10e+01, P95=5.92e+04, P99=6.41e+04

#### 🏷️ Label Distribution Analysis
**Label_multi**: 5 classes, 108,327 records
- normal: 73,532 (67.9%)
- syn_flood: 16,080 (14.8%)
- udp_flood: 10,304 (9.5%)
- icmp_flood: 8,148 (7.5%)
- ad_syn: 263 (0.2%)

**Label_binary**: 2 classes, 108,327 records
- 0: 73,532 (67.9%)
- 1: 34,795 (32.1%)

- **Performance**: Fast loading, Memory efficiency: 4.8

### FLOW Dataset
- **File**: main_output/v2_main/flow_dataset.csv
- **Size**: 58.2 MB
- **Records**: 437,441
- **Features**: 19 columns
- **Memory Usage**: 169.6 MB
- **Source Datasets**: 12 datasets
- **Records per Dataset**: 36,239 - 36,797 (avg: 36,453)
- **Distribution**: ✅ Well balanced
- **Quality Issues**: Missing: 1,354,656 (16.30%)
#### 🔍 Detailed Missing Values Analysis
| Column | Missing Count | % Missing | Data Type | Pattern |
|--------|---------------|-----------|-----------|---------|
| table_id | 437,441 | 100.00% | float64 | mostly_missing |
| cookie | 437,441 | 100.00% | float64 | mostly_missing |
| duration_nsec | 437,441 | 100.00% | float64 | mostly_missing |
| in_port | 14,111 | 3.23% | float64 | scattered |
| eth_src | 14,111 | 3.23% | object | scattered |
| eth_dst | 14,111 | 3.23% | object | scattered |
#### 📊 Detailed Statistics for Problematic Columns
**table_id** (float64):
- Total: 437,441, Finite: 0, Missing: 437,441, Infinity: 0

**cookie** (float64):
- Total: 437,441, Finite: 0, Missing: 437,441, Infinity: 0

**in_port** (float64):
- Total: 437,441, Finite: 423,330, Missing: 14,111, Infinity: 0
- Range: 1.00e+00 to 6.00e+00
- Mean: 3.50e+00, Median: 3.50e+00, Std: 1.71e+00
- Zeros: 0, Negatives: 0
- Percentiles: P1=1.00e+00, P5=1.00e+00, P95=6.00e+00, P99=6.00e+00

**duration_nsec** (float64):
- Total: 437,441, Finite: 0, Missing: 437,441, Infinity: 0

**pkt_rate** (float64):
- Total: 437,441, Finite: 437,441, Missing: 0, Infinity: 0
- Range: 8.35e-04 to 8.25e+00
- Mean: 2.18e-01, Median: 2.00e-03, Std: 6.48e-01
- Zeros: 0, Negatives: 0
- Outliers (IQR): 77,939 (17.8%)
- Outlier fences: -5.70e-03 to 1.27e-02
- Percentiles: P1=8.53e-04, P5=9.01e-04, P95=2.21e+00, P99=2.65e+00

**byte_rate** (float64):
- Total: 437,441, Finite: 437,441, Missing: 0, Infinity: 0
- Range: 8.18e-02 to 7.54e+02
- Mean: 1.92e+01, Median: 1.96e-01, Std: 6.52e+01
- Zeros: 0, Negatives: 0
- Outliers (IQR): 77,883 (17.8%)
- Outlier fences: -5.58e-01 to 1.25e+00
- Percentiles: P1=8.36e-02, P5=8.83e-02, P95=1.58e+02, P99=3.49e+02

#### 🏷️ Label Distribution Analysis
**Label_multi**: 5 classes, 437,441 records
- normal: 337,218 (77.1%)
- udp_flood: 30,504 (7.0%)
- syn_flood: 29,450 (6.7%)
- icmp_flood: 29,450 (6.7%)
- ad_syn: 10,819 (2.5%)

**Label_binary**: 2 classes, 437,441 records
- 0: 337,218 (77.1%)
- 1: 100,223 (22.9%)

- **Performance**: Fast loading, Memory efficiency: 2.9

### CICFLOW Dataset
- **File**: main_output/v2_main/cicflow_dataset.csv
- **Size**: 16.7 MB
- **Records**: 45,550
- **Features**: 86 columns
- **Memory Usage**: 40.6 MB
- **Source Datasets**: 12 datasets
- **Records per Dataset**: 3,750 - 3,843 (avg: 3,796)
- **Distribution**: ✅ Well balanced
- **Quality Issues**: Duplicates: 1,811 (3.98%)
#### 📊 Detailed Statistics for Problematic Columns
**dst_port** (int64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: -1.00e+00 to 6.08e+04
- Mean: 4.16e+02, Median: 8.00e+01, Std: 2.49e+03
- Zeros: 0, Negatives: 5,291
- Outliers (IQR): 7,058 (15.5%)
- Outlier fences: 1.25e+01 to 1.20e+02
- Percentiles: P1=-1.00e+00, P5=-1.00e+00, P95=8.00e+01, P99=1.23e+04

**timestamp** (float64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 1.75e+09 to 1.75e+09
- Mean: 1.75e+09, Median: 1.75e+09, Std: 4.34e+04
- Zeros: 0, Negatives: 0
- Outliers (IQR): 5,316 (11.7%)
- Outlier fences: 1.75e+09 to 1.75e+09
- Percentiles: P1=1.75e+09, P5=1.75e+09, P95=1.75e+09, P99=1.75e+09

**flow_duration** (float64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 2.57e+02
- Mean: 4.50e+00, Median: 4.00e-06, Std: 1.18e+01
- Zeros: 19,705, Negatives: 0
- Outliers (IQR): 8,116 (17.8%)
- Outlier fences: -2.75e+00 to 4.59e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=2.10e+01, P99=2.10e+01

**fwd_pkts_s** (float64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.50e+06
- Mean: 1.44e+05, Median: 1.43e-01, Std: 2.49e+05
- Zeros: 19,705, Negatives: 0
- Outliers (IQR): 6,000 (13.2%)
- Outlier fences: -3.00e+05 to 5.00e+05
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=7.50e+05, P99=7.50e+05

**bwd_pkts_s** (float64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.82e+05
- Mean: 1.41e+04, Median: 0.00e+00, Std: 4.09e+04
- Zeros: 29,264, Negatives: 0
- Outliers (IQR): 8,461 (18.6%)
- Outlier fences: -7.14e-02 to 1.19e-01
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=1.33e+05, P99=1.54e+05

**tot_fwd_pkts** (int64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 2.00e+00 to 1.61e+02
- Mean: 3.30e+00, Median: 3.00e+00, Std: 3.54e+00
- Zeros: 0, Negatives: 0
- Outliers (IQR): 3,627 (8.0%)
- Outlier fences: 5.00e-01 to 4.50e+00
- Percentiles: P1=2.00e+00, P5=2.00e+00, P95=1.10e+01, P99=1.10e+01

**tot_bwd_pkts** (int64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 2.60e+01
- Mean: 1.11e+00, Median: 0.00e+00, Std: 2.59e+00
- Zeros: 29,264, Negatives: 0
- Outliers (IQR): 3,469 (7.6%)
- Outlier fences: -1.50e+00 to 2.50e+00
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=1.00e+01, P99=1.00e+01

**totlen_fwd_pkts** (int64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 1.12e+02 to 1.61e+04
- Mean: 3.47e+02, Median: 1.32e+02, Std: 6.78e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 4,128 (9.1%)
- Outlier fences: -2.20e+01 to 3.78e+02
- Percentiles: P1=1.28e+02, P5=1.28e+02, P95=1.58e+03, P99=3.29e+03

**totlen_bwd_pkts** (int64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 0.00e+00 to 1.46e+03
- Mean: 6.51e+01, Median: 0.00e+00, Std: 1.46e+02
- Zeros: 29,264, Negatives: 0
- Outliers (IQR): 4,555 (10.0%)
- Outlier fences: -9.30e+01 to 1.55e+02
- Percentiles: P1=0.00e+00, P5=0.00e+00, P95=5.60e+02, P99=5.60e+02

**fwd_pkt_len_max** (int64):
- Total: 45,550, Finite: 45,550, Missing: 0, Infinity: 0
- Range: 4.40e+01 to 1.52e+03
- Mean: 1.22e+02, Median: 6.40e+01, Std: 2.13e+02
- Zeros: 0, Negatives: 0
- Outliers (IQR): 9,017 (19.8%)
- Outlier fences: 4.60e+01 to 9.40e+01
- Percentiles: P1=4.40e+01, P5=4.40e+01, P95=5.79e+02, P99=1.28e+03

#### 🏷️ Label Distribution Analysis
**Label_multi**: 7 classes, 45,550 records
- ad_syn: 19,639 (43.1%)
- normal: 5,721 (12.6%)
- udp_flood: 4,189 (9.2%)
- ad_slow: 4,117 (9.0%)
- icmp_flood: 4,073 (8.9%)
- syn_flood: 4,006 (8.8%)
- ad_udp: 3,805 (8.4%)

**Label_binary**: 2 classes, 45,550 records
- 1: 39,829 (87.4%)
- 0: 5,721 (12.6%)

- **Performance**: Fast loading, Memory efficiency: 2.4

## Cross-Dataset Consistency
✅ **All datasets contain the same source dataset IDs**
- Common dataset IDs: 190725-1, 190725-2, 190725-3, 190725-4, 190725-5, 190725-6, 190725-7, 200725-1, 200725-2, 200725-3, 200725-4, 200725-5

## 🧹 Detailed Data Cleaning Recommendations
### Missing Values Treatment
#### PACKET Dataset:
- **ip_flags** (60.6% missing): Consider dropping or use advanced imputation (e.g., iterative)
- **tcp_flags** (25.0% missing): Use mode imputation or 'unknown' category
- **src_port** (15.3% missing): Safe for median/mean imputation
- **dst_port** (15.3% missing): Safe for median/mean imputation
#### FLOW Dataset:
- **table_id** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation
- **cookie** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation
- **duration_nsec** (100.0% missing): **DROP COLUMN** - Too sparse for reliable imputation
- **in_port** (3.2% missing): Simple interpolation or deletion of missing rows
- **eth_src** (3.2% missing): Simple interpolation or deletion of missing rows
- **eth_dst** (3.2% missing): Simple interpolation or deletion of missing rows

### Outlier Treatment
#### PACKET Dataset:
- **timestamp** (25.0% outliers, 0.0% extreme):
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.75e+09, 1.75e+09]
- **packet_length** (14.6% outliers, 7.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [3.05e+01, 9.85e+01]
- **ip_id** (7.8% outliers, 7.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Use robust statistics (median, IQR) for normalization
  - **Clipping bounds**: [-1.50e+00, 2.50e+00]
- **ip_len** (14.6% outliers, 7.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.45e+01, 8.25e+01]
#### FLOW Dataset:
- **pkt_rate** (17.8% outliers, 15.6% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-5.70e-03, 1.27e-02]
- **byte_rate** (17.8% outliers, 15.6% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-5.58e-01, 1.25e+00]
#### CICFLOW Dataset:
- **dst_port** (15.5% outliers, 3.9% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.25e+01, 1.20e+02]
- **timestamp** (11.7% outliers, 0.0% extreme):
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [1.75e+09, 1.75e+09]
- **flow_duration** (17.8% outliers, 17.8% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-2.75e+00, 4.59e+00]
- **fwd_pkts_s** (13.2% outliers, 0.7% extreme):
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-3.00e+05, 5.00e+05]
- **bwd_pkts_s** (18.6% outliers, 18.5% extreme):
  - **Action**: Cap extreme outliers at 3×IQR boundaries
  - **Action**: Apply log transformation or robust scaling
  - **Clipping bounds**: [-7.14e-02, 1.19e-01]

### Dataset-Specific Cleaning Strategies
#### PACKET Dataset Cleaning Plan:
   1. **Remove duplicates**: Drop 19 duplicate rows
   3. **Impute missing**: Apply appropriate imputation for 125,833 missing values
   4. **Packet-specific**: Validate timestamp sequences and packet ordering
   5. **Network validation**: Check for impossible protocol combinations
   6. **Normalization**: Apply appropriate scaling based on outlier analysis
   7. **Validation**: Cross-check cleaned data maintains attack patterns

#### FLOW Dataset Cleaning Plan:
   3. **Impute missing**: Apply appropriate imputation for 1,354,656 missing values
   4. **Flow-specific**: Consider time-based interpolation for flow statistics
   5. **Feature engineering**: Create flow duration and rate features from existing data
   6. **Normalization**: Apply appropriate scaling based on outlier analysis
   7. **Validation**: Cross-check cleaned data maintains attack patterns

#### CICFLOW Dataset Cleaning Plan:
   1. **Remove duplicates**: Drop 1,811 duplicate rows
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