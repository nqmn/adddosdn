# Combined Dataset Leakage Analysis - AdDDoSDN v3

**Analysis Date:** 2025-09-19 12:15:19.726604
**Base Directory:** ../main_output/v4
**Combined Datasets Analyzed:** 3
**Dataset Types:** flow_dataset.csv, packet_dataset.csv, cicflow_dataset.csv

## Overall Risk Assessment

- **🚨 HIGH Risk**: 2 datasets (>95% accuracy)
- **⚠️  MEDIUM Risk**: 1 datasets (90-95% accuracy)
- **✅ LOW Risk**: 0 datasets (<90% accuracy)

## Detailed Results by Dataset

### v4/cicflow_dataset.csv
- **Label_binary**: 0.999975 (HIGH risk)
- **Label_multi**: 1.000000 (HIGH risk)

### v4/flow_dataset.csv
- **Label_binary**: 0.997091 (HIGH risk)
- **Label_multi**: 0.982981 (HIGH risk)

### v4/packet_dataset.csv
- **Label_binary**: 0.932295 (MEDIUM risk)
- **Label_multi**: 0.844714 (LOW risk)

## Key Recommendations

1. **Immediate Action**: Drop protocol identifiers (icmp_type, tcp_flags, transport_protocol)
2. **Review Features**: Analyze tcp_window and packet_length patterns
3. **Protocol-Agnostic**: Implement behavioral feature engineering
4. **Target Accuracy**: Aim for 60-75% for realistic behavioral detection
