# AdDDoSDN Dataset Framework

A comprehensive Python-based framework for generating, capturing, processing, and documenting network traffic datasets in Software-Defined Networking (SDN) environments. This framework specializes in creating datasets that include both traditional DDoS attacks and advanced adversarial attacks for security research and machine learning applications.

## 🚀 Features

### Attack Vectors
- **Traditional DDoS Attacks**: SYN Flood, UDP Flood, ICMP Flood with enhanced comprehensive logging
- **Advanced Adversarial Attacks**: TCP State Exhaustion, Application Layer Mimicry, Slow Read attacks
- **Benign Traffic Generation**: Multi-protocol normal traffic simulation (HTTP, HTTPS, DNS, SMTP, FTP)

### SDN Integration
- **Native SDN Support**: OpenFlow/SDN environments via Ryu controller
- **REST API Integration**: Flow monitoring and statistics collection
- **Multiple Controller Support**: Ryu (primary), ONOS (alternative)
- **Flexible Topologies**: Linear, custom topologies via Mininet

### Dataset Output
- **Rich Feature Sets**: Both packet-level and flow-level feature datasets
- **Comprehensive Labeling**: Binary and multi-class labels for all traffic types
- **PCAP Capture**: Full packet captures for deep analysis
- **Statistical Analysis**: Built-in dataset statistics and analysis tools

### Enhanced Logging & Monitoring
- **Run ID Tracking**: Unique identifiers for each attack execution
- **Real-time Monitoring**: Attack progress, packet rates, process statistics
- **Pre-attack Reconnaissance**: Target reachability and service testing
- **Comprehensive Summaries**: Detailed attack statistics and performance metrics

### Configuration & Extensibility
- **Configurable Scenarios**: Easy parameter adjustment via `config.json`
- **Modular Architecture**: Cleanly separated attack modules, controller logic, and utilities
- **Extensible Design**: Easy addition of new attack types and monitoring capabilities

## 📦 Repository Structure

```
.
├── dataset_generation/          # Main dataset generation module
│   ├── main_output/            # Output directory for main.py (production)
│   ├── test_output/            # Output directory for test.py (testing)
│   ├── src/                    # Source code
│   │   ├── attacks/            # Attack implementations
│   │   │   ├── gen_syn_flood.py          # Enhanced SYN flood attack
│   │   │   ├── gen_udp_flood.py          # Enhanced UDP flood attack
│   │   │   ├── gen_icmp_flood.py         # Enhanced ICMP flood attack
│   │   │   ├── gen_advanced_adversarial_ddos_attacks_refactored.py
│   │   │   ├── ddos_coordinator.py       # Advanced attack coordination
│   │   │   ├── ip_rotation.py            # IP rotation techniques
│   │   │   ├── packet_crafting.py        # Advanced packet crafting
│   │   │   ├── advanced_techniques.py    # Evasion techniques
│   │   │   ├── session_management.py     # Session handling
│   │   │   └── adaptive_control.py       # Adaptive attack control
│   │   ├── controller/         # Ryu controller applications
│   │   │   └── flow_monitor.py           # Enhanced flow monitoring
│   │   └── utils/              # Utility functions
│   │       ├── enhanced_pcap_processing.py  # PCAP capture & processing
│   │       ├── logger.py                    # Centralized logging system
│   │       └── feature_extraction.py       # Feature extraction utilities
│   ├── files/                  # Configuration and label files
│   │   ├── Label_binary.txt    # Binary classification labels
│   │   ├── Label_multi.txt     # Multi-class classification labels
│   │   ├── packet_feature_names.txt  # Packet-level feature definitions
│   │   └── flow_feature_names.txt    # Flow-level feature definitions
│   ├── config.json             # Traffic scenario configuration
│   ├── main.py                 # Production dataset generation (uses config.json)
│   ├── test.py                 # Testing script (fixed 5s durations)
│   ├── gen_benign_traffic.py   # Benign traffic generation
│   ├── calculate_percentages.py # Dataset statistics analysis
│   └── requirements.txt        # Python dependencies
├── examples/                   # Example implementations and tutorials
│   ├── mininet/               # Mininet examples and configurations
│   │   └── ryu-flowmonitor/   # Advanced flow monitoring examples
│   ├── ryu/                   # Ryu controller examples
│   └── onos/                  # ONOS controller setup and examples
├── CLAUDE.md                  # Project instructions and guidelines
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites

**System Requirements:**
- Ubuntu 18.04+ (recommended) or compatible Linux distribution
- Python 3.7+
- Sudo access (required for Mininet)

**Core Dependencies:**
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-venv git default-jre tshark slowhttptest

# Install Mininet (if not already installed)
sudo apt install -y mininet

# Install Ryu SDN controller
sudo apt install -y ryu-manager
# OR install via pip: pip install ryu
```

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/nqmn/AdDDoSSDN-novel_adversarial_ddos_sdn_dataset.git
   cd AdDDoSSDN-novel_adversarial_ddos_sdn_dataset
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r dataset_generation/requirements.txt
   ```

4. **Verify installation**
   ```bash
   # Test Mininet installation
   sudo mn --test pingall

   # Test Ryu installation
   ryu-manager --version
   ```

## 🚀 Quick Start

### Basic Usage

1. **Configure traffic scenarios (optional)**
   ```bash
   # Edit configuration file to adjust attack durations
   nano dataset_generation/config.json
   ```

2. **Generate full dataset (production)**
   ```bash
   # Requires sudo for Mininet
   sudo python3 dataset_generation/main.py
   ```
   - Uses configurable durations from `config.json`
   - Outputs saved to `dataset_generation/main_output/`
   - Includes: `packet_features.csv`, `flow_features.csv`, `*.pcap` files, `attack.log`

3. **Quick test run (development)**
   ```bash
   # Same functionality but with fixed short durations (5s each)
   sudo python3 dataset_generation/test.py
   ```
   - Uses hardcoded short durations for quick testing
   - Outputs saved to `dataset_generation/test_output/`
   - Same features and format as main.py

### Advanced Usage

**Custom Attack Configuration:**
```bash
# Modify config.json for custom durations (affects main.py only)
{
  "scenario_durations": {
    "initialization": 5,
    "normal_traffic": 1200,
    "syn_flood": 600,
    "udp_flood": 600,
    "icmp_flood": 600,
    "ad_syn": 600,
    "ad_udp": 600,
    "ad_slow": 600,
    "cooldown": 10
  },
  "flow_collection_retry_delay": 5
}
```

**Dataset Analysis:**
```bash
# Generate dataset statistics
python3 dataset_generation/calculate_percentages.py main_output

# Analyze PCAP files
tcpdump -r dataset_generation/main_output/syn_flood.pcap
tshark -r dataset_generation/main_output/syn_flood.pcap -q -z io,stat,1
```

## 📊 Dataset Generation Flow

### Traffic Generation Timeline

#### test.py (Fixed Durations - Development)
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        test.py Traffic Generation Timeline                       │
└─────────────────────────────────────────────────────────────────────────────────┘

Time: 0s    5s    10s    15s    20s    25s    30s    35s    40s    45s
      │     │     │      │      │      │      │      │      │      │
      ▼     ▼     ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│Init │Normal│SYN │UDP │ICMP │ad_syn│ad_udp│slow │Cool │     │
│ 5s  │ 5s  │ 5s │ 5s │ 5s  │ 5s  │ 5s  │ 5s  │ 5s  │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

#### main.py (Configurable Durations - Production)
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        main.py Traffic Generation Timeline                       │
│                           (Default config.json values)                          │
└─────────────────────────────────────────────────────────────────────────────────┘

Time: 0s    5s     20m    30m    40m    50m    60m    70m    80m    90m
      │     │      │      │      │      │      │      │      │      │
      ▼     ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌─────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────┐
│Init │Normal│ SYN  │ UDP  │ ICMP │ad_syn│ad_udp│slow  │Cool │
│ 5s  │1200s │ 600s │ 600s │ 600s │ 600s │ 600s │ 600s │ 10s │
└─────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────┘
```

**Both scripts provide identical functionality and output format:**

**Timeline Legend:**
- **Init**: Network initialization and stabilization  
- **Normal**: Benign multi-protocol traffic (HTTP, DNS, SMTP, FTP)
- **SYN/UDP/ICMP**: Traditional DDoS flood attacks with enhanced logging
- **ad_syn/ad_udp/slow**: Advanced adversarial attacks with evasion techniques
- **Cool**: Cooldown period for flow collection completion
- **Flow Collection**: Continuous SDN controller statistics via REST API

**Key Differences:**
- **test.py**: Fixed 5-second durations per phase (50 seconds total)
- **main.py**: Configurable durations via config.json (default: ~80 minutes total)
- **Output**: Both generate identical file formats and feature sets
```

### Feature Extraction Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Feature Extraction Workflow                           │
└─────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │          Raw Data Sources           │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┼───────────────────┐
                    │                 │                   │
           ┌────────▼──────────┐     │      ┌────────────▼─────────┐
           │ PCAP Files        │     │      │ Flow Statistics     │
           │                   │     │      │ (REST API)          │
           │ • normal.pcap     │     │      │                     │
           │ • syn_flood.pcap  │     │      │ • Real-time polling │
           │ • udp_flood.pcap  │     │      │ • Switch flow tables│
           │ • icmp_flood.pcap │     │      │ • OpenFlow metrics  │
           │ • ad_syn.pcap     │     │      │ • Performance data  │
           │ • ad_udp.pcap     │     │      │                     │
           │ • ad_slow.pcap    │     │      │                     │
           └────────┬──────────┘     │      └────────────┬─────────┘
                    │                │                   │
                    ▼                │                   ▼
           ┌────────────────────┐    │      ┌─────────────────────────┐
           │ Packet Processing  │    │      │ Flow Processing         │
           │                    │    │      │                         │
           │ 1. Integrity Check │    │      │ 1. Real-time Collection │
           │ 2. Timestamp Fix   │    │      │ 2. Time Synchronization │
           │ 3. Protocol Parse  │    │      │ 3. Metric Calculation   │
           │ 4. Feature Extract │    │      │ 4. Label Assignment     │
           │ 5. Label Assign    │    │      │ 5. Quality Validation   │
           └────────┬───────────┘    │      └─────────────┬───────────┘
                    │                │                    │
                    ▼                │                    ▼
        ┌─────────────────────────┐  │     ┌──────────────────────────┐
        │ 84 Packet-Level         │  │     │ 26 Flow-Level            │
        │ Features                │  │     │ Features                 │
        │                         │  │     │                          │
        │ • Network Layer (12)    │  │     │ • Flow Identity (6)      │
        │ • Transport Layer (15)  │  │     │ • Traffic Metrics (8)    │
        │ • Temporal (20)         │  │     │ • Rate Features (6)      │
        │ • Statistical (25)      │  │     │ • Behavioral (4)         │
        │ • Protocol Specific (10)│  │     │ • Labels (2)             │
        │ • Labels (2)            │  │     │                          │
        └─────────┬───────────────┘  │     └──────────────┬───────────┘
                  │                  │                    │
                  └──────────────────┼────────────────────┘
                                     │
                                     ▼
                   ┌─────────────────────────────────────┐
                   │        Dataset Consolidation        │
                   │                                     │
                   │ ┌─────────────────────────────────┐ │
                   │ │ Quality Assurance               │ │
                   │ │ • Label consistency checks      │ │
                   │ │ • Feature completeness          │ │
                   │ │ • Statistical validation        │ │
                   │ │ • Temporal correlation          │ │
                   │ └─────────────────────────────────┘ │
                   │                                     │
                   │ ┌─────────────────────────────────┐ │
                   │ │ Final Dataset Export            │ │
                   │ │ • packet_features.csv           │ │
                   │ │ • flow_features.csv             │ │
                   │ │ • Feature name files            │ │
                   │ │ • Statistical summaries         │ │
                   │ └─────────────────────────────────┘ │
                   └─────────────────────────────────────┘
```

### Enhanced Logging Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Enhanced Logging System Architecture                      │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │   Centralized       │
                              │   Logging Manager   │
                              │                     │
                              │ • Run ID Generation │
                              │ • Format Standards  │
                              │ • Multi-destination │
                              │ • Level Control     │
                              └──────────┬──────────┘
                                         │
                ┌────────────────────────┼────────────────────────┐
                │                        │                        │
                ▼                        ▼                        ▼
    ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
    │ Attack Execution    │  │ System Operations   │  │ Network Monitoring  │
    │ Logging             │  │ Logging             │  │ Logging             │
    │                     │  │                     │  │                     │
    │ Files:              │  │ Files:              │  │ Files:              │
    │ • attack.log        │  │ • main.log/test.log │  │ • ryu.log           │
    │                     │  │ • mininet.log       │  │ • flow_stats.log    │
    │ Content:            │  │                     │  │                     │
    │ • Run ID tracking   │  │ Content:            │  │ Content:            │
    │ • Pre-attack recon  │  │ • System startup    │  │ • Controller events │
    │ • Real-time metrics │  │ • Process mgmt      │  │ • Flow installations│
    │ • Progress updates  │  │ • Error handling    │  │ • Network topology  │
    │ • Performance stats │  │ • Resource usage    │  │ • Performance data  │
    │ • Attack summaries  │  │ • Cleanup ops       │  │ • REST API calls    │
    └─────────────────────┘  └─────────────────────┘  └─────────────────────┘
                │                        │                        │
                └────────────────────────┼────────────────────────┘
                                         │
                                         ▼
                          ┌─────────────────────────────┐
                          │   Log Analysis & Debugging  │
                          │                             │
                          │ • Cross-reference capability│
                          │ • Correlation by Run ID     │
                          │ • Performance profiling     │
                          │ • Error traceability        │
                          │ • Attack pattern analysis   │
                          └─────────────────────────────┘

Enhanced Logging Format:
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - [component] [Run ID: uuid] message

Example Entries:
2025-07-12 15:19:27,706 - INFO - [syn_flood] [Run ID: a1b2c3d4-e5f6] Starting SYN Flood...
2025-07-12 15:19:27,800 - DEBUG - [syn_flood] [Run ID: a1b2c3d4-e5f6] Target reachable (0.123s)
2025-07-12 15:19:30,450 - INFO - [syn_flood] [Run ID: a1b2c3d4-e5f6] Progress: 500 packets sent
```

## 📊 Generated Datasets

### Packet-Level Features (84 features)

#### **Network Layer Features (12 features)**
- **Addressing**: `ip_src`, `ip_dst` - Source/destination IP identification
- **Protocol**: `ip_proto`, `eth_type` - Protocol classification and analysis
- **Size Metrics**: `packet_length`, `ip_len` - Packet size characteristics
- **Header Analysis**: `ip_ttl`, `ip_id`, `ip_flags` - Network behavior indicators

#### **Transport Layer Features (15 features)**
- **Port Analysis**: `src_port`, `dst_port` - Application service identification
- **TCP State**: `tcp_flags`, `tcp_seq`, `tcp_ack` - Connection state tracking
- **UDP Metrics**: `udp_len`, `udp_checksum` - UDP-specific characteristics

#### **Temporal Features (20 features)**
- **Timing**: `timestamp`, `inter_arrival_time` - Temporal pattern analysis
- **Flow Duration**: `flow_start`, `flow_end` - Connection lifecycle
- **Rate Analysis**: `packet_rate`, `burst_detection` - Traffic intensity patterns

#### **Statistical Features (25 features)**
- **Aggregations**: `packet_count`, `byte_count` - Volume measurements
- **Distributions**: `port_entropy`, `protocol_distribution` - Behavioral analysis
- **Pattern Detection**: `flow_symmetry`, `connection_patterns` - Traffic characteristics

#### **Protocol-Specific Features (10 features)**
- **TCP Analysis**: `tcp_window`, `tcp_options` - TCP behavior indicators
- **HTTP Detection**: `http_method`, `user_agent` - Application layer analysis
- **DNS Analysis**: `dns_query_type`, `dns_response` - DNS traffic characteristics

### Flow-Level Features (26 features)

#### **Flow Identity Features (6 features)**
- **SDN Context**: `switch_id`, `table_id`, `cookie` - OpenFlow identification
- **Network Path**: `in_port`, `out_port` - Traffic routing analysis
- **Priority**: `flow_priority` - Rule matching hierarchy

#### **Traffic Metrics (8 features)**
- **Volume**: `packet_count`, `byte_count` - Direct measurements
- **Duration**: `duration_sec`, `duration_nsec` - Flow lifetime precision
- **Rates**: `packet_rate`, `byte_rate` - Performance indicators

#### **Behavioral Features (4 features)**
- **Addressing**: `eth_src`, `eth_dst` - MAC address patterns
- **Flow Patterns**: `bidirectional_analysis` - Communication characteristics
- **Service Classification**: `port_service_mapping` - Application identification

#### **Advanced Analytics (6 features)**
- **Statistical**: `avg_packet_size`, `flow_efficiency` - Derived metrics
- **Anomaly Detection**: `rate_variance`, `burst_characteristics` - Pattern analysis
- **Correlation**: `inter_flow_timing` - Relationship analysis

### Multi-Level Classification System

#### **Binary Classification**
```
┌─────────────────────────────────────────────────────────┐
│                Binary Classification                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Normal Traffic (Label = 0)    │  Attack Traffic (Label = 1)  │
│  ├─ Benign HTTP/HTTPS         │  ├─ Traditional DDoS          │
│  ├─ DNS Queries               │  │  ├─ SYN Flood              │
│  ├─ SMTP/FTP Traffic          │  │  ├─ UDP Flood              │
│  ├─ SSH/Telnet Sessions       │  │  └─ ICMP Flood             │
│  └─ Standard Network Ops      │  └─ Adversarial Attacks       │
│                                │     ├─ TCP State Exhaustion   │
│                                │     ├─ App Layer Mimicry      │
│                                │     └─ Slow Read Attacks      │
└─────────────────────────────────────────────────────────┘
```

#### **Multi-Class Classification**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Multi-Class Attack Classification                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  normal        syn_flood       udp_flood       icmp_flood                      │
│  │             │               │               │                               │
│  ├─Multi-proto ├─TCP port 80   ├─UDP port 53   ├─ICMP echo                    │
│  │ benign      │ connection    │ DNS service   │ requests                      │
│  │ traffic     │ exhaustion    │ overwhelming  │ bandwidth                     │
│  │ patterns    │ ~100 pps      │ ~100 pps      │ consumption                   │
│  │             │               │               │ ~100 pps                      │
│                                                                                 │
│  ad_syn         ad_udp          ad_slow                                        │
│  │              │               │                                               │
│  ├─Advanced     ├─HTTP app      ├─Slow read                                    │
│  │ TCP state    │ layer         │ connection                                   │
│  │ exhaustion   │ mimicry       │ exhaustion                                   │
│  │ IP rotation  │ legitimate    │ slowhttptest                                 │
│  │ adaptive     │ patterns      │ 100 conns                                    │
│  │ timing       │ varied UA     │ slow consume                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔬 Attack Scenarios

### Traditional DDoS Attacks
- **SYN Flood**: TCP connection exhaustion attacks
- **UDP Flood**: UDP packet flooding targeting DNS services
- **ICMP Flood**: ICMP echo request flooding

### Advanced Adversarial Attacks
- **TCP State Exhaustion**: Sophisticated SYN-based attacks with IP rotation
- **Application Layer Mimicry**: HTTP-based attacks mimicking legitimate traffic
- **Slow Read Attacks**: Low-and-slow HTTP attacks using slowhttptest

### Enhanced Logging Features
All attacks now include:
- Unique run ID tracking
- Pre-attack target reconnaissance
- Real-time progress monitoring
- Comprehensive attack summaries
- Process performance metrics

## 🏗️ System Architecture

### Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AdDDoSDN Dataset Framework                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │   Control Plane │    │    Data Plane    │    │    Management Plane        │ │
│  │                 │    │                  │    │                             │ │
│  │ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────────────────┐ │ │
│  │ │ Ryu         │ │    │ │ Mininet      │ │    │ │ Dataset Generation      │ │ │
│  │ │ Controller  │◄┼────┼─┤ Network      │ │    │ │ Framework               │ │ │
│  │ │             │ │    │ │ Emulation    │ │    │ │                         │ │ │
│  │ │ - Flow Mon  │ │    │ │              │ │    │ │ - Traffic Orchestration │ │ │
│  │ │ - REST API  │ │    │ │ ┌──────────┐ │ │    │ │ - Attack Coordination   │ │ │
│  │ │ - Stats     │ │    │ │ │ OVS      │ │ │    │ │ - Data Collection       │ │ │
│  │ └─────────────┘ │    │ │ │ Switch   │ │ │    │ │ - Feature Extraction    │ │ │
│  └─────────────────┘    │ │ │ (OpenFlow│ │ │    │ │ - Enhanced Logging      │ │ │
│                         │ │ │  1.3)    │ │ │    │ └─────────────────────────┘ │ │
│                         │ │ └────┬─────┘ │ │    └─────────────────────────────┘ │
│                         │ │      │       │ │                                    │
│                         │ │ ┌────▼─────┐ │ │                                    │
│                         │ │ │ Hosts    │ │ │                                    │
│                         │ │ │ h1...h6  │ │ │                                    │
│                         │ │ └──────────┘ │ │                                    │
│                         │ └──────────────┘ │                                    │
│                         └──────────────────┘                                    │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              Attack Generation Layer                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│ │ Traditional     │  │ Adversarial     │  │ Benign Traffic                   │ │
│ │ DDoS Attacks    │  │ Attacks         │  │ Generation                       │ │
│ │                 │  │                 │  │                                  │ │
│ │ • SYN Flood     │  │ • TCP State     │  │ • HTTP/HTTPS                     │ │
│ │ • UDP Flood     │  │   Exhaustion    │  │ • DNS Queries                    │ │
│ │ • ICMP Flood    │  │ • App Layer     │  │ • SMTP/FTP                       │ │
│ │                 │  │   Mimicry       │  │ • SSH/Telnet                     │ │
│ │ Enhanced with:  │  │ • Slow Read     │  │                                  │ │
│ │ • Run ID Track  │  │                 │  │ Multi-protocol                   │ │
│ │ • Real-time Mon │  │ Advanced with:  │  │ Realistic Patterns               │ │
│ │ • Target Recon  │  │ • IP Rotation   │  │                                  │ │
│ │ • Process Stats │  │ • Adaptive Rate │  │                                  │ │
│ └─────────────────┘  │ • Evasion Tech  │  │                                  │ │
│                      └─────────────────┘  └──────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Network Topology Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Ryu Controller              │
                    │                                     │
                    │  ┌─────────────┐ ┌─────────────────┐│
                    │  │ Flow        │ │ REST API        ││
                    │  │ Monitor     │ │ (Port 8080)     ││
                    │  │ App         │ │                 ││
                    │  └─────────────┘ └─────────────────┘│
                    │         │ OpenFlow (Port 6653)      │
                    └─────────┼─────────────────────────────┘
                              │
                              ▼
               ┌──────────────────────────────────────────┐
               │           OpenVSwitch (s1)               │
               │          OpenFlow 1.3 Enabled           │
               └─┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┘
                 │  │  │  │  │  │  │  │  │  │  │  │  │
        ┌────────▼┐ │  │  │  │  │  │  │  │  │  │  │  │
        │   h1    │ │  │  │  │  │  │  │  │  │  │  │  │
        │10.0.0.1 │ │  │  │  │  │  │  │  │  │  │  │  │
        │         │ │  │  │  │  │  │  │  │  │  │  │  │
        │ Attack  │ │  │  │  │  │  │  │  │  │  │  │  │
        │ Source  │ │  │  │  │  │  │  │  │  │  │  │  │
        └─────────┘ │  │  │  │  │  │  │  │  │  │  │  │
                    │  │  │  │  │  │  │  │  │  │  │  │
           ┌────────▼┐ │  │  │  │  │  │  │  │  │  │  │
           │   h2    │ │  │  │  │  │  │  │  │  │  │  │
           │10.0.0.2 │ │  │  │  │  │  │  │  │  │  │  │
           │         │ │  │  │  │  │  │  │  │  │  │  │
           │ Attack  │ │  │  │  │  │  │  │  │  │  │  │
           │ Source  │ │  │  │  │  │  │  │  │  │  │  │
           └─────────┘ │  │  │  │  │  │  │  │  │  │  │
                       │  │  │  │  │  │  │  │  │  │  │
              ┌────────▼┐ │  │  │  │  │  │  │  │  │  │
              │   h3    │ │  │  │  │  │  │  │  │  │  │
              │10.0.0.3 │ │  │  │  │  │  │  │  │  │  │
              │         │ │  │  │  │  │  │  │  │  │  │
              │ Benign  │ │  │  │  │  │  │  │  │  │  │
              │ Traffic │ │  │  │  │  │  │  │  │  │  │
              └─────────┘ │  │  │  │  │  │  │  │  │  │
                          │  │  │  │  │  │  │  │  │  │
                 ┌────────▼┐ │  │  │  │  │  │  │  │  │
                 │   h4    │ │  │  │  │  │  │  │  │  │
                 │10.0.0.4 │ │  │  │  │  │  │  │  │  │
                 │         │ │  │  │  │  │  │  │  │  │
                 │ Attack  │ │  │  │  │  │  │  │  │  │
                 │ Target  │ │  │  │  │  │  │  │  │  │
                 └─────────┘ │  │  │  │  │  │  │  │  │
                             │  │  │  │  │  │  │  │  │
                    ┌────────▼┐ │  │  │  │  │  │  │  │
                    │   h5    │ │  │  │  │  │  │  │  │
                    │10.0.0.5 │ │  │  │  │  │  │  │  │
                    │         │ │  │  │  │  │  │  │  │
                    │ Benign  │ │  │  │  │  │  │  │  │
                    │ Traffic │ │  │  │  │  │  │  │  │
                    └─────────┘ │  │  │  │  │  │  │  │
                                │  │  │  │  │  │  │  │
                       ┌────────▼┐ │  │  │  │  │  │  │
                       │   h6    │ │  │  │  │  │  │  │
                       │10.0.0.6 │ │  │  │  │  │  │  │
                       │         │ │  │  │  │  │  │  │
                       │ Attack  │ │  │  │  │  │  │  │
                       │ Target  │ │  │  │  │  │  │  │
                       └─────────┘ │  │  │  │  │  │  │
                                   └──▼──▼──▼──▼──▼──┘
                                   Additional ports for
                                   traffic monitoring
```

### Data Collection and Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Dataset Generation Pipeline                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Network   │    │   Traffic   │    │    Data     │    │   Dataset   │
│   Setup     │───▶│ Generation  │───▶│ Collection  │───▶│  Processing │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Cleanup  │    │ 1. Normal   │    │ 1. PCAP     │    │ 1. Feature  │
│ 2. Controller│    │    Traffic  │    │    Capture  │    │   Extraction│
│ 3. Mininet  │    │ 2. SYN      │    │ 2. Flow     │    │ 2. Label    │
│ 4. Topology │    │    Flood    │    │    Stats    │    │   Assignment│
│ 5. Connectivity│  │ 3. UDP      │    │ 3. Enhanced │    │ 3. Quality  │
│              │    │    Flood    │    │    Logging  │    │   Validation│
│              │    │ 4. ICMP     │    │ 4. Real-time│    │ 4. CSV      │
│              │    │    Flood    │    │    Monitor  │    │   Export    │
│              │    │ 5. Advanced │    │             │    │             │
│              │    │    Attacks  │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

       ┌─────────────────────────────────────────────────────────────┐
       │                    Concurrent Processes                      │
       └─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PCAP      │    │    Flow     │    │  Enhanced   │
│  Capture    │    │ Statistics  │    │  Logging    │
│  (tcpdump)  │    │ Collection  │    │  System     │
│             │    │ (REST API)  │    │             │
│ • Per-phase │    │ • Real-time │    │ • Run IDs   │
│   isolation │    │   polling   │    │ • Progress  │
│ • Timestamp │    │ • Flow      │    │   tracking  │
│   sync      │    │   persistence│   │ • Target    │
│ • Quality   │    │ • Performance│   │   recon     │
│   checks    │    │   metrics   │    │ • Stats     │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Attack Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Attack Execution Workflow                            │
└─────────────────────────────────────────────────────────────────────────────────┘

                               ┌─────────────────┐
                               │  Attack Start   │
                               └─────────┬───────┘
                                        │
                               ┌─────────▼───────┐
                               │ Generate Run ID │
                               │ (UUID)          │
                               └─────────┬───────┘
                                        │
                               ┌─────────▼───────┐
                               │ Pre-Attack      │
                               │ Reconnaissance  │
                               │                 │
                               │ • ICMP Ping     │
                               │ • Service Test  │
                               │ • Connectivity  │
                               └─────────┬───────┘
                                        │
                               ┌─────────▼───────┐
                               │ Attack Phase    │
                               │ Identification  │
                               │                 │
                               │ • Log attack    │
                               │   type & target │
                               │ • Record params │
                               └─────────┬───────┘
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
               ┌────────▼─────────┐    │    ┌─────────▼────────┐
               │ Traditional      │    │    │ Adversarial      │
               │ DDoS Attacks     │    │    │ Attacks          │
               │                  │    │    │                  │
               │ • SYN Flood      │    │    │ • TCP State      │
               │ • UDP Flood      │    │    │   Exhaustion     │
               │ • ICMP Flood     │    │    │ • App Layer      │
               │                  │    │    │   Mimicry        │
               │ Enhanced with:   │    │    │ • Slow Read      │
               │ • Real-time      │    │    │                  │
               │   monitoring     │    │    │ Advanced with:   │
               │ • Process stats  │    │    │ • IP Rotation    │
               │ • Progress track │    │    │ • Adaptive Rate  │
               └────────┬─────────┘    │    │ • Evasion Tech   │
                        │              │    └─────────┬────────┘
                        │              │              │
                        └──────────────┼──────────────┘
                                       │
                               ┌───────▼───────┐
                               │ Real-time     │
                               │ Monitoring    │
                               │               │
                               │ • Packet rate │
                               │ • CPU/Memory  │
                               │ • Network     │
                               │   response    │
                               │ • Progress    │
                               │   updates     │
                               └───────┬───────┘
                                       │
                               ┌───────▼───────┐
                               │ Attack        │
                               │ Termination   │
                               │               │
                               │ • Graceful    │
                               │   shutdown    │
                               │ • Process     │
                               │   cleanup     │
                               └───────┬───────┘
                                       │
                               ┌───────▼───────┐
                               │ Comprehensive │
                               │ Summary       │
                               │               │
                               │ • Total stats │
                               │ • Performance │
                               │ • Duration    │
                               │ • Success     │
                               │   metrics     │
                               └───────────────┘
```

## 🔧 Development

### Adding New Attacks
1. Create attack module in `dataset_generation/src/attacks/`
2. Implement `run_attack(attacker_host, victim_ip, duration)` function
3. Add comprehensive logging with run ID tracking
4. Update main script to include new attack
5. Add appropriate labels to label files

### Extending Features
1. Modify feature extraction in `dataset_generation/src/utils/`
2. Update feature name files in `dataset_generation/files/`
3. Ensure backward compatibility with existing datasets

### Custom Controllers
1. Add controller applications to `examples/ryu/` or `examples/onos/`
2. Update flow monitoring logic as needed
3. Modify data collection intervals and metrics

## 📚 Examples and Tutorials

See the `examples/` directory for:
- **Mininet Examples**: Custom topologies and network configurations
- **Ryu Examples**: Controller applications and REST API usage
- **ONOS Examples**: Setup instructions and configuration
- **Advanced Monitoring**: Multi-controller setups and enhanced monitoring

## 🤝 Contributing

We welcome contributions! Please see our guidelines:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code style**: Use existing patterns and comprehensive logging
4. **Add tests**: Ensure new features work with both `main.py` and `test.py`
5. **Update documentation**: Keep README and CLAUDE.md current
6. **Submit pull request**: Include detailed description of changes

### Development Guidelines
- Maintain defensive security focus
- Add comprehensive logging to all new features
- Follow existing code patterns and structure
- Test with both traditional and adversarial attacks
- Ensure compatibility with SDN environments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📖 Citation

If you use this framework in your research, please cite our work:

```bibtex
@misc{addosdn2024,
  title={AdDDoSDN: Advanced Adversarial DDoS Attack Dataset for SDN Environments},
  author={[Your Name]},
  year={2024},
  url={https://github.com/nqmn/AdDDoSSDN-novel_adversarial_ddos_sdn_dataset}
}
```

## 🆘 Support

- **Documentation**: Check `CLAUDE.md` for detailed project guidelines
- **Issues**: Report bugs and request features via GitHub Issues
- **Examples**: See `examples/` directory for usage patterns
- **Logs**: Check `attack.log` and console output for debugging

## 🔒 Security Notice

This framework is designed for **defensive security research only**. The generated datasets and attack implementations are intended for:
- Academic research and education
- Security system testing and validation
- DDoS detection and mitigation development
- Network security analysis and classification

Please use responsibly and in accordance with applicable laws and regulations.