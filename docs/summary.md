# SDN DDoS Dataset Generation Framework

## Overview
This project provides a comprehensive framework for generating labeled DDoS attack datasets in a Software-Defined Networking (SDN) environment. The primary script for this process is `dataset_generation/test.py`, which orchestrates the simulation of both normal network traffic and various DDoS attacks to create realistic datasets for training and evaluating machine learning-based intrusion detection systems.

## Key Components

### 1. Network Topology
- Single switch (s1) with six hosts (h1-h6)
- IP range: 10.0.0.1 to 10.0.0.6
- Built using Mininet for network emulation

### 2. Core Components
- **`dataset_generation/test.py`**: The main script orchestrating the dataset generation process.
- **Ryu Controller**: Implements SDN control plane functionality.
- **Attack Modules**: Implements various DDoS attack vectors (located in `dataset_generation/src/attacks/`).
- **Data Collectors**: Captures network traffic (PCAP) and processes it into labeled CSVs.

### 3. Supported Attacks
- **Traditional DDoS**:
  - SYN Flood
  - UDP Flood
  - ICMP Flood
- **Advanced Adversarial Attacks**:
  - TCP State Exhaustion
  - Application Layer Attacks
  - Multi-vector Attacks

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Mininet      │─────│   Ryu SDN      │─────│   Dataset      │
│   Emulation    │     │   Controller   │     │   Generator    │
│                 │     │                 │     │   (test.py)    │
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

### 1. Raw Packet Capture (`capture.pcap`)
- Raw packet captures of all network traffic generated during the scenario.

### 2. Labeled Packet Features (`labeled_packet_features.csv`)
- Extracted packet features with corresponding labels for each packet, indicating the traffic phase (e.g., `normal`, `syn_flood`, `ad_syn`).

## Getting Started

### Prerequisites
- Python 3.x
- Mininet
- Ryu SDN Controller
- Scapy
- Other dependencies listed in `dataset_generation/requirements.txt`

### Installation
```bash
# Install dependencies
pip install -r dataset_generation/requirements.txt

# Ensure Mininet and Ryu are installed (refer to their official documentation)
```

### Running the System
```bash
# Start the dataset generation
sudo python3 dataset_generation/test.py
```

## License
[Specify License]

## Citation
[Add citation information if applicable]
