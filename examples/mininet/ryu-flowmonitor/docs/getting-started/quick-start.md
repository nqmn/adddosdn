# Quick Start Guide

Get your SDN DDoS Detection System up and running in 15 minutes!

## 🎯 Prerequisites

Before starting, ensure you have:
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8 or higher
- At least 4GB RAM
- Network connectivity between servers (if using multi-server setup)

## 🚀 Single Server Quick Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd adversarial-ddos-attacks-sdn-dataset/mininet/ryu-flowmonitor
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python3 -m venv ddos_env
source ddos_env/bin/activate

# Install core dependencies
pip install ryu webob eventlet scikit-learn pandas numpy

# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install tcpdump wireshark-common libpcap-dev mininet openvswitch-switch -y
```

### Step 3: Test the Installation

```bash
# Test controller import
python -c "import flow_monitor_controller; print('✅ Controller ready!')"

# Test Ryu installation
ryu-manager --version
```

### Step 4: Start the Controller

```bash
# Start the enhanced controller
ryu-manager flow_monitor_controller.py --wsapi-port 8080 --verbose
```

### Step 5: Start Mininet Network

Open a new terminal:

```bash
# Activate environment
source ddos_env/bin/activate

# Start simple network
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13
```

### Step 6: Access Web Interface

Open your browser and navigate to:
- **Controller Dashboard**: http://localhost:8080/flow_monitor.html
- **API Status**: http://localhost:8080/stats

## 🌐 Multi-Server Quick Setup

### Server 1: Ryu Controller (Root)

```bash
# On Ryu Server (192.168.1.100)
cd ryu-flowmonitor
source ddos_env/bin/activate

# Start root controller
ryu-manager flow_monitor_controller.py \
    --wsapi-port 8080 \
    --ofp-tcp-listen-port 6633 \
    --verbose
```

### Server 2: Mininet Client

```bash
# On Mininet Server (192.168.1.101)
cd ryu-flowmonitor
source ddos_env/bin/activate

# Start client controller
ryu-manager mininet_client_controller.py \
    --wsapi-port 8081 \
    --ofp-tcp-listen-port 6634 \
    --verbose

# In another terminal, start Mininet
sudo mn --topo linear,5 \
    --controller remote,ip=127.0.0.1,port=6634 \
    --switch ovsk,protocols=OpenFlow13
```

## 🧪 Quick Test

### Test Basic Connectivity

In Mininet CLI:
```bash
mininet> pingall
mininet> iperf h1 h3
```

### Test DDoS Detection

Generate some traffic to trigger detection:

```bash
# In Mininet CLI - simulate normal traffic
mininet> h1 ping -c 10 h3

# Simulate potential DDoS (high rate)
mininet> h1 ping -f -c 100 h3
```

Watch the controller logs and web interface for DDoS alerts!

## 📊 Verify Everything Works

### Check Controller Status
```bash
curl http://localhost:8080/stats
```

### Check Switches
```bash
curl http://localhost:8080/switches
```

### Check DDoS Alerts
```bash
curl http://localhost:8080/ddos/alerts
```

## 🎉 Success Indicators

You should see:
- ✅ Controller starts without errors
- ✅ Mininet connects to controller
- ✅ Web interface loads at http://localhost:8080/flow_monitor.html
- ✅ API endpoints return JSON data
- ✅ Ping tests work in Mininet
- ✅ DDoS detection logs appear during high-rate traffic

## 🔧 Quick Configuration

### Enable More Features

Edit the controller configuration:

```python
# In flow_monitor_controller.py
CONTROLLER_CONFIG = {
    'detection_threshold': 0.7,  # Lower = more sensitive
    'training_interval': 300,    # 5 minutes
    'enable_cicflow': True,      # Enable CICFlowMeter
    'enable_federated': True     # Enable federated learning
}
```

### Adjust Detection Sensitivity

```python
# More sensitive detection
self.detection_threshold = 0.5

# Less sensitive detection  
self.detection_threshold = 0.9
```

## 🚨 Common Quick Fixes

### Controller Won't Start
```bash
# Check if port is in use
sudo netstat -tlnp | grep :8080

# Kill existing process
sudo pkill -f ryu-manager
```

### Mininet Connection Issues
```bash
# Clean up Mininet
sudo mn -c

# Restart with verbose logging
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13 -v debug
```

### Web Interface Not Loading
```bash
# Check if webob is installed
pip list | grep webob

# Install if missing
pip install webob
```

## 📚 Next Steps

Now that you have the basic system running:

1. **Explore the Web Interface**: Navigate through the monitoring dashboard
2. **Read the [Architecture Overview](architecture.md)**: Understand how the system works
3. **Try Advanced Features**: Enable CICFlowMeter and federated learning
4. **Review [Configuration Guide](../user-guides/configuration.md)**: Customize the system
5. **Check [Examples](../examples/basic.md)**: See more usage scenarios

## 🆘 Need Help?

- **Issues**: Check [Common Issues](../troubleshooting/common-issues.md)
- **Configuration**: See [Configuration Guide](../user-guides/configuration.md)
- **Advanced Setup**: Read [Installation Guide](installation.md)
- **API Usage**: Check [API Reference](../user-guides/api-reference.md)

---

**Estimated Time**: 15 minutes  
**Difficulty**: Beginner  
**Next**: [Architecture Overview](architecture.md)
