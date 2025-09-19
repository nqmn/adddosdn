# Data Leakage Assessment Report
Generated on: 2025-09-19 12:13:35
Dataset Path: ../main_output/v4

## Executive Summary
**Overall Assessment**: ⚠️ CRITICAL DATA LEAKAGE DETECTED
**Recommendation**: Immediate attention required before ML training
**Folders Analyzed**: 0/1
**Features Analyzed**: 138
**Potentially Leaky Features**: 60 (43.5%)

## Risk Distribution Across Folders
- CRITICAL: 1 folders

## Detailed Analysis by Folder
### Folder: v3_combined_datasets
**Overall Risk**: CRITICAL
**CSV Files**: flow_dataset.csv, packet_dataset.csv, cicflow_dataset.csv

#### Dataset: flow_dataset
**Total Features**: 19
**Overall Risk**: CRITICAL
**Detected Leakage Categories**:
- **Target Leakage** (CRITICAL): 2 features (10.5%)
  - Description: Features directly derived from target variable
  - Features: Label_multi, Label_binary
- **Statistical Leakage** (HIGH): 3 features (15.8%)
  - Description: Pre-computed statistical features that may contain future info
  - Features: avg_pkt_size, pkt_rate, byte_rate
- **Size Duration Leakage** (LOW): 5 features (26.3%)
  - Description: Packet/flow size and duration metrics that may reveal attack patterns
  - Features: packet_count, byte_count, duration_sec, duration_nsec, avg_pkt_size
- **Infrastructure Leakage** (LOW): 9 features (47.4%)
  - Description: Network infrastructure details (typically dropped in ML)
  - Features: dataset_id, timestamp, switch_id, table_id, cookie, in_port, eth_src, eth_dst, out_port

#### Dataset: packet_dataset
**Total Features**: 33
**Overall Risk**: CRITICAL
**Detected Leakage Categories**:
- **Target Leakage** (CRITICAL): 2 features (6.1%)
  - Description: Features directly derived from target variable
  - Features: Label_multi, Label_binary
- **Protocol Specific Leakage** (MEDIUM): 5 features (15.2%)
  - Description: Protocol-specific features that may reveal attack signatures
  - Features: tcp_flags, tcp_seq, tcp_ack, tcp_urgent, icmp_type
- **Size Duration Leakage** (LOW): 1 features (3.0%)
  - Description: Packet/flow size and duration metrics that may reveal attack patterns
  - Features: packet_length
- **Infrastructure Leakage** (LOW): 12 features (36.4%)
  - Description: Network infrastructure details (typically dropped in ML)
  - Features: dataset_id, timestamp, eth_type, ip_id, src_port, dst_port, tcp_seq, udp_sport, udp_dport, icmp_id
  - ... and 2 more

#### Dataset: cicflow_dataset
**Total Features**: 86
**Overall Risk**: CRITICAL
**Detected Leakage Categories**:
- **Target Leakage** (CRITICAL): 3 features (3.5%)
  - Description: Features directly derived from target variable
  - Features: Label_multi, Label_binary, Attack_Type
- **Statistical Leakage** (HIGH): 2 features (2.3%)
  - Description: Pre-computed statistical features that may contain future info
  - Features: fwd_blk_rate_avg, bwd_blk_rate_avg
- **Protocol Specific Leakage** (MEDIUM): 3 features (3.5%)
  - Description: Protocol-specific features that may reveal attack signatures
  - Features: fin_flag_cnt, syn_flag_cnt, rst_flag_cnt
- **Size Duration Leakage** (LOW): 5 features (5.8%)
  - Description: Packet/flow size and duration metrics that may reveal attack patterns
  - Features: flow_duration, fwd_seg_size_min, pkt_size_avg, fwd_seg_size_avg, bwd_seg_size_avg
- **Infrastructure Leakage** (LOW): 8 features (9.3%)
  - Description: Network infrastructure details (typically dropped in ML)
  - Features: dataset_id, src_port, dst_port, timestamp, idle_max, idle_min, idle_mean, idle_std

#### 🔍 Detailed Feature Uniqueness Analysis for cicflow_dataset
**Summary**: 268,887 total records
- **Constant features**: 10 features (may be removable)
- **Near-constant features**: 46 features (<1% unique)

**🚨 Detailed Analysis of Risky Features:**

| Feature | Risk Type | Unique Count | Unique Ratio | Data Type | Sample Values | Notes |
|---------|-----------|--------------|--------------|-----------|---------------|-------|
| Attack_Type | Target Leakage | 7 | 0.000 | object | ad_udp, icmp_flood, syn_flood, ... | Near-constant |
| Label_binary | Target Leakage | 2 | 0.000 | int64 | 1.0, 0.0 | Near-constant |
| Label_multi | Target Leakage | 7 | 0.000 | object | ad_udp, icmp_flood, syn_flood, ... | Near-constant |
| bwd_blk_rate_avg | Statistical Leakage | 15,918 | 0.059 | float64 | 15926829.268292682, 18138888.888888888, 18657142.85714285, ... | Normal |
| bwd_seg_size_avg | Size Duration Leakage | 1,451 | 0.005 | float64 | 178.16666666666666, 168.28571428571428, 44.0, ... | Near-constant |
| dataset_id | Infrastructure Leakage | 95 | 0.000 | object | 120925-1, 120925-10, 120925-11, ... | Near-constant |
| dst_port | Infrastructure Leakage | 24 | 0.000 | int64 | 80.0, -1.0, 443.0, ... | Near-constant |
| fin_flag_cnt | Protocol Specific Leakage | 9 | 0.000 | int64 | 4.0, -1.0, 0.0, ... | Near-constant |
| flow_duration | Size Duration Leakage | 33,745 | 0.126 | float64 | 0.001336, 0.001176, 0.001085, ... | Normal |
| fwd_blk_rate_avg | Statistical Leakage | 2,645 | 0.010 | float64 | 0.0, 283081081.0810811, 262709677.41935483, ... | Near-constant |
| fwd_seg_size_avg | Size Duration Leakage | 7,119 | 0.026 | float64 | 104.15384615384616, 97.6923076923077, 101.07692307692308, ... | Normal |
| fwd_seg_size_min | Size Duration Leakage | 1 | 0.000 | int64 | 20.0 | Constant |
| idle_max | Infrastructure Leakage | 1 | 0.000 | int64 | 0.0 | Constant |
| idle_mean | Infrastructure Leakage | 1 | 0.000 | int64 | 0.0 | Constant |
| idle_min | Infrastructure Leakage | 1 | 0.000 | int64 | 0.0 | Constant |
| idle_std | Infrastructure Leakage | 1 | 0.000 | int64 | 0.0 | Constant |
| pkt_size_avg | Size Duration Leakage | 7,405 | 0.028 | float64 | 139.68, 136.32, 138.08, ... | Normal |
| rst_flag_cnt | Protocol Specific Leakage | 21 | 0.000 | int64 | 0.0, -1.0, 2.0, ... | Near-constant |
| src_port | Infrastructure Leakage | 45,278 | 0.168 | int64 | 52880.0, 52886.0, 52902.0, ... | Normal |
| syn_flag_cnt | Protocol Specific Leakage | 15 | 0.000 | int64 | 5.0, -1.0, 3.0, ... | Near-constant |
| timestamp | Infrastructure Leakage | 53,318 | 0.198 | object | 2025-09-12 16:19:49, 2025-09-12 16:19:50, 2025-09-12 16:19:51, ... | Normal |

**🔧 Constant/Near-Constant Feature Analysis:**
- **fwd_seg_size_min** (CONSTANT): Always = `20.0` → **REMOVE**
- **fwd_iat_min** (CONSTANT): Always = `0.0` → **REMOVE**
- **active_max** (CONSTANT): Always = `0.0` → **REMOVE**
- **active_min** (CONSTANT): Always = `0.0` → **REMOVE**
- **active_mean** (CONSTANT): Always = `0.0` → **REMOVE**
- **active_std** (CONSTANT): Always = `0.0` → **REMOVE**
- **idle_max** (CONSTANT): Always = `0.0` → **REMOVE**
- **idle_min** (CONSTANT): Always = `0.0` → **REMOVE**
- **idle_mean** (CONSTANT): Always = `0.0` → **REMOVE**
- **idle_std** (CONSTANT): Always = `0.0` → **REMOVE**
- **dataset_id** (NEAR-CONSTANT): 95 unique values → Consider removal
- **src_ip** (NEAR-CONSTANT): 1057 unique values → Consider removal
- **dst_ip** (NEAR-CONSTANT): 44 unique values → Consider removal
  - Most common: `192.168.30.10` (207,994 records, 77.4%)
- **dst_port** (NEAR-CONSTANT): 24 unique values → Consider removal
- **protocol** (NEAR-CONSTANT): 3 unique values → Consider removal
- **tot_fwd_pkts** (NEAR-CONSTANT): 116 unique values → Consider removal
- **tot_bwd_pkts** (NEAR-CONSTANT): 75 unique values → Consider removal
- **totlen_bwd_pkts** (NEAR-CONSTANT): 1528 unique values → Consider removal
- **fwd_pkt_len_min** (NEAR-CONSTANT): 1468 unique values → Consider removal
- **bwd_pkt_len_max** (NEAR-CONSTANT): 1417 unique values → Consider removal
- **bwd_pkt_len_min** (NEAR-CONSTANT): 1402 unique values → Consider removal
- **bwd_pkt_len_mean** (NEAR-CONSTANT): 1451 unique values → Consider removal
- **bwd_pkt_len_std** (NEAR-CONSTANT): 56 unique values → Consider removal
- **pkt_len_min** (NEAR-CONSTANT): 1468 unique values → Consider removal
- **fwd_header_len** (NEAR-CONSTANT): 116 unique values → Consider removal
- **bwd_header_len** (NEAR-CONSTANT): 75 unique values → Consider removal
- **fwd_act_data_pkts** (NEAR-CONSTANT): 79 unique values → Consider removal
- **flow_iat_min** (NEAR-CONSTANT): 2 unique values → Consider removal
- **bwd_iat_min** (NEAR-CONSTANT): 448 unique values → Consider removal
- **fwd_psh_flags** (NEAR-CONSTANT): 13 unique values → Consider removal
- **bwd_psh_flags** (NEAR-CONSTANT): 24 unique values → Consider removal
- **fwd_urg_flags** (NEAR-CONSTANT): 2 unique values → Consider removal
- **bwd_urg_flags** (NEAR-CONSTANT): 2 unique values → Consider removal
- **fin_flag_cnt** (NEAR-CONSTANT): 9 unique values → Consider removal
- **syn_flag_cnt** (NEAR-CONSTANT): 15 unique values → Consider removal
- **rst_flag_cnt** (NEAR-CONSTANT): 21 unique values → Consider removal
- **psh_flag_cnt** (NEAR-CONSTANT): 31 unique values → Consider removal
- **ack_flag_cnt** (NEAR-CONSTANT): 52 unique values → Consider removal
- **urg_flag_cnt** (NEAR-CONSTANT): 2 unique values → Consider removal
- **ece_flag_cnt** (NEAR-CONSTANT): 2 unique values → Consider removal
- **down_up_ratio** (NEAR-CONSTANT): 97 unique values → Consider removal
- **init_fwd_win_byts** (NEAR-CONSTANT): 9 unique values → Consider removal
- **init_bwd_win_byts** (NEAR-CONSTANT): 8 unique values → Consider removal
- **fwd_byts_b_avg** (NEAR-CONSTANT): 2126 unique values → Consider removal
- **fwd_pkts_b_avg** (NEAR-CONSTANT): 94 unique values → Consider removal
- **bwd_byts_b_avg** (NEAR-CONSTANT): 1429 unique values → Consider removal
- **bwd_pkts_b_avg** (NEAR-CONSTANT): 31 unique values → Consider removal
- **fwd_blk_rate_avg** (NEAR-CONSTANT): 2645 unique values → Consider removal
- **bwd_seg_size_avg** (NEAR-CONSTANT): 1451 unique values → Consider removal
- **cwr_flag_count** (NEAR-CONSTANT): 2 unique values → Consider removal
- **subflow_fwd_pkts** (NEAR-CONSTANT): 116 unique values → Consider removal
- **subflow_bwd_pkts** (NEAR-CONSTANT): 75 unique values → Consider removal
- **subflow_bwd_byts** (NEAR-CONSTANT): 1528 unique values → Consider removal
- **Label_multi** (NEAR-CONSTANT): 7 unique values → Consider removal
  - Most common: `udp_flood` (88,699 records, 33.0%)
- **Label_binary** (NEAR-CONSTANT): 2 unique values → Consider removal
- **Attack_Type** (NEAR-CONSTANT): 7 unique values → Consider removal
  - Most common: `udp_flood` (88,699 records, 33.0%)

#### Temporal Analysis
**flow_dataset** temporal issues:
- MEDIUM: 224252 large timestamp gaps detected - Irregular timestamp gaps may indicate data collection issues
- MEDIUM: 1335516 duplicate timestamps - High number of duplicate timestamps may indicate processing errors
**packet_dataset** temporal issues:
- MEDIUM: 457509 large timestamp gaps detected - Irregular timestamp gaps may indicate data collection issues
**cicflow_dataset** temporal issues:
- MEDIUM: 268886 duplicate timestamps - High number of duplicate timestamps may indicate processing errors

#### Label Correlation Analysis
**cicflow_dataset** label issues:
- CRITICAL: Attack_Type - Feature name suggests target variable derivation


## 🛠️ Data Leakage Mitigation Recommendations
### Critical Actions Required
1. **Remove target-derived features**: Features directly derived from target variables must be removed
1. **Feature audit**: Manually review all flagged features before training
1. **Temporal validation**: Ensure proper temporal train/test splits

### Feature-Specific Recommendations
#### Target Leakage (CRITICAL Risk)
**Affected features**: Attack_Type, Label_binary, Label_multi
**Action**: Remove these features immediately

#### Statistical Leakage (HIGH Risk)
**Affected features**: avg_pkt_size, bwd_blk_rate_avg, byte_rate, fwd_blk_rate_avg, pkt_rate
**Action**: Review if statistics are computed over future data; recompute if necessary

#### Size Duration Leakage (LOW Risk)
**Affected features**: avg_pkt_size, bwd_seg_size_avg, byte_count, duration_nsec, duration_sec, flow_duration, fwd_seg_size_avg, fwd_seg_size_min, packet_count, packet_length, pkt_size_avg
**Action**: Review for necessity and potential impact on generalization

#### Infrastructure Leakage (LOW Risk)
**Affected features**: cookie, dataset_id, dst_port, eth_dst, eth_src, eth_type, icmp_id, icmp_seq, idle_max, idle_mean, idle_min, idle_std, in_port, ip_id, out_port, src_port, switch_id, table_id, tcp_seq, timestamp, transport_protocol, udp_dport, udp_sport
**Action**: Consider removing if they don't generalize to other network environments

#### Protocol Specific Leakage (MEDIUM Risk)
**Affected features**: fin_flag_cnt, icmp_type, rst_flag_cnt, syn_flag_cnt, tcp_ack, tcp_flags, tcp_seq, tcp_urgent
**Action**: Review for necessity and potential impact on generalization

### ML Pipeline Recommendations
1. **Temporal Splits**: Use timestamp-based train/test splits, not random splits
2. **Cross-validation**: Use time-series cross-validation for temporal data
3. **Feature Engineering**: Create features from raw data within each fold separately
4. **Validation Strategy**: Implement separate validation on hold-out temporal data
5. **Model Monitoring**: Track feature importance to detect potential leakage indicators

### 🐍 Python Code for Leakage Prevention
#### Temporal Train/Test Split
```python
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

# Load data and sort by timestamp
df = pd.read_csv('dataset.csv')
df = df.sort_values('timestamp')

# Time-based split (80% train, 20% test)
split_time = df['timestamp'].quantile(0.8)
train_data = df[df['timestamp'] <= split_time]
test_data = df[df['timestamp'] > split_time]

# Remove timestamp from features
feature_cols = [col for col in df.columns if col not in ['timestamp', 'Label_multi', 'Label_binary']]
X_train, y_train = train_data[feature_cols], train_data['Label_binary']
X_test, y_test = test_data[feature_cols], test_data['Label_binary']
```

#### Feature Leakage Detection
```python
def detect_leakage_features(df, target_col):
    leaky_features = []
    
    for col in df.columns:
        if col == target_col:
            continue
        
        # Check correlation with target
        if df[col].dtype in ['int64', 'float64']:
            corr = df[col].corr(df[target_col])
            if abs(corr) > 0.9:  # Very high correlation
                leaky_features.append((col, corr))
        
        # Check for suspicious names
        suspicious_patterns = ['label', 'target', 'class', 'attack', 'malicious']
        if any(pattern in col.lower() for pattern in suspicious_patterns):
            leaky_features.append((col, 'suspicious_name'))
    
    return leaky_features
```
