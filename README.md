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
│   ├── main_output/            # Output directory for main.py
│   ├── test_output/            # Output directory for test.py
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
│   ├── main.py                 # Primary dataset generation script
│   ├── test.py                 # Quick testing script
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

2. **Generate full dataset**
   ```bash
   # Requires sudo for Mininet
   sudo python3 dataset_generation/main.py
   ```
   - Outputs saved to `dataset_generation/main_output/`
   - Includes: `packet_features.csv`, `flow_features.csv`, `*.pcap` files, `attack.log`

3. **Quick test run**
   ```bash
   # Shorter test with fixed durations
   sudo python3 dataset_generation/test.py
   ```
   - Outputs saved to `dataset_generation/test_output/`

### Advanced Usage

**Custom Attack Configuration:**
```bash
# Modify config.json for custom durations
{
  "normal_duration": 30,
  "syn_flood_duration": 15,
  "udp_flood_duration": 15,
  "icmp_flood_duration": 15,
  "ad_syn_duration": 10,
  "ad_udp_duration": 10,
  "slow_read_duration": 10,
  "flow_collection_interval": 5
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

## 📊 Generated Datasets

### Packet-Level Features
- **Network Layer**: IP addresses, protocols, packet sizes, TTL
- **Transport Layer**: Port numbers, TCP flags, sequence numbers
- **Timing Features**: Inter-arrival times, flow duration
- **Statistical Features**: Packet counts, byte counts, flow statistics

### Flow-Level Features
- **Flow Statistics**: Packets per flow, bytes per flow, flow duration
- **Rate Features**: Packet rate, byte rate, flow rate
- **Behavioral Features**: Port distributions, protocol distributions
- **Temporal Features**: Flow start/end times, inter-flow times

### Attack Labels
- **Binary Classification**: Normal (0) vs Attack (1)
- **Multi-class Classification**: Normal, SYN Flood, UDP Flood, ICMP Flood, Adversarial attacks

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

## 🏗️ Architecture

### SDN Environment
- **Network Emulation**: Mininet with OpenFlow switches
- **Controller**: Ryu with custom flow monitoring applications
- **Topology**: Configurable network topologies
- **Traffic Generation**: Scapy-based packet crafting and injection

### Data Pipeline
1. **Network Setup**: Mininet topology creation
2. **Controller Start**: Ryu flow monitoring application
3. **Traffic Generation**: Benign and attack traffic simulation
4. **Packet Capture**: tcpdump-based PCAP generation
5. **Feature Extraction**: Multi-level feature computation
6. **Dataset Export**: CSV format with comprehensive labeling

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