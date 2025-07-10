# Installation Guide

Complete installation guide for the Enhanced Ryu Flow Monitor with DDoS Detection system.

## 📋 System Requirements

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 20 GB free space
- **Network**: 100 Mbps connection

#### Recommended Requirements
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: 1 Gbps connection

### Software Requirements

#### Operating System
- Ubuntu 20.04 LTS or later
- Debian 10 or later
- CentOS 8 or later
- Other Linux distributions (with manual dependency installation)

#### Python Requirements
- Python 3.8 or higher
- pip 20.0 or higher
- virtualenv (recommended)

## 🔧 Pre-Installation Setup

### 1. Update System

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# or for newer versions
sudo dnf update -y
```

### 2. Install System Dependencies

#### Ubuntu/Debian
```bash
# Core development tools
sudo apt install -y build-essential python3-dev python3-pip python3-venv

# Network tools
sudo apt install -y tcpdump wireshark-common libpcap-dev

# OpenFlow and SDN tools
sudo apt install -y openvswitch-switch openvswitch-common

# Mininet (for network simulation)
sudo apt install -y mininet

# Java (required for CICFlowMeter)
sudo apt install -y default-jdk

# Additional utilities
sudo apt install -y git curl wget htop
```

#### CentOS/RHEL
```bash
# Core development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel python3-pip

# Network tools
sudo yum install -y tcpdump wireshark libpcap-devel

# OpenFlow tools
sudo yum install -y openvswitch

# Java
sudo yum install -y java-11-openjdk-devel

# Additional utilities
sudo yum install -y git curl wget htop
```

### 3. Configure Network

```bash
# Enable IP forwarding
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Configure firewall (Ubuntu/Debian)
sudo ufw allow 8080/tcp  # Web interface
sudo ufw allow 8081/tcp  # Client web interface
sudo ufw allow 6633/tcp  # OpenFlow
sudo ufw allow 6634/tcp  # Client OpenFlow
sudo ufw allow 9999/tcp  # Federated learning

# Configure firewall (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --permanent --add-port=6633/tcp
sudo firewall-cmd --permanent --add-port=6634/tcp
sudo firewall-cmd --permanent --add-port=9999/tcp
sudo firewall-cmd --reload
```

## 📦 Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd adversarial-ddos-attacks-sdn-dataset/mininet/ryu-flowmonitor

# Run automated installation script
chmod +x install.sh
./install.sh
```

### Method 2: Manual Installation

#### Step 1: Clone Repository

```bash
git clone <repository-url>
cd adversarial-ddos-attacks-sdn-dataset/mininet/ryu-flowmonitor
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv ddos_env

# Activate virtual environment
source ddos_env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 3: Install Python Dependencies

```bash
# Install from requirements file
pip install -r requirements.txt

# Or install manually
pip install ryu>=4.34
pip install webob>=1.8.7
pip install eventlet>=0.33.0
pip install scikit-learn>=1.0.0
pip install pandas>=1.3.0
pip install numpy>=1.21.0
pip install scapy>=2.4.5
pip install psutil>=5.8.0
pip install flask>=2.0.0
pip install requests>=2.25.0
```

#### Step 4: Install Optional Dependencies

```bash
# For advanced ML features
pip install torch>=1.10.0 torchvision>=0.11.0

# For CICFlowMeter
pip install cicflowmeter>=0.1.4

# For development and testing
pip install pytest>=6.2.0 pytest-cov>=3.0.0
```

#### Step 5: Verify Installation

```bash
# Test Python imports
python -c "import ryu; print('✅ Ryu installed')"
python -c "import sklearn; print('✅ Scikit-learn installed')"
python -c "import pandas; print('✅ Pandas installed')"
python -c "import flow_monitor_controller; print('✅ Controller ready')"

# Test Ryu manager
ryu-manager --version

# Test Mininet
sudo mn --version
```

## 🌐 Multi-Server Installation

### Server 1: Ryu Controller Server

```bash
# On Ryu Server (e.g., 192.168.1.100)
git clone <repository-url>
cd adversarial-ddos-attacks-sdn-dataset/mininet/ryu-flowmonitor

# Install controller dependencies
python3 -m venv ddos_env
source ddos_env/bin/activate
pip install ryu webob eventlet scikit-learn pandas numpy flask

# Configure as root controller
cp config/root_controller.conf controller.conf
```

### Server 2: Mininet Client Server

```bash
# On Mininet Server (e.g., 192.168.1.101)
git clone <repository-url>
cd adversarial-ddos-attacks-sdn-dataset/mininet/ryu-flowmonitor

# Install full dependencies including Mininet
python3 -m venv ddos_env
source ddos_env/bin/activate
pip install -r requirements.txt

# Install Mininet if not already installed
sudo apt install mininet

# Configure as client controller
cp config/client_controller.conf controller.conf
```

## 🔧 Post-Installation Configuration

### 1. Create Directories

```bash
# Create necessary directories
mkdir -p logs traffic_captures models config

# Set permissions
chmod 755 logs traffic_captures models
```

### 2. Configure Controller

```bash
# Copy example configuration
cp config/controller.conf.example config/controller.conf

# Edit configuration
nano config/controller.conf
```

### 3. Set Up Logging

```bash
# Configure log rotation
sudo cp config/logrotate.conf /etc/logrotate.d/ddos-controller

# Test log rotation
sudo logrotate -f /etc/logrotate.d/ddos-controller
```

### 4. Create Systemd Services (Optional)

```bash
# Copy service files
sudo cp config/ddos-controller.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable ddos-controller
sudo systemctl start ddos-controller
sudo systemctl status ddos-controller
```

## 🧪 Installation Verification

### 1. Basic Functionality Test

```bash
# Activate environment
source ddos_env/bin/activate

# Test controller import
python -c "
import flow_monitor_controller
controller = flow_monitor_controller.FlowMonitorController()
print('✅ Controller initialized successfully')
"
```

### 2. Network Test

```bash
# Start controller in background
ryu-manager flow_monitor_controller.py --wsapi-port 8080 &
CONTROLLER_PID=$!

# Wait for startup
sleep 5

# Test API endpoints
curl -s http://localhost:8080/stats | python -m json.tool

# Clean up
kill $CONTROLLER_PID
```

### 3. Mininet Integration Test

```bash
# Start controller
ryu-manager flow_monitor_controller.py --wsapi-port 8080 &
CONTROLLER_PID=$!

# Start Mininet
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633 --test pingall

# Clean up
sudo mn -c
kill $CONTROLLER_PID
```

## 🚨 Troubleshooting Installation

### Common Issues

#### Python Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall in virtual environment
pip uninstall ryu
pip install ryu
```

#### Permission Errors
```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod +x *.py *.sh
```

#### Port Conflicts
```bash
# Check port usage
sudo netstat -tlnp | grep :8080

# Kill conflicting processes
sudo pkill -f ryu-manager
```

#### Mininet Issues
```bash
# Clean Mininet state
sudo mn -c

# Restart Open vSwitch
sudo systemctl restart openvswitch-switch
```

### Dependency Issues

#### Missing System Libraries
```bash
# Ubuntu/Debian
sudo apt install -y python3-dev libffi-dev libssl-dev

# CentOS/RHEL
sudo yum install -y python3-devel libffi-devel openssl-devel
```

#### CICFlowMeter Installation
```bash
# Install Java if missing
sudo apt install default-jdk

# Install CICFlowMeter manually
wget https://github.com/ahlashkari/CICFlowMeter/releases/download/v4.0/CICFlowMeter-4.0.jar
sudo cp CICFlowMeter-4.0.jar /usr/local/bin/
```

## 📝 Next Steps

After successful installation:

1. **Configure the System**: See [Configuration Guide](../user-guides/configuration.md)
2. **Start Using**: Follow [Basic Usage Guide](../user-guides/basic-usage.md)
3. **Deploy in Production**: Read [Production Deployment](../deployment/production.md)
4. **Explore Examples**: Check [Examples](../examples/basic.md)

---

**Estimated Time**: 30-60 minutes  
**Difficulty**: Intermediate  
**Next**: [System Requirements](requirements.md)  
**Previous**: [Quick Start Guide](quick-start.md)
