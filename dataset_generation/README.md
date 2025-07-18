# Dataset Generation Module

This module provides the core functionality for generating comprehensive DDoS attack datasets in Software-Defined Networking (SDN) environments. It combines traditional and advanced adversarial attack techniques with enhanced monitoring and feature extraction capabilities.

## 🎯 Overview

The dataset generation framework automates the entire process of creating labeled network traffic datasets with **three synchronized data formats**:

1. **Network Emulation**: Creates realistic SDN environments using Mininet
2. **Traffic Generation**: Simulates both benign and attack traffic patterns
3. **Data Capture**: Records packet-level, SDN flow-level, and aggregated flow data
4. **Feature Extraction**: Computes comprehensive feature sets across all formats
5. **Timeline Integrity**: Ensures conservative data preservation with attack.log validation
6. **Dataset Export**: Produces three synchronized CSV datasets with rich feature sets

## ⚙️ Configuration & Timing

### Current Configuration Issues
The default configuration in `config.json` produces severely imbalanced datasets:
- **Normal traffic**: Only 7,713 packets (6.4 pps) - extremely low baseline
- **Traditional attacks**: 400,000+ packets each (53x more than normal)
- **Adversarial attacks**: 200-2,500 packets (97% fewer than traditional)

### Recommended Balanced Configuration
```json
{
    "scenario_durations": {
        "initialization": 5,
        "normal_traffic": 3600,    // 60 min → ~230K packets (with benign fix)
        "syn_flood": 300,          // 5 min → ~100K packets  
        "udp_flood": 300,          // 5 min → ~100K packets
        "icmp_flood": 300,         // 5 min → ~100K packets
        "ad_syn": 7200,            // 120 min → ~80K packets
        "ad_udp": 4800,            // 80 min → ~60K packets
        "ad_slow": 3600,           // 60 min → ~50K packets
        "cooldown": 5
    }
}
```

### Expected Dataset Sizes
| Configuration | Total Size | Normal Traffic | Traditional Attacks | Adversarial Attacks | Balance Quality |
|---------------|------------|----------------|-------------------|-------------------|-----------------|
| **Current (Default)** | 185M | 1.2M (7K packets) | 66M (1M+ packets) | 404K (3K packets) | ❌ Severely Imbalanced |
| **Recommended** | ~400M | 36M (230K packets) | 17M (300K packets) | 50M (190K packets) | ✅ Well Balanced |

### Performance Improvements
- **Benign traffic generation**: 10x faster packet generation (timing fixes applied)
- **Total runtime**: ~6-6.5 hours for balanced dataset vs 3 hours for imbalanced
- **Storage efficiency**: Traditional attacks reduced 4x, adversarial increased 3x for balance

### Generated Dataset Types

The framework generates **three synchronized data formats** from the same PCAP source:

- **Packet-Level Dataset**: Individual packet features (15 features) - `packet_features.csv`
- **SDN Flow Dataset**: OpenFlow controller statistics (18 features) - `flow_features.csv`
- **CICFlow Dataset**: Bidirectional flow aggregations (78 features) - `cicflow_features_all.csv`
- **PCAP Files**: Raw packet captures for each traffic scenario (`*.pcap`)
- **Attack Logs**: Comprehensive attack execution logs with metrics (`attack.log`)

### Data Format Relationship
- **Packet-to-CICFlow Ratio**: ~5.21 packets per flow (validated across all datasets)
- **Timeline Consistency**: All formats use identical attack.log timeline boundaries
- **Data Integrity**: 98.9% labeling accuracy with conservative unknown label handling

## 🏗️ Architecture

### Core Components

```
src/
├── attacks/                    # Attack implementation modules
│   ├── gen_syn_flood.py       # Enhanced SYN flood with comprehensive logging
│   ├── gen_udp_flood.py       # Enhanced UDP flood with monitoring
│   ├── gen_icmp_flood.py      # Enhanced ICMP flood with statistics
│   ├── enhanced_timing.py     # Human-like timing patterns for traditional attacks
│   ├── protocol_compliance.py # Protocol compliance for realistic behavior
│   ├── gen_advanced_adversarial_ddos_attacks_refactored.py  # Main adversarial attacks
│   ├── ddos_coordinator.py    # Advanced attack coordination and orchestration
│   ├── ip_rotation.py         # IP rotation and evasion techniques
│   ├── packet_crafting.py     # Advanced packet crafting utilities
│   ├── advanced_techniques.py # Sophisticated evasion methods (with burst/jitter)
│   ├── session_management.py  # Session maintenance and handling
│   └── adaptive_control.py    # Adaptive attack rate control
├── controller/                # SDN controller applications
│   └── flow_monitor.py        # Ryu controller for flow statistics collection
└── utils/                     # Utility functions and processing
    ├── enhanced_pcap_processing.py  # PCAP capture and feature extraction
    ├── logger.py              # Centralized logging system with run ID tracking
    └── feature_extraction.py  # Advanced feature computation algorithms
```

### Configuration Files

```
files/
├── Label_binary.txt           # Binary classification labels (Normal=0, Attack=1)
├── Label_multi.txt           # Multi-class labels (Normal, SYN, UDP, ICMP, Adversarial)
├── packet_feature_names.txt  # 15 packet-level feature definitions
└── flow_feature_names.txt    # 18 flow-level feature definitions
```

## 🚀 Usage

### Main Dataset Generation

**Full Dataset Generation:**
```bash
# Use default config.json
sudo python3 main.py

# Use custom configuration file
sudo python3 main.py test_config.json

# Use absolute path to config file
sudo python3 main.py /path/to/custom_config.json
```

- **Duration**: Configurable via `config.json`
- **Output**: `main_output/` directory
- **Features**: Complete feature sets with all attack types
- **Logging**: Comprehensive attack execution logs

**Configuration Example:**
```json
{
  "normal_duration": 60,        # Benign traffic duration (seconds)
  "syn_flood_duration": 30,     # SYN flood attack duration
  "udp_flood_duration": 30,     # UDP flood attack duration  
  "icmp_flood_duration": 30,    # ICMP flood attack duration
  "ad_syn_duration": 20,        # Advanced SYN attack duration
  "ad_udp_duration": 20,        # Advanced UDP attack duration
  "slow_read_duration": 20,     # Slow read attack duration
  "flow_collection_interval": 5 # Flow statistics collection interval
}
```

### Test Dataset Generation

**Quick Test Run:**
```bash
sudo python3 test.py
```

- **Duration**: Fixed short durations (5-10 seconds each)
- **Output**: `test_output/` directory  
- **Purpose**: Rapid prototyping and validation
- **Features**: Same feature sets as main dataset

### Dataset Analysis

**Statistical Analysis:**
```bash
python3 calculate_percentages.py [main_output|test_output]
```

**Output Statistics:**
- Traffic distribution by attack type
- Feature value ranges and distributions
- Dataset completeness and quality metrics
- Label distribution analysis

## 📊 Attack Scenarios

### Traditional DDoS Attacks

#### 1. SYN Flood Attack
- **Method**: TCP SYN packet flooding
- **Target**: Port 80 (HTTP service)
- **Rate**: ~100 packets/second (0.01s interval)
- **Features**: TCP state exhaustion detection

**Enhanced Logging:**
```
[syn_flood] [Run ID: uuid] Starting SYN Flood from h1 to 10.0.0.6 for 30 seconds.
[syn_flood] [Run ID: uuid] Target 10.0.0.6 is reachable (ping: 0.123s)
[syn_flood] [Run ID: uuid] Service 10.0.0.6:80 is active (SYN-ACK: 0.045s)
[syn_flood] [Run ID: uuid] Attack progress: 10.1s elapsed, ~1010 packets sent, Rate: 100.0 pps
[syn_flood] [Run ID: uuid] Total packets sent: 3000, Average rate: 100.00 packets/sec
```

#### 2. UDP Flood Attack
- **Method**: UDP packet flooding
- **Target**: Port 53 (DNS service)
- **Rate**: ~100 packets/second
- **Features**: UDP service disruption patterns

#### 3. ICMP Flood Attack
- **Method**: ICMP Echo Request flooding
- **Target**: Network layer (no specific port)
- **Rate**: ~100 packets/second
- **Features**: Network layer flood detection

### Advanced Adversarial Attacks

#### 1. TCP State Exhaustion (ad_syn)
- **Method**: Advanced SYN attacks with IP rotation
- **Evasion**: Source IP spoofing and rotation
- **Rate**: Variable, adaptive control
- **Features**: Sophisticated TCP manipulation

#### 2. Application Layer Mimicry (ad_udp)
- **Method**: HTTP-based attacks mimicking legitimate traffic
- **Evasion**: Realistic HTTP requests with varied user agents
- **Rate**: Low-frequency, burst patterns
- **Features**: Application layer analysis

#### 3. Slow Read Attack (slow_read)
- **Method**: Slow HTTP attacks using slowhttptest
- **Tool**: External slowhttptest binary
- **Parameters**: 100 connections, 10s intervals, 20 connections/sec
- **Features**: Connection exhaustion detection

### Benign Traffic Generation

**Multi-Protocol Traffic:**
- **HTTP/HTTPS**: Web browsing simulation
- **DNS**: Domain name resolution queries
- **SMTP**: Email traffic simulation  
- **FTP**: File transfer protocol traffic
- **Rate**: Variable, realistic patterns

## 📈 Three Synchronized Data Formats

### Format 1: Packet-Level Features (15 features)
**Granularity**: Individual network packets  
**Source**: Direct PCAP extraction using tshark

**Network Layer Features:**
- Source/Destination IP addresses
- Protocol types and codes
- Packet sizes and fragmentation
- Time-to-Live (TTL) values

**Transport Layer Features:**
- Source/Destination ports
- TCP flags and sequence numbers
- UDP header information
- Connection state indicators

**Temporal Features:**
- Inter-arrival times
- Flow duration and timing
- Packet rate statistics
- Burst detection metrics

**Statistical Features:**
- Packet count aggregations
- Byte count distributions
- Flow size statistics
- Rate-based features

### Format 2: SDN Flow Features (18 features)
**Granularity**: OpenFlow switch flow entries  
**Source**: Ryu controller flow monitoring

**Flow Statistics:**
- Packets per flow (forward/backward)
- Bytes per flow (forward/backward)
- Flow duration and timing
- Flow inter-arrival times

**Rate Features:**
- Packet rate per flow
- Byte rate per flow
- Flow rate metrics
- Burst rate indicators

**Behavioral Features:**
- Port number distributions
- Protocol usage patterns
- Connection patterns
- Service fingerprinting

### Format 3: CICFlow Aggregated Features (78 features)
**Granularity**: Bidirectional network flows  
**Source**: CICFlowMeter processing of PCAP files

**Key Features Include**:
- **Flow Duration & Timing**: Duration, inter-arrival times, idle times
- **Packet & Byte Counts**: Forward/backward packet/byte counts and rates
- **Statistical Measures**: Min, max, mean, std of packet sizes and intervals
- **Protocol Flags**: TCP flags, flow control indicators
- **Behavioral Patterns**: Active/idle periods, subflow analysis

### Data Format Synchronization
All three formats are extracted from the same PCAP source with:
- **Timeline Consistency**: Identical attack.log timeline boundaries
- **Packet-to-CICFlow Ratio**: ~5.21 packets per flow (validated)
- **Conservative Data Integrity**: 98.9% labeling accuracy with edge cases preserved

## 🔍 Monitoring and Logging

### Enhanced Attack Logging

**Run ID Tracking:**
- Unique UUID for each attack execution
- Consistent logging format across all attacks
- Correlation between logs and captured data

**Pre-Attack Reconnaissance:**
- Target reachability testing (ICMP ping)
- Service connectivity validation
- Network path verification
- Response time measurement

**Real-Time Monitoring:**
- Attack progress tracking
- Packet rate measurement
- Process resource monitoring (CPU, memory)
- Network performance metrics

**Comprehensive Summaries:**
- Total packets/requests sent
- Average rates and performance
- Attack duration and timing
- Success/failure indicators

### Logging Format

```
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - [attack_type] [Run ID: uuid] message
```

**Example Log Entries:**
```
2025-07-12 15:19:27,706 - INFO - [udp_flood] [Run ID: 45cd6db3-c6df-4426-9181-ca14106f4f03] Starting UDP Flood from h2 to 10.0.0.4 for 30 seconds.
2025-07-12 15:19:27,706 - INFO - [udp_flood] [Run ID: 45cd6db3-c6df-4426-9181-ca14106f4f03] Attack Phase: Traditional UDP Flood - Attacker: h2, Target: 10.0.0.4:53, Duration: 30s
2025-07-12 15:19:31,797 - WARNING - [udp_flood] [Run ID: 45cd6db3-c6df-4426-9181-ca14106f4f03] UDP service 10.0.0.4:53 no response (time: 4.091s)
```

## 🛠️ Technical Details

### SDN Environment Setup

**Mininet Configuration:**
- Topology: Linear topology with configurable hosts
- Switches: OpenFlow-enabled OpenVSwitch
- Controller: Ryu with custom flow monitoring
- Network: 10.0.0.0/8 address space

**Ryu Controller:**
- REST API for flow statistics
- Real-time flow monitoring
- Packet-in handling for unknown flows
- Flow rule installation and management

### Data Collection Pipeline

1. **Network Initialization**: Mininet topology setup
2. **Controller Startup**: Ryu flow monitoring application
3. **Baseline Collection**: Initial benign traffic generation
4. **Attack Execution**: Sequential attack scenario execution
5. **Data Capture**: Continuous PCAP and flow collection
6. **Feature Extraction**: Multi-threaded feature computation
7. **Dataset Export**: CSV generation with proper labeling

### Performance Optimization

**Multi-threading:**
- Parallel packet processing
- Concurrent feature extraction
- Asynchronous data collection

**Memory Management:**
- Streaming packet processing
- Incremental feature computation
- Efficient data structures

**Scalability:**
- Configurable batch sizes
- Adaptive resource allocation
- Memory-efficient algorithms

## 🧪 Testing and Validation

### Test Scripts

**Unit Testing:**
```bash
# Test individual attack modules
python3 -m pytest src/attacks/test_*.py

# Test feature extraction
python3 -m pytest src/utils/test_*.py
```

**Integration Testing:**
```bash
# Quick end-to-end test
sudo python3 test.py

# Validate generated datasets
python3 validate_dataset.py test_output/
```

### Quality Assurance

**Dataset Validation:**
- Feature completeness checks
- Label consistency verification
- Statistical distribution analysis
- Temporal correlation validation

**Attack Validation:**
- Packet rate verification
- Attack signature confirmation
- Network impact measurement
- Detection algorithm testing

## 🔧 Customization

### Adding New Attacks

1. **Create Attack Module:**
   ```python
   # src/attacks/gen_new_attack.py
   import uuid
   import logging
   
   attack_logger = logging.getLogger('attack_logger')
   
   def run_attack(attacker_host, victim_ip, duration):
       run_id = str(uuid.uuid4())
       attack_logger.info(f"[new_attack] [Run ID: {run_id}] Starting attack...")
       # Implementation here
       return process
   ```

2. **Update Main Scripts:**
   - Add import in `main.py` and `test.py`
   - Add attack execution in traffic generation sequence
   - Update configuration file with new attack duration

3. **Update Labels:**
   - Add new attack type to `files/Label_multi.txt`
   - Update feature extraction to include new labels

### Extending Features

1. **Packet-Level Features:**
   - Modify `src/utils/enhanced_pcap_processing.py`
   - Add feature computation in packet processing loop
   - Update `files/packet_feature_names.txt`

2. **Flow-Level Features:**
   - Modify `src/controller/flow_monitor.py`
   - Add new flow statistics collection
   - Update `files/flow_feature_names.txt`

### Configuration Options

**Network Configuration:**
- Topology size and structure
- Host IP address assignments
- Switch configuration parameters
- Controller connection settings

**Attack Configuration:**
- Attack duration and intensity
- Target selection and rotation
- Rate limiting and adaptive control
- Evasion technique parameters

**Data Collection Configuration:**
- Feature extraction parameters
- PCAP capture filters
- Flow collection intervals
- Output file formats

## 📚 Dependencies

### Core Dependencies
```
scapy>=2.4.5          # Packet crafting and manipulation
mininet>=2.3.0         # Network emulation
ryu>=4.34              # SDN controller framework
pandas>=1.3.0          # Data manipulation and analysis
numpy>=1.21.0          # Numerical computing
tshark>=3.2.0          # Packet analysis (system dependency)
psutil>=5.8.0          # System monitoring
```

### System Dependencies
```bash
# Ubuntu/Debian packages
sudo apt install -y mininet ryu-manager tshark slowhttptest openvswitch-switch
```

## 🐛 Troubleshooting

### Common Issues

**Permission Errors:**
```bash
# Ensure sudo access for Mininet
sudo python3 main.py [config_file]

# Check Mininet installation
sudo mn --test pingall
```

**Network Connectivity:**
```bash
# Clean up previous Mininet sessions
sudo mn -c

# Check controller connectivity
ryu-manager src/controller/flow_monitor.py
```

**PCAP Capture Issues:**
```bash
# Check tcpdump permissions
sudo tcpdump -i any -c 1

# Verify network interfaces
ip link show
```

### Debugging

**Enable Debug Logging:**
```python
# Add to main.py or test.py
logging.getLogger().setLevel(logging.DEBUG)
```

**Network Debugging:**
```bash
# Monitor network traffic during generation
sudo tcpdump -i any host 10.0.0.4

# Check SDN controller logs
tail -f /var/log/ryu/ryu-manager.log
```

## 📖 References

- [Mininet Documentation](http://mininet.org/overview/)
- [Ryu SDN Framework](https://ryu-sdn.org/)
- [OpenFlow Specification](https://opennetworking.org/sdn-definition/)
- [Scapy Packet Manipulation](https://scapy.net/)
- [TShark Network Analysis](https://www.wireshark.org/docs/man-pages/tshark.html)