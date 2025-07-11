# SDN DDoS Dataset Generation Framework

## Overview
This project provides a comprehensive framework for generating labeled DDoS attack datasets in a Software-Defined Networking (SDN) environment. The primary script for this process is `dataset_generation/main.py`, which orchestrates the simulation of both normal network traffic and various DDoS attacks to create realistic datasets for training and evaluating machine learning-based intrusion detection systems. The scenario durations and other parameters are configurable via `dataset_generation/config.json`.

## Key Components

### 1. Network Topology
- Single switch (s1) with six hosts (h1-h6)
- IP range: 10.0.0.1 to 10.0.0.6
- Built using Mininet for network emulation

### 2. Core Components
- **`dataset_generation/main.py`**: The main script orchestrating the dataset generation process.
- **`dataset_generation/config.json`**: Configuration file for scenario durations.
- **Ryu Controller**: Implements SDN control plane functionality, with a REST API for flow monitoring.
- **Attack Modules**: Implements various DDoS attack vectors (located in `dataset_generation/src/attacks/`).
- **Data Collectors**: Captures network traffic (PCAP) and processes it into labeled CSVs, and collects flow statistics from the Ryu controller.

### 3. Supported Attacks
- **Traditional DDoS**:
  - SYN Flood
  - UDP Flood
  - ICMP Flood
- **Advanced Adversarial Attacks**: (Implemented in `gen_advanced_adversarial_ddos_attacks.py`)
  - TCP State Exhaustion
  - Application Layer Attacks
  - Slow Read

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Mininet      │─────│   Ryu SDN      │─────│   Dataset      │
│   Emulation    │     │   Controller   │     │   Generator    │
│                 │     │                 │     │   (main.py)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       │                       │                        │
       │                       │                        │
       ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Network       │     │   Flow          │     │   Labeled      │
│   Traffic       │     │   Statistics    │     │   Datasets     │
│   (PCAP)        │     │   (from Ryu)    │     │   (CSV)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Dataset Outputs

### 1. Raw Packet Captures (`*.pcap` files)
- Individual raw packet capture files for each traffic phase (e.g., `normal.pcap`, `syn_flood.pcap`).

### 2. Labeled Packet Features (`packet_features.csv`)
- Extracted packet features with corresponding labels for each packet, indicating the traffic phase (e.g., `normal`, `syn_flood`, `ad_slow`).

### 3. Labeled Flow Features (`flow_features.csv`)
- A new dataset containing flow-based statistics collected from the Ryu controller, labeled based on the active traffic phase.

## Getting Started

### Prerequisites
- Python 3.x
- Mininet
- Ryu SDN Controller
- Scapy
- `tshark` (from Wireshark)
- `slowhttptest`
- Other dependencies listed in `dataset_generation/requirements.txt`

### Installation
```bash
# Install system-level dependencies (Ubuntu/Debian example)
sudo apt-get update
sudo apt-get install -y mininet ryu-bin python3-pip tshark slowhttptest

# Install Python dependencies
pip install -r dataset_generation/requirements.txt
```

### Running the System
```bash
# Start the dataset generation
sudo python3 dataset_generation/main.py
```

## License
MIT License

## Citation
[Add citation information if applicable]
