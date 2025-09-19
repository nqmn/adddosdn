# Dataset Generation Test Framework

This document outlines the usage, logic, and expected outputs of the `test.py` script, which orchestrates the generation of a comprehensive DDoS attack dataset within a Software-Defined Networking (SDN) environment. The test framework provides a quick validation environment with enhanced logging and monitoring capabilities.

## 🎯 Overview

The `test.py` script provides a streamlined dataset generation environment with:

- **Balanced Class Durations**: Optimized timing with 5s minimum duration for practical testing
- **Same Functionality**: Identical feature extraction, logging, and output format as main.py
- **Quick Testing**: Total execution time ~15 minutes (balanced vs ~80 minutes for main.py)
- **Development Focus**: Ideal for balanced dataset testing, ML model validation, and development

### Key Differences from main.py
- **Optimized Durations**: Balanced timing with 5s minimum enforced (vs configurable durations in main.py)
- **Quick Execution**: ~15 minutes total (vs ~80 minutes for main.py default config)
- **Same Features**: Identical 84 packet-level and 26 flow-level features
- **Output Directory**: Results saved to `test_output/` instead of `main_output/`

## 🛠️ Prerequisites

To run this script, ensure you have the following installed on an Ubuntu system:

### Core Dependencies
- **Python 3.7+**: Main scripting environment
- **Mininet**: Network emulator for rapid SDN prototyping
- **Ryu**: SDN controller framework with REST API support
- **TShark**: Network protocol analyzer (part of Wireshark)
- **Slowhttptest**: Tool for slow HTTP attack testing

### Installation Commands
```bash
# System dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv git default-jre tshark slowhttptest mininet ryu-manager

# Python dependencies
pip3 install -r requirements.txt
```

### Permission Requirements
- **Root access**: Required for Mininet network emulation
- **Network privileges**: Needed for packet capture and network interface manipulation

## 🚀 How to Run

### Basic Execution
```bash
sudo python3 test.py
```

### Environment Verification
```bash
# Verify Mininet installation
sudo mn --test pingall

# Check Ryu installation
ryu-manager --version

# Test TShark permissions
sudo tshark -i any -c 1

# Verify slowhttptest
slowhttptest --help
```

## 📊 Script Logic and Flow

### 1. Environment Setup and Initialization

#### **Cleanup and Preparation**
- **Previous Session Cleanup**: Clears any existing Mininet instances (`sudo mn -c`)
- **Tool Verification**: Validates presence of all required command-line tools
- **Output Directory**: Creates `test_output/` directory for all generated files
- **Logging Setup**: Initializes comprehensive logging system with multiple log files

#### **SDN Controller Initialization**
- **Ryu Controller Startup**: Launches Ryu SDN controller with custom flow monitoring
  ```bash
  ryu-manager src/controller/flow_monitor.py --observe-links
  ```
- **Controller Health Check**: Verifies controller is running on port 6653
- **REST API Validation**: Tests `/hello` endpoint for API responsiveness
- **Flow Table Initialization**: Prepares flow monitoring and statistics collection

#### **Network Topology Creation**
- **Mininet Network**: Creates custom topology with 1 OpenFlow switch + 6 hosts
  ```
  Topology: h1--h2--h3--[s1]--h4--h5--h6
  Controller: Remote Ryu controller (127.0.0.1:6653)
  Switch: OpenVSwitch with OpenFlow 1.3
  Network: 10.0.0.0/8 address space
  ```
- **Connectivity Verification**: Executes `pingAll` to confirm basic network connectivity
- **Interface Setup**: Configures network interfaces and routing

### 2. Enhanced Traffic Generation Scenario

The script orchestrates a comprehensive multi-phase traffic generation process with enhanced monitoring:

#### **Phase 1: Initialization (5 seconds)**
- **Purpose**: System stabilization and baseline establishment
- **Activities**: Network settling, controller synchronization
- **Monitoring**: Initial flow table state capture

#### **Phase 2: Normal Traffic Generation (50 seconds)**
- **PCAP Output**: `test_output/normal.pcap`
- **Traffic Types**: Same multi-protocol benign traffic as main.py
  - **ICMP**: Echo requests between h3 ↔ h5
  - **TCP**: HTTP, HTTPS, SSH, Telnet, FTP connections
  - **UDP**: DNS queries, general UDP communication
- **Duration**: 50 seconds → ~300 packets (6.3 pps observed rate)
- **Features**: Identical feature extraction as main.py

#### **Phase 3.1: Traditional DDoS Attacks (15 seconds total)**

| Attack Type | Source | Target | Port | Duration | Expected Packets | main.py Equivalent |
|-------------|--------|--------|------|----------|------------------|--------------------|
| **SYN Flood** | h1 | h6 (10.0.0.6) | 80 | 5s | ~1,188 (237.6 pps) | 600s (10min) |
| **UDP Flood** | h2 | h4 (10.0.0.4) | 53 | 5s | ~380 (76.1 pps) | 600s (10min) |
| **ICMP Flood** | h2 | h4 (10.0.0.4) | N/A | 5s | ~440 (87.9 pps) | 600s (10min) |

**Same Attack Implementation**: Uses identical attack scripts and logging as main.py

**Enhanced Traditional Attack Logging Example:**
```
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Starting SYN Flood from h1 to 10.0.0.6 for 5 seconds.
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Attack Phase: Traditional SYN Flood - Attacker: h1, Target: 10.0.0.6:80, Duration: 5s
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Target 10.0.0.6 is reachable (ping: 0.123s)
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Service 10.0.0.6:80 is active (SYN-ACK: 0.045s)
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Attack progress: 2.5s elapsed, ~250 packets sent, Rate: 100.0 pps
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] --- Attack Summary ---
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Total packets sent: 500
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Average rate: 100.00 packets/sec
[syn_flood] [Run ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890] Attack method: TCP SYN Flood
```

#### **Phase 3.2: Advanced Adversarial Attacks (830 seconds total)**

| Attack Type | Source | Target | Method | Duration | Expected Packets | main.py Equivalent |
|-------------|--------|--------|--------|----------|------------------|--------------------|
| **TCP State Exhaustion (ad_syn)** | h2 | h6 (10.0.0.6) | Advanced SYN | 625s | ~100 (0.16 pps) | 600s (10min) |
| **Application Layer Mimicry (ad_udp)** | h2 | h6 (10.0.0.6) | HTTP-based | 200s | ~100 (0.50 pps) | 600s (10min) |
| **Slow Read Attack (ad_slow)** | h2 | h6 (10.0.0.6) | slowhttptest | 5s | ~244 (48.8 pps) | 600s (10min) |

**Same Attack Implementation**: Uses identical adversarial attack scripts as main.py

**Advanced Attack Configuration:**
- **TCP State Exhaustion**: Sophisticated SYN attacks with source IP spoofing
- **Application Layer**: HTTP requests mimicking legitimate traffic patterns
- **Slow Read**: `slowhttptest -c 100 -H -i 10 -r 20 -l 5 -u http://10.0.0.6:80/ -t SR`

#### **Phase 4: Cooldown and Data Collection (5 seconds)**
- **Network Stabilization**: Allows lingering flows to complete
- **Flow Table Cleanup**: Captures final flow statistics
- **Duration**: 5 seconds (unchanged)
- **Same Processing**: Identical data collection and CSV generation as main.py

### 3. Enhanced Data Collection and Processing

#### **Real-time Flow Statistics Collection**
- **Concurrent Collection**: Separate thread continuously polls Ryu REST API
- **Endpoint**: `GET /flows/{switch_id}` every 1 second
- **Data Capture**: Real-time flow table statistics and metrics
- **Enhanced Features**: Flow duration, packet rates, byte counts, pattern analysis

#### **Advanced PCAP Processing Pipeline**
For each generated PCAP file:

1. **Integrity Verification**: `verify_pcap_integrity()` ensures valid packet capture
2. **Timestamp Validation**: `validate_and_fix_pcap_timestamps()` corrects timing issues
3. **Feature Extraction**: `enhanced_process_pcap_to_csv()` computes 84 packet-level features
4. **Label Assignment**: Time-based labeling with attack type classification
5. **Quality Assurance**: `verify_labels_in_csv()` validates label consistency

#### **Dataset Consolidation**
- **Packet-Level**: All temporary CSVs merged into `packet_features.csv`
- **Flow-Level**: Real-time collection saved to `flow_features.csv`
- **Feature Names**: Descriptive headers saved to corresponding `.txt` files

### 4. Enhanced Monitoring and Logging

#### **Multi-Level Logging System**
- **Main Script**: `test.log` - Overall execution flow and system events
- **Attack Logging**: `attack.log` - Comprehensive attack execution details
- **Controller**: `ryu.log` - SDN controller operations and flow management
- **Network**: `mininet.log` - Network emulation and connectivity logs

#### **Run ID Tracking**
- **Unique Identifiers**: Each attack execution gets a UUID for correlation
- **Cross-Reference**: Links attack logs with captured data and performance metrics
- **Debugging**: Enables precise tracking of individual attack instances

#### **Real-time Monitoring Features**
- **Target Reconnaissance**: Pre-attack connectivity and service testing
- **Progress Tracking**: Real-time packet rates, timing, and performance metrics
- **Resource Monitoring**: CPU, memory usage of attack processes
- **Network Analysis**: Response times, connectivity status, service availability

### 5. Graceful Cleanup and Termination

#### **Process Management**
- **Controller Shutdown**: Graceful termination of Ryu controller
- **Network Cleanup**: Complete Mininet network teardown (`sudo mn -c`)
- **Resource Release**: Proper cleanup of network interfaces and processes
- **Data Integrity**: Ensures all data collection is complete before cleanup

## 📂 Expected Output Structure

Upon successful execution, the `test_output/` directory contains:

### **Log Files**
```
test_output/
├── test.log                    # Main script execution logs
├── attack.log                  # Enhanced attack execution details with run IDs
├── ryu.log                     # SDN controller operations and flow management
└── mininet.log                 # Network emulation and connectivity logs
```

### **Raw Traffic Captures (PCAP Files)**
```
test_output/
├── normal.pcap                 # Baseline benign traffic capture
├── syn_flood.pcap             # SYN flood attack traffic
├── udp_flood.pcap             # UDP flood attack traffic
├── icmp_flood.pcap            # ICMP flood attack traffic
├── ad_syn.pcap                # Advanced TCP state exhaustion
├── ad_udp.pcap                # Application layer mimicry attack
└── ad_slow.pcap               # Slow read attack traffic
```

### **Processed Datasets**
```
test_output/
├── packet_features.csv        # 84-feature packet-level dataset
├── flow_features.csv          # 26-feature flow-level dataset
├── packet_feature_names.txt   # Packet-level feature descriptions
└── flow_feature_names.txt     # Flow-level feature descriptions
```

## 📊 Enhanced Feature Engineering

### **Packet-Level Features (84 features)**

#### **Network Layer Features**
| Feature Category | Features | Description |
|------------------|----------|-------------|
| **Addressing** | `ip_src`, `ip_dst` | Source/destination IP addresses |
| **Protocol** | `ip_proto`, `eth_type` | IP protocol numbers and Ethernet types |
| **Size Metrics** | `packet_length`, `ip_len` | Packet and IP layer sizes |
| **Header Fields** | `ip_ttl`, `ip_id`, `ip_flags` | IP header analysis fields |

#### **Transport Layer Features**
| Feature Category | Features | Description |
|------------------|----------|-------------|
| **Port Analysis** | `src_port`, `dst_port` | Application service identification |
| **TCP State** | `tcp_flags`, `tcp_seq`, `tcp_ack` | Connection state and sequence analysis |
| **UDP Metrics** | `udp_len`, `udp_checksum` | UDP-specific characteristics |

#### **Temporal and Statistical Features**
| Feature Category | Features | Description |
|------------------|----------|-------------|
| **Timing** | `timestamp`, `inter_arrival_time` | Temporal pattern analysis |
| **Flow Stats** | `flow_duration`, `packet_count`, `byte_count` | Flow aggregation metrics |
| **Rate Features** | `packet_rate`, `byte_rate` | Traffic intensity indicators |

### **Flow-Level Features (26 features)**

#### **OpenFlow Statistics**
| Feature Category | Features | Description |
|------------------|----------|-------------|
| **Flow Identity** | `switch_id`, `table_id`, `cookie` | Flow table identification |
| **Matching** | `priority`, `in_port`, `out_port` | Flow matching criteria |
| **Addressing** | `eth_src`, `eth_dst` | MAC address flow patterns |

#### **Traffic Metrics**
| Feature Category | Features | Description |
|------------------|----------|-------------|
| **Volume** | `packet_count`, `byte_count` | Direct traffic measurements |
| **Duration** | `duration_sec`, `duration_nsec` | Flow lifetime analysis |
| **Calculated** | `avg_pkt_size`, `pkt_rate`, `byte_rate` | Derived performance metrics |

## 🏷️ Enhanced Labeling System

### **Multi-Level Classification**

#### **Binary Classification**
- **Label_binary**: `0` (Normal) / `1` (Attack)
- **Purpose**: Basic anomaly detection and binary classification tasks
- **Coverage**: All traffic types with simple attack/normal distinction

#### **Multi-Class Classification**
- **Labels**: `normal`, `syn_flood`, `udp_flood`, `icmp_flood`, `ad_syn`, `ad_udp`, `ad_slow`
- **Purpose**: Detailed attack type identification and classification
- **Granularity**: Specific attack method recognition and analysis

### **Time-Based Labeling Process**

#### **Packet-Level Labeling**
1. **Phase Isolation**: Each PCAP corresponds to a specific traffic phase
2. **Timestamp Baseline**: Reliable timestamp establishment using `validate_and_fix_pcap_timestamps`
3. **Label Timeline**: Phase-specific timelines for accurate label assignment
4. **Precision Matching**: Exact timestamp-to-label mapping for each packet

#### **Flow-Level Labeling**
1. **Continuous Collection**: Real-time flow statistics during entire scenario
2. **Comprehensive Timeline**: Single timeline spanning all traffic phases
3. **Robust Matching**: Epsilon-based time matching for controller delays
4. **Flow Persistence**: Accounts for lingering flow entries in switch tables

### **Label Verification and Quality Assurance**
- **Consistency Checks**: `verify_labels_in_csv()` validates label integrity
- **Distribution Analysis**: Ensures balanced representation across attack types
- **Temporal Validation**: Verifies correct time-based label assignment
- **Cross-Reference**: Correlates packet and flow labels for consistency

## 🔍 Enhanced Attack Analysis

### **Traditional DDoS Attack Characteristics**

#### **SYN Flood Analysis**
- **Attack Vector**: TCP connection exhaustion
- **Packet Rate**: ~100 packets/second (0.01s interval)
- **Target**: Port 80 (HTTP service)
- **Detection Features**: High SYN-to-ACK ratio, incomplete connections

#### **UDP Flood Analysis**
- **Attack Vector**: UDP service overwhelm
- **Packet Rate**: ~100 packets/second
- **Target**: Port 53 (DNS service)
- **Detection Features**: High UDP packet volume, service response degradation

#### **ICMP Flood Analysis**
- **Attack Vector**: Network layer bandwidth consumption
- **Packet Rate**: ~100 packets/second
- **Target**: Network layer (no specific port)
- **Detection Features**: High ICMP echo request volume

### **Advanced Adversarial Attack Characteristics**

#### **TCP State Exhaustion (ad_syn)**
- **Sophistication**: IP rotation, adaptive timing
- **Evasion**: Source address spoofing, burst patterns
- **Detection Challenge**: Low-rate, distributed appearance

#### **Application Layer Mimicry (ad_udp)**
- **Sophistication**: Legitimate HTTP request patterns
- **Evasion**: Varied user agents, realistic payloads
- **Detection Challenge**: Application-layer analysis required

#### **Slow Read Attack (ad_slow)**
- **Sophistication**: Connection resource exhaustion
- **Evasion**: Slow data consumption, long-lived connections
- **Detection Challenge**: Requires connection state monitoring

## 🛠️ Troubleshooting and Debugging

### **Common Issues and Solutions**

#### **Permission Errors**
```bash
# Ensure proper sudo access
sudo python3 test.py

# Check Mininet permissions
sudo mn --test pingall
```

#### **Network Connectivity Issues**
```bash
# Clean previous sessions
sudo mn -c

# Verify controller connectivity
telnet 127.0.0.1 6653
```

#### **PCAP Capture Problems**
```bash
# Check tcpdump permissions
sudo tcpdump -i any -c 1

# Verify network interfaces
ip link show
```

#### **Controller Issues**
```bash
# Check Ryu installation
ryu-manager --version

# Test REST API
curl http://127.0.0.1:8080/hello
```

### **Debug Mode Execution**
```bash
# Enable debug logging
export PYTHONPATH=$PYTHONPATH:src
sudo python3 test.py --debug

# Monitor network traffic during execution
sudo tcpdump -i any host 10.0.0.4 &
sudo python3 test.py
```

### **Log Analysis**
```bash
# Monitor attack execution in real-time
tail -f test_output/attack.log

# Analyze network controller logs
grep "flow" test_output/ryu.log

# Check for errors
grep -i error test_output/*.log
```

## 📈 Performance Analysis

### **Expected Execution Time**
- **Total Duration**: ~15 minutes (vs ~80 minutes for main.py)
- **Initialization**: ~10 seconds
- **Traffic Generation**: ~900 seconds (optimized phase durations with 5s minimum)
  - Normal: 50s, Traditional attacks: 15s, Adversarial attacks: 830s, Cooldown: 5s
- **Data Processing**: ~10-20 seconds
- **Cleanup**: ~5 seconds

### **Comparison with main.py**
- **test.py**: 15 minutes total, optimized durations with 5s minimum enforced
- **main.py**: ~80 minutes total, 10min per attack phase (default config)
- **Same Output**: Both generate identical feature sets and file formats

### **Resource Requirements**
- **CPU**: Moderate usage during packet generation and processing
- **Memory**: ~500MB-1GB for Mininet and data processing
- **Disk**: ~50-100MB for PCAP files and CSV datasets
- **Network**: Local loopback interfaces only

### **Output Size Expectations**
- **PCAP Files**: Optimized with 5s minimum duration enforced
  - SYN flood: ~500KB per file (very high packet rate, 5s duration ~1,188 packets)
  - UDP/ICMP floods: ~50-100KB per file (moderate-high packet rate, 5s duration ~380-440 packets)
  - Adversarial SYN/UDP: ~10-20KB per file (very low packet rate, long duration ~100 packets)
  - Adversarial Slow: ~80KB per file (moderate packet rate, 5s duration ~244 packets)
  - Normal traffic: ~60KB (low packet rate, 50s duration ~300 packets)
- **CSV Datasets**: ~2,500 total rows with variable class sizes due to rate differences
- **Log Files**: 1-10MB total logging output

## 🔒 Security and Safety

### **Defensive Research Focus**
- **Purpose**: Security research and detection algorithm development
- **Scope**: Controlled, isolated network environment
- **Applications**: DDoS detection, SDN security analysis, ML model training

### **Ethical Usage**
- **Environment**: Local network emulation only
- **Impact**: No external network effects
- **Compliance**: Designed for academic and defensive security research

### **Safety Measures**
- **Isolation**: All attacks contained within Mininet environment
- **Cleanup**: Automatic resource cleanup and network teardown
- **Monitoring**: Comprehensive logging for audit and analysis

This enhanced test framework provides a comprehensive, quick-turnaround environment for developing and validating DDoS detection systems in SDN environments, with detailed logging and monitoring capabilities that support both traditional and advanced adversarial attack analysis.