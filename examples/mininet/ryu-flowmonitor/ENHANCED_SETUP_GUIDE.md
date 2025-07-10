# Enhanced Ryu Flow Monitor with DDoS Detection Setup Guide

This comprehensive guide covers the setup and deployment of the Enhanced Ryu Flow Monitor system with ML-based DDoS detection, federated learning, and multi-controller support.

## System Architecture

### Overview
The Enhanced Ryu Flow Monitor implements a distributed SDN security system with:

```
┌─────────────────┐    ┌─────────────────┐
│   Ryu Server    │    │ Mininet Server  │
│  (Root Ctrl)    │◄──►│ (Client Ctrl)   │
│ 192.168.1.100   │    │ 192.168.1.101   │
│                 │    │                 │
│ - Federated     │    │ - Switch-level  │
│   Learning      │    │   Detection     │
│ - Global Model  │    │ - Local ML      │
│ - Threat Intel  │    │ - CICFlowMeter  │
│ - Port 8080     │    │ - Port 8081     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Web Interface  │    │   SDN Network   │
│ - DDoS Monitor  │    │ - OpenFlow      │
│ - ML Metrics    │    │ - Switches      │
│ - Mitigation    │    │ - Traffic       │
└─────────────────┘    └─────────────────┘
```

### Key Features
- **Real-time DDoS Detection**: ML-based anomaly detection
- **Federated Learning**: Distributed model training
- **CICFlowMeter Integration**: Advanced traffic analysis
- **Automated Mitigation**: Immediate threat response
- **Multi-Controller Support**: Scalable architecture
- **Comprehensive Logging**: Detailed attack analysis

## Prerequisites

### System Requirements
- **Ryu Server**: Ubuntu 20.04+, 4GB RAM, Python 3.8+
- **Mininet Server**: Ubuntu 20.04+, 8GB RAM, Python 3.8+
- **Network**: Gigabit connection between servers
- **Storage**: 50GB+ for traffic captures and logs

### Software Dependencies

#### Both Servers
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install tcpdump wireshark-common libpcap-dev -y
```

#### Python Packages
```bash
# Create virtual environment
python3 -m venv ddos_env
source ddos_env/bin/activate

# Install core packages
pip install ryu webob eventlet

# Install ML packages
pip install scikit-learn pandas numpy torch

# Install network analysis
pip install scapy psutil

# Install CICFlowMeter
pip install cicflowmeter
```

#### Mininet Server Only
```bash
# Install Mininet
sudo apt install mininet -y

# Install Open vSwitch
sudo apt install openvswitch-switch -y
```

## Installation

### 1. Clone and Setup

#### On Both Servers
```bash
# Clone the repository
git clone <repository-url>
cd adversarial-ddos-attacks-sdn-dataset/mininet/ryu-flowmonitor

# Make scripts executable
chmod +x *.sh *.py

# Create necessary directories
mkdir -p traffic_captures logs models
```

### 2. Configure Network

#### Ryu Server (192.168.1.100)
```bash
# Configure firewall
sudo ufw allow 8080/tcp  # REST API
sudo ufw allow 9999/tcp  # Federated Learning
sudo ufw allow 6633/tcp  # OpenFlow

# Test connectivity
ping 192.168.1.101
```

#### Mininet Server (192.168.1.101)
```bash
# Configure firewall
sudo ufw allow 8081/tcp  # REST API
sudo ufw allow 6634/tcp  # OpenFlow

# Test connectivity
ping 192.168.1.100
```

## Deployment

### 1. Start Root Controller (Ryu Server)

```bash
# Activate environment
source ddos_env/bin/activate

# Start root controller
python3 flow_monitor_controller.py \
    --controller-id root_controller \
    --is-root true \
    --wsapi-port 8080 \
    --ofp-tcp-listen-port 6633 \
    --verbose

# Alternative: Use ryu-manager
ryu-manager flow_monitor_controller.py \
    --wsapi-port 8080 \
    --ofp-tcp-listen-port 6633 \
    --observe-links \
    --verbose
```

### 2. Start Client Controller (Mininet Server)

```bash
# Activate environment
source ddos_env/bin/activate

# Start client controller
python3 mininet_client_controller.py \
    --controller-id mininet_client_1 \
    --root-address 192.168.1.100:9999 \
    --wsapi-port 8081 \
    --ofp-tcp-listen-port 6634 \
    --verbose
```

### 3. Start Mininet Network

```bash
# On Mininet Server
sudo mn --topo linear,5 \
    --controller remote,ip=127.0.0.1,port=6634 \
    --switch ovsk,protocols=OpenFlow13 \
    --link tc,bw=100

# In Mininet CLI
mininet> pingall
mininet> iperf h1 h5
```

### 4. Access Web Interface

Open browser and navigate to:
- **Root Controller**: http://192.168.1.100:8080/flow_monitor.html
- **Client Controller**: http://192.168.1.101:8081/flow_monitor.html

## Configuration

### Controller Configuration

#### Root Controller Settings
```python
# In flow_monitor_controller.py
CONTROLLER_CONFIG = {
    'controller_id': 'root_controller',
    'is_root': True,
    'federated_port': 9999,
    'detection_threshold': 0.7,
    'training_interval': 300,  # 5 minutes
    'aggregation_interval': 600  # 10 minutes
}
```

#### Client Controller Settings
```python
# In mininet_client_controller.py
CLIENT_CONFIG = {
    'controller_id': 'mininet_client_1',
    'is_root': False,
    'root_address': '192.168.1.100:9999',
    'detection_threshold': 0.8,  # Higher for immediate action
    'sync_interval': 300  # 5 minutes
}
```

### CICFlowMeter Configuration

```bash
# Configure capture interface
export CICFLOW_INTERFACE="any"
export CICFLOW_DURATION=300  # 5 minutes
export CICFLOW_OUTPUT_DIR="./traffic_captures"

# Test CICFlowMeter
cicflowmeter -f test.pcap -c test_flows.csv
```

## Testing DDoS Detection

### 1. Generate Normal Traffic

```bash
# In Mininet CLI
mininet> h1 ping h5
mininet> iperf h1 h2
mininet> h3 wget -O /dev/null http://h4/
```

### 2. Simulate DDoS Attacks

#### TCP SYN Flood
```bash
# On host h1
mininet> h1 hping3 -S -p 80 --flood h5
```

#### UDP Flood
```bash
# On host h1
mininet> h1 hping3 -2 -p 53 --flood h5
```

#### ICMP Flood
```bash
# On host h1
mininet> h1 ping -f h5
```

### 3. Monitor Detection

Watch the web interface for:
- **DDoS Alerts**: Real-time attack notifications
- **ML Confidence**: Detection accuracy scores
- **Mitigation Status**: Automatic blocking actions
- **Federated Updates**: Model synchronization

## API Endpoints

### Standard Endpoints
- `GET /switches` - Switch information
- `GET /flows` - Flow statistics
- `GET /stats` - Network statistics
- `GET /topology` - Network topology
- `GET /logs` - Activity logs

### DDoS Monitoring Endpoints
- `GET /ddos/alerts` - DDoS detection alerts
- `GET /ddos/stats` - Detection statistics
- `GET /ddos/mitigation` - Active mitigation rules
- `GET /ddos/threats` - Threat intelligence
- `GET /cicflow/features` - CICFlowMeter features
- `GET /federated/status` - Federated learning status

## Troubleshooting

### Common Issues

#### 1. Controller Connection Failed
```bash
# Check ports
sudo netstat -tlnp | grep :8080
sudo netstat -tlnp | grep :6633

# Check firewall
sudo ufw status
```

#### 2. CICFlowMeter Not Working
```bash
# Install Java (required for CICFlowMeter)
sudo apt install default-jdk -y

# Check permissions
sudo chmod +x /usr/local/bin/cicflowmeter
```

#### 3. ML Models Not Loading
```bash
# Check Python packages
pip list | grep -E "(sklearn|torch|pandas)"

# Check model files
ls -la ddos_model_*.pkl
```

#### 4. Federated Learning Issues
```bash
# Check network connectivity
telnet 192.168.1.100 9999

# Check logs
tail -f ddos_controller_*.log
```

### Log Analysis

#### Controller Logs
```bash
# View real-time logs
tail -f ddos_controller_root_controller.log

# Search for DDoS events
grep "DDoS DETECTED" ddos_controller_*.log

# Check mitigation actions
grep "mitigation applied" ddos_controller_*.log
```

#### Traffic Analysis
```bash
# View captured traffic
ls -la traffic_captures/

# Analyze with CICFlowMeter
cicflowmeter -f capture_*.pcap -c analysis.csv
```

## Performance Optimization

### 1. ML Model Tuning
```python
# Adjust detection threshold
DETECTION_THRESHOLD = 0.75  # Balance false positives/negatives

# Optimize training interval
TRAINING_INTERVAL = 180  # 3 minutes for faster adaptation
```

### 2. Network Optimization
```bash
# Increase buffer sizes
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
sudo sysctl -p
```

### 3. Storage Management
```bash
# Rotate logs
logrotate -f /etc/logrotate.d/ddos-controller

# Compress old captures
find traffic_captures/ -name "*.pcap" -mtime +7 -exec gzip {} \;
```

## Security Considerations

### 1. Access Control
```bash
# Restrict API access
sudo ufw allow from 192.168.1.0/24 to any port 8080
sudo ufw allow from 192.168.1.0/24 to any port 8081
```

### 2. Data Protection
```bash
# Encrypt sensitive data
gpg --cipher-algo AES256 --compress-algo 1 --symmetric ddos_model_*.pkl
```

### 3. Monitoring
```bash
# Set up system monitoring
sudo apt install htop iotop nethogs -y

# Monitor controller processes
ps aux | grep -E "(ryu|python.*controller)"
```

This completes the enhanced setup guide. The system provides comprehensive DDoS detection and mitigation capabilities with federated learning across multiple controllers.
