# AdDDoSDN Dataset Framework 🛡️

A comprehensive framework for generating network security datasets in Software-Defined Networks (SDN). This tool creates realistic datasets containing both normal traffic and various types of DDoS attacks for cybersecurity research and machine learning.

## 🎯 What Does This Do?

This framework helps researchers and security professionals create datasets for:
- **DDoS Attack Detection**: Training machine learning models to identify attacks
- **Network Security Research**: Studying attack patterns and defense mechanisms  
- **Cybersecurity Education**: Learning about SDN security and attack types
- **Defense System Testing**: Evaluating security tools and detection systems

## 🚀 Quick Start Guide

### Step 1: Setup Your Environment

**System Requirements:**
- Ubuntu Linux (18.04 or newer recommended)
- At least 4GB RAM and 10GB free disk space
- Internet connection for downloading dependencies

**Install Required Software:**
```bash
# Update system
sudo apt update

# Install essential tools
sudo apt install -y python3-pip python3-venv git tshark mininet ryu-manager slowhttptest

# Clone this project
git clone https://github.com/nqmn/AdDDoSSDN_dataset.git
cd AdDDoSSDN_dataset

# Create Python environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r dataset_generation/requirements.txt
```

### Step 2: Run Your First Test

**Quick Test (5 minutes):**
```bash
# Test that everything works (requires sudo for network simulation)
sudo python3 dataset_generation/test.py
```
This creates a small dataset in `dataset_generation/test_output/` with:
- 📊 `packet_features.csv` - Detailed packet data (84 features)
- 📈 `flow_features.csv` - Network flow data (26 features)  
- 📦 `*.pcap` files - Raw network packet captures
- 📝 `attack.log` - Detailed attack information

**Full Dataset Generation (1+ hours):**
```bash
# Generate full research dataset (configurable durations)
sudo python3 dataset_generation/main.py
```
This creates a comprehensive dataset in `dataset_generation/main_output/`

### Step 3: Configure for Your Needs

Edit `dataset_generation/config.json` to customize attack durations:
```json
{
  "scenario_durations": {
    "normal_traffic": 1200,    "← 20 minutes of normal traffic"
    "syn_flood": 600,          "← 10 minutes of SYN flood attack"  
    "udp_flood": 600,          "← 10 minutes of UDP flood attack"
    "icmp_flood": 600,         "← 10 minutes of ICMP flood attack"
    "ad_syn": 600,             "← 10 minutes of advanced TCP attack"
    "ad_udp": 600,             "← 10 minutes of advanced HTTP attack"
    "ad_slow": 600             "← 10 minutes of slow read attack"
  }
}
```

## 📚 Understanding the Framework

### What Gets Generated?

#### 🎭 Traffic Types Created:
1. **Normal Traffic** - Legitimate web browsing, email, file transfers
2. **Traditional DDoS Attacks** - SYN floods, UDP floods, ICMP floods  
3. **Advanced Adversarial Attacks** - Sophisticated attacks that mimic normal traffic

#### 📊 Dataset Outputs:
- **Packet Features (84 columns)** - Individual packet characteristics
- **Flow Features (26 columns)** - Aggregated network flow statistics  
- **Binary Labels** - Normal (0) vs Attack (1)
- **Multi-class Labels** - Specific attack types (normal, syn_flood, udp_flood, etc.)

### How It Works

```
🏗️  Network Setup        🚦 Traffic Generation      📈 Data Collection
   │                        │                          │
   ├─ Virtual Network       ├─ Normal Web Traffic      ├─ Packet Capture  
   ├─ SDN Controller        ├─ SYN Flood Attacks       ├─ Flow Statistics
   ├─ 6 Virtual Hosts       ├─ UDP Flood Attacks       ├─ Performance Logs
   └─ OpenFlow Switch       ├─ ICMP Flood Attacks      └─ Feature Extraction
                            ├─ Advanced TCP Attacks              │
                            ├─ Advanced HTTP Attacks             ▼
                            └─ Slow Read Attacks          📊 CSV Datasets
```

## 🛠️ Two Usage Modes

### 🧪 Development Mode (`test.py`)
**Purpose:** Quick testing and development
- **Duration:** Each attack runs for 5 seconds (45 seconds total)
- **Use Case:** Verify setup, test changes, debug issues
- **Output:** `dataset_generation/test_output/`

### 🏭 Production Mode (`main.py`) 
**Purpose:** Full research dataset generation
- **Duration:** Configurable via `config.json` (default: 80+ minutes)
- **Use Case:** Generate datasets for research, training ML models
- **Output:** `dataset_generation/main_output/`

**Both modes generate identical data formats - only duration differs!**

## 📁 Project Structure

```
📂 adversarial-ddos-attacks-sdn-dataset/
├── 📂 dataset_generation/           ← Main framework
│   ├── 🐍 test.py                  ← Quick test script (5s per attack)
│   ├── 🐍 main.py                  ← Full dataset generation (configurable)
│   ├── ⚙️ config.json              ← Duration settings for main.py
│   ├── 📂 src/                     ← Source code
│   │   ├── 📂 attacks/             ← Attack implementations
│   │   ├── 📂 controller/          ← SDN controller code
│   │   └── 📂 utils/               ← Data processing utilities
│   ├── 📂 test_output/             ← test.py results
│   ├── 📂 main_output/             ← main.py results
│   └── 📂 files/                   ← Configuration files
├── 📂 examples/                    ← Usage examples and tutorials
└── 📄 README.md                    ← This file
```

## 🎯 Generated Dataset Features

### Packet-Level Features (84 features)
- **Network Layer** (12 features): IP addresses, protocols, packet sizes
- **Transport Layer** (15 features): Ports, TCP flags, connection states  
- **Timing** (20 features): Timestamps, arrival patterns, flow duration
- **Statistics** (25 features): Packet counts, distributions, patterns
- **Protocol-Specific** (10 features): HTTP methods, DNS queries, TCP options
- **Labels** (2 features): Binary and multi-class attack labels

### Flow-Level Features (26 features)  
- **SDN Context** (6 features): Switch info, flow rules, OpenFlow data
- **Traffic Metrics** (8 features): Packet/byte counts, rates, duration
- **Network Behavior** (4 features): MAC addresses, communication patterns
- **Advanced Analytics** (6 features): Statistical analysis, anomaly detection
- **Labels** (2 features): Binary and multi-class attack labels

## 🔍 Attack Types Generated

### Traditional DDoS Attacks
| Attack Type | Description | Target Port | Rate |
|-------------|-------------|-------------|------|
| **SYN Flood** | TCP connection exhaustion | 80 (HTTP) | ~100 packets/sec |
| **UDP Flood** | UDP packet flooding | 53 (DNS) | ~100 packets/sec |  
| **ICMP Flood** | ICMP echo request flooding | N/A | ~100 packets/sec |

### Advanced Adversarial Attacks
| Attack Type | Description | Technique | Evasion Method |
|-------------|-------------|-----------|----------------|
| **TCP State Exhaustion** | Advanced SYN-based attack | Half-open connections | IP rotation, timing variation |
| **Application Layer Mimicry** | HTTP-based attack | Legitimate-looking requests | User agent rotation, realistic patterns |
| **Slow Read Attack** | Low-and-slow HTTP attack | Slow data consumption | Connection holding, slowhttptest |

## ⚠️ Important Notes

### Network Simulation
- Uses Mininet to create virtual networks
- Simulates real SDN environment with OpenFlow
- No actual network traffic leaves your computer
- Safe for educational and research use

### System Impact
- Requires sudo access for network simulation
- May temporarily use network resources
- Automatically cleans up after completion
- Safe shutdown with Ctrl+C

**This framework is for DEFENSIVE security research only!**

## 📖 Citation

If you use this framework in research, please cite:
```bibtex
@misc{addosdn2024,
  title={AdDDoSDN: A Novel Adversarial DDoS Attack Dataset for SDN Environments},
  author={[Mohd Adil, Mokti]},
  year={2025},
  url={https://github.com/nqmn/AdDDoSSDN_dataset}
}
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.