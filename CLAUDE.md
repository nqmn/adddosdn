# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the AdDDoSDN Dataset Framework - a comprehensive Python-based framework for generating, capturing, processing, and documenting network traffic datasets in Software-Defined Networking (SDN) environments. The project focuses on adversarial DDoS attacks and detection in SDN networks using Mininet emulation and various SDN controllers (Ryu, ONOS).

## Repository Architecture

The codebase is organized into several key components:

### Core Dataset Generation (`dataset_generation/`)
- **Main Entry Points**: 
  - `main.py` - Primary script for full dataset generation with configurable scenarios
  - `test.py` - Quick testing script with fixed durations
- **Configuration**: `config.json` - Controls traffic scenario durations and flow collection settings
- **Output**: Results saved to `main_output/` or `test_output/` directories
- **Source Code**:
  - `src/attacks/` - Attack implementations (SYN flood, UDP flood, ICMP flood, advanced adversarial)
  - `src/controller/` - Ryu controller application for flow monitoring
  - `src/utils/` - PCAP processing and feature extraction utilities
  - `gen_benign_traffic.py` - Benign traffic generation

### Examples and Development (`examples/`)
- **Mininet Examples** (`examples/mininet/`):
  - Basic topologies and custom network configurations
  - Advanced flow monitoring system in `ryu-flowmonitor/`
  - Multiple controller applications for security monitoring
- **Ryu Examples** (`examples/ryu/`): Controller applications for REST topology and switching
- **ONOS Examples** (`examples/onos/`): Installation and setup instructions

## Common Commands

### Dataset Generation
```bash
# Full dataset generation (requires sudo for Mininet)
sudo python3 dataset_generation/main.py

# Quick test run
sudo python3 dataset_generation/test.py

# Install dependencies
pip install -r dataset_generation/requirements.txt
```

### Development Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r dataset_generation/requirements.txt

# System dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip python3-venv git default-jre tshark slowhttptest
```

### Testing and Quality Assurance
```bash
# Code formatting and linting (if available)
black dataset_generation/
flake8 dataset_generation/
isort dataset_generation/

# Run tests (using pytest)
pytest dataset_generation/
pytest --cov=dataset_generation/
```

### Mininet and SDN Controller Operations
```bash
# Start Ryu controller (basic)
ryu-manager examples/ryu/simple_switch_13.py

# Enhanced flow monitor system
cd examples/mininet/ryu-flowmonitor/
./run_script.sh start
./enhanced_run_script.sh root-start  # For multi-controller setup

# Mininet network cleanup
sudo mn -c

# Start Mininet with custom topology
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13
```

### ONOS Controller Setup
```bash
# Install ONOS (Ubuntu)
sudo apt install openjdk-11-jdk
# Add JAVA_HOME to /etc/environment
sudo mkdir /opt && cd /opt
sudo wget -c https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz
sudo tar -xvf onos-2.7.0.tar.gz && sudo mv onos-2.7.0 onos
sudo /opt/onos/bin/onos-service start
```

## Key Configuration Files

### Dataset Generation Configuration
- `dataset_generation/config.json` - Controls scenario durations and parameters
- `dataset_generation/files/` - Contains label files and feature name definitions

### Attack Scenarios
The framework supports multiple attack types with configurable durations:
- Normal traffic baseline
- SYN flood attacks
- UDP flood attacks  
- ICMP flood attacks
- Advanced adversarial attacks (TCP state exhaustion, application layer mimicry, slow read)

## Development Workflow

1. **Environment Setup**: Create virtual environment and install dependencies
2. **Configuration**: Modify `config.json` for desired scenario parameters
3. **Development**: Work primarily in `dataset_generation/src/` for core functionality
4. **Testing**: Use `test.py` for quick iterations, `main.py` for full runs
5. **Analysis**: Generated datasets include both packet-level and flow-level features
6. **Controller Development**: Use examples in `examples/mininet/ryu-flowmonitor/` for advanced SDN applications

## Network Architecture

The framework operates in SDN environments with:
- **Switches**: OpenFlow-enabled switches (typically OpenVSwitch)
- **Controllers**: Ryu (primary), ONOS (alternative)
- **Topology**: Configurable via Mininet (linear, custom topologies supported)
- **Monitoring**: Flow-level and packet-level data collection
- **Output**: CSV datasets with comprehensive network features

## Security Focus

This framework is designed for **defensive security research only**:
- DDoS detection and mitigation research
- SDN security analysis
- Network traffic analysis and classification
- Adversarial attack detection in SDN environments

The generated datasets and tools are intended for academic research, security testing, and development of defensive mechanisms in SDN networks.