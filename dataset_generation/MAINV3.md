# AdDDoSDN Dataset Generation Framework v3.0
## 30-Feature Real-Time DDoS Detection Dataset

### Overview

Framework v3.0 is designed specifically for **real-time DDoS detection** using an optimal 30-feature set that can be extracted with <1ms latency in production environments. This implementation is completely independent of mainv1 and mainv2, ensuring no conflicts with existing workflows.

### Key Features

- **30-feature extraction engine** optimized for real-time processing
- **Timeline-ordered feature output** for ML training compatibility
- **Independent implementation** (preserves mainv1 & mainv2)
- **CPU affinity optimization** for maximum performance
- **Enhanced adversarial attacks** from mainv2 framework
- **Production-ready feature set** for network security appliances

### 30-Feature Set Specification

#### **Timeline-Ordered CSV Header:**
```csv
timestamp,eth_type,ip_src,ip_dst,ip_proto,ip_ttl,ip_id,ip_flags,ip_len,ip_tos,ip_version,ip_frag_offset,src_port,dst_port,tcp_flags,tcp_seq,tcp_ack,tcp_window,tcp_urgent,udp_sport,udp_dport,udp_len,udp_checksum,icmp_type,icmp_code,icmp_id,icmp_seq,packet_length,transport_protocol,tcp_options_len,Label_multi,Label_binary
```

#### **Feature Categories:**

**🔴 Pure Live Extractable (24 Features) - Zero Calculations**
- **Link Layer (1):** `eth_type`
- **IP Header (10):** `ip_src`, `ip_dst`, `ip_proto`, `ip_ttl`, `ip_id`, `ip_flags`, `ip_len`, `ip_tos`, `ip_version`, `ip_frag_offset`
- **TCP Header (7):** `src_port`, `dst_port`, `tcp_flags`, `tcp_seq`, `tcp_ack`, `tcp_window`, `tcp_urgent`
- **UDP Header (4):** `udp_sport`, `udp_dport`, `udp_len`, `udp_checksum`
- **ICMP Header (4):** `icmp_type`, `icmp_code`, `icmp_id`, `icmp_seq`

**🟡 Minimal Calculation (4 Features) - Simple Operations**
- `timestamp` - Packet capture time
- `packet_length` - Total packet size
- `transport_protocol` - Protocol name (TCP/UDP/ICMP)
- `tcp_options_len` - TCP options length

**🏷️ Labels (2 Features)**
- `Label_multi` - Multi-class labels (0=normal, 1=syn_flood, 2=udp_flood, 3=icmp_flood, 4=ad_syn, 5=ad_udp, 6=ad_slow)
- `Label_binary` - Binary labels (0=normal, 1=attack)

### Architecture

#### **File Structure:**
```
dataset_generation/
├── mainv3.py                    # Main v3.0 framework
├── run_bulk_mainv3.py          # Bulk execution script
├── main_output/v3/             # v3.0 output directory
│   ├── packet_features_30.csv  # 30-feature dataset
│   ├── flow_features.csv       # Flow-level features
│   ├── *.pcap                  # Traffic captures
│   └── *.log                   # Execution logs
└── MAINV3.md                   # This documentation
```

#### **Output Files:**
- **Primary Dataset:** `packet_features_30.csv` - 30-feature packet-level data
- **Flow Dataset:** `flow_features.csv` - Flow-level aggregated data
- **PCAP Files:** Individual attack scenario captures
- **Logs:** `main.log`, `attack.log`, `ryu.log`, `mininet.log`

### Attack Scenarios

#### **Enhanced Traditional Attacks:**
1. **Enhanced SYN Flood** - RFC-compliant TCP options with human-like timing
2. **Enhanced UDP Flood** - Realistic DNS payloads with ephemeral ports
3. **Enhanced ICMP Flood** - Protocol compliance with session patterns

#### **Enhanced Adversarial Attacks:**
1. **TCP State Exhaustion** - Advanced protocol exploitation with burst patterns
2. **Application Layer Attack** - Behavioral pattern generation with IP rotation
3. **Slow Read Attack** - Traffic fingerprint evasion with adaptive control

### Usage Guide

#### **Basic Usage:**
```bash
# Single run with auto-detection
sudo python3 mainv3.py

# Custom configuration file
sudo python3 mainv3.py config.json

# Optimize for specific hardware
sudo python3 mainv3.py --max-cores 16 --cores 12
```

#### **Bulk Execution:**
```bash
# Run multiple iterations
sudo python3 run_bulk_mainv3.py --runs 4

# Custom configuration with bulk runs
sudo python3 run_bulk_mainv3.py --runs 5 --config config.json --cores 8
```

#### **Output Directory Structure:**
```
main_output/v3/
├── DDMMYY-1/              # First run output
├── DDMMYY-2/              # Second run output
├── DDMMYY-3/              # Third run output
└── DDMMYY-4/              # Fourth run output
```

### Performance Optimization

#### **CPU Core Allocation:**
- **Core 0:** System/OS
- **Core 1:** Ryu Controller
- **Cores 2-4:** Mininet Network (3 cores)
- **Cores 5-10:** Attack Generation (6 cores)
- **Core 11:** Background Services
- **Cores 0-15:** PCAP Processing (all cores, post-simulation)

#### **Real-Time Extraction Performance:**
- **Target Latency:** <1ms per packet
- **Processing Rate:** 100K+ packets per second
- **Memory Usage:** <1KB per active analysis
- **CPU Usage:** <5% for sustained traffic

### Feature Extraction Engine

#### **Protocol-Specific Handling:**
```python
def extract_30_features_from_packet(packet, capture_time=None):
    """
    Extract 30 features optimized for real-time DDoS detection.
    Returns timeline-ordered feature dictionary.
    """
    # TCP packets: TCP fields populated, UDP/ICMP fields empty
    # UDP packets: UDP fields populated, TCP/ICMP fields empty  
    # ICMP packets: ICMP fields populated, TCP/UDP fields empty
```

#### **Timeline Compatibility:**
- Features ordered for ML training pipelines
- Timestamp-first ordering for temporal analysis
- Consistent empty value handling across protocols
- Label alignment with attack timelines

### Attack Detection Signatures

#### **Enhanced SYN Flood Detection:**
```python
# Critical Features: tcp_flags, dst_port, packet_length, ip_src
IF tcp_flags == "S" AND dst_port IN [80,443,22] AND packet_length < 80:
    POTENTIAL_SYN_FLOOD = True
```

#### **Enhanced UDP Flood Detection:**
```python
# Critical Features: ip_proto, udp_dport, udp_len, packet_length
IF ip_proto == 17 AND udp_dport IN [53,67,123,161] AND udp_len > 20:
    POTENTIAL_UDP_FLOOD = True
```

#### **Enhanced ICMP Flood Detection:**
```python
# Critical Features: ip_proto, icmp_type, icmp_code, packet_length
IF ip_proto == 1 AND icmp_type == 8 AND packet_length == 44:
    POTENTIAL_ICMP_FLOOD = True
```

### Implementation Benefits

#### **Real-Time Deployment Ready:**
- Direct packet header field access (no complex calculations)
- Minimal computational overhead
- Production network compatibility
- Hardware acceleration support

#### **ML Training Optimized:**
- Consistent feature ordering across datasets
- Timeline-aligned labels for temporal models
- Balanced attack representation
- Missing value standardization

#### **Research Applications:**
- Network security appliance development
- Real-time monitoring system integration
- SDN controller security enhancements
- Edge detection device deployment

### Configuration

#### **Scenario Durations (config.json):**
```json
{
    "scenario_durations": {
        "initialization": 5,
        "normal_traffic": 1200,     # 20 min for balanced dataset
        "syn_flood": 300,           # 5 min
        "udp_flood": 300,           # 5 min
        "icmp_flood": 300,          # 5 min
        "ad_syn": 900,              # 15 min
        "ad_udp": 600,              # 10 min
        "ad_slow": 600,             # 10 min
        "cooldown": 10
    }
}
```

#### **Hardware Requirements:**
- **Minimum:** 8 CPU cores, 16GB RAM
- **Recommended:** 16+ CPU cores, 32GB+ RAM
- **Network:** 1Gbps+ for high-volume testing
- **Storage:** 50GB+ for dataset output

### Integration with Existing Framework

#### **Independence Guarantee:**
- **No modifications** to `main.py` or `mainv2.py`
- **Separate output directory** (`main_output/v3/`)
- **Independent logging** and configuration
- **Parallel execution** with other versions

#### **Compatibility:**
- Uses same underlying infrastructure (Mininet, Ryu, attacks)
- Compatible with existing analysis tools
- Timeline analysis integration
- Dataset summary generation

### Advanced Features

#### **Enhanced Adversarial Techniques:**
- **Statistical Feature Manipulation** - Basic ML evasion
- **TCP State Machine Simulation** - Advanced protocol exploitation
- **Behavioral Pattern Generator** - Enhanced behavioral mimicry
- **Traffic Fingerprint Evasion** - Traffic camouflage enhancement

#### **Quality Assurance:**
- **PCAP integrity validation** before processing
- **Timestamp correction** and normalization
- **Timeline synchronization** verification
- **Attack log correlation** analysis

### Troubleshooting

#### **Common Issues:**
1. **Permission Errors:** Ensure running as root for Mininet
2. **Port Conflicts:** Check if Ryu controller ports are available
3. **Memory Issues:** Increase system memory for large datasets
4. **CPU Affinity:** Verify taskset utility is installed

#### **Performance Tuning:**
1. **Adjust core allocation** based on available hardware
2. **Optimize PCAP processing** worker count
3. **Balance attack durations** for dataset quality
4. **Monitor system resources** during execution

### Expected Output

#### **Dataset Characteristics:**
- **Normal Traffic:** ~150K packets (balanced baseline)
- **Traditional Attacks:** ~100K packets each (SYN/UDP/ICMP floods)
- **Adversarial Attacks:** ~60K packets each (ad_syn/ad_udp/ad_slow)
- **Total Dataset:** ~600K+ packets with 30 features each

#### **Detection Accuracy Targets:**
- **Traditional Enhanced Attacks:** 80-85% accuracy
- **Adversarial Attacks:** 60-70% accuracy
- **Overall Performance:** 75-85% with <1ms latency

### Version History

- **v3.0:** 30-feature real-time optimized extraction engine
- **v2.0:** Enhanced adversarial attacks with CPU affinity
- **v1.0:** Original comprehensive dataset generation framework

---

**Note:** This implementation maintains full independence from previous versions while leveraging proven infrastructure components. The 30-feature set is specifically designed for production deployment in real-time network security applications.