# SDN DDoS Dataset Generation Framework

## Overview
This project provides a comprehensive framework for generating labeled DDoS attack datasets in a Software-Defined Networking (SDN) environment. It simulates both normal network traffic and various DDoS attacks to create realistic datasets for training and evaluating machine learning-based intrusion detection systems.

## Key Components

### 1. Network Topology
- Single switch (s1) with six hosts (h1-h6)
- IP range: 10.0.0.1 to 10.0.0.6
- Built using Mininet for network emulation

### 2. Core Components
- **Main Orchestrator**: Controls the entire dataset generation process
- **Ryu Controller**: Implements SDN control plane functionality
- **Attack Modules**: Implements various DDoS attack vectors
- **Data Collectors**: Captures network traffic and flow statistics

### 3. Supported Attacks
- **Traditional DDoS**:
  - SYN Flood
  - UDP Flood
  - ICMP Flood
- **Advanced Adversarial Attacks**:
  - TCP State Exhaustion
  - Application Layer Attacks
  - Hybrid Mix Attacks
  - Adaptive Rate Control

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Mininet      │─────│   Ryu SDN      │─────│   Dataset      │
│   Emulation    │     │   Controller   │     │   Generator    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       │                       │                        │
       │                       │                        │
       ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Network       │     │   Flow          │     │   Labeled      │
│   Traffic       │     │   Statistics    │     │   Datasets     │
│   (PCAP)        │     │   (REST API)    │     │   (CSV)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Dataset Outputs

### 1. Packet-Level Features (`packet_features.csv`)
- Raw packet captures with extracted features
- Timestamp, protocol, size, and other packet headers

### 2. Flow Statistics (`ryu_flow_features.csv`)
- Flow-level metrics from OpenFlow
- Source/destination IPs and ports
- Packet/byte counts and duration
- Protocol information

### 3. CICFlow Dataset (`cicflow_dataset.csv`)
- Advanced flow features using CICFlowMeter
- 80+ statistical features per flow
- Suitable for machine learning

## Getting Started

### Prerequisites
- Python 3.x
- Mininet
- Ryu SDN Controller
- Scapy
- Other dependencies in `requirements.txt`

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Mininet and Ryu are installed
sudo apt-get install mininet
pip install ryu
```

### Running the System
```bash
# Start the dataset generation
sudo python3 main.py
```

## Configuration
Edit `config.json` to customize:
- Network topology
- Traffic patterns
- Attack types and parameters
- Data collection settings

## Extending the Framework

### Adding New Attacks
1. Create a new Python file in the `attacks/` directory
2. Implement the `run_attack(attacker_host, victim_ip, duration)` function
3. Update `config.json` to include the new attack

### Modifying Network Topology
Edit `topology.py` to change the network structure or add more hosts/switches.

## License
[Specify License]

## Citation
[Add citation information if applicable]
