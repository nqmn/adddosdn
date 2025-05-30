# Basic Usage Guide

Learn how to use the Enhanced Ryu Flow Monitor for DDoS detection and network monitoring.

## 🚀 Getting Started

### Prerequisites
- System installed and configured (see [Installation Guide](../getting-started/installation.md))
- Virtual environment activated
- Basic understanding of SDN concepts

### Quick Start Checklist
- [ ] Controller starts without errors
- [ ] Web interface accessible
- [ ] Mininet connects successfully
- [ ] API endpoints respond
- [ ] DDoS detection active

## 🎮 Basic Operations

### 1. Starting the Controller

#### Single Server Mode
```bash
# Activate virtual environment
source ddos_env/bin/activate

# Start controller with web interface
ryu-manager flow_monitor_controller.py \
    --wsapi-port 8080 \
    --verbose

# Alternative: Start with custom configuration
ryu-manager flow_monitor_controller.py \
    --wsapi-port 8080 \
    --ofp-tcp-listen-port 6633 \
    --observe-links \
    --verbose
```

#### Multi-Server Mode

**Root Controller (Server 1)**:
```bash
# Start root controller
ryu-manager flow_monitor_controller.py \
    --wsapi-port 8080 \
    --ofp-tcp-listen-port 6633 \
    --verbose
```

**Client Controller (Server 2)**:
```bash
# Start client controller
ryu-manager mininet_client_controller.py \
    --wsapi-port 8081 \
    --ofp-tcp-listen-port 6634 \
    --verbose
```

### 2. Starting Mininet Network

#### Basic Linear Topology
```bash
# Simple 3-node linear topology
sudo mn --topo linear,3 \
    --controller remote,ip=127.0.0.1,port=6633 \
    --switch ovsk,protocols=OpenFlow13

# Test connectivity
mininet> pingall
mininet> iperf h1 h3
```

#### Custom Topology
```bash
# Tree topology with 4 hosts
sudo mn --topo tree,depth=2,fanout=2 \
    --controller remote,ip=127.0.0.1,port=6633 \
    --switch ovsk,protocols=OpenFlow13 \
    --link tc,bw=100

# Single switch with 4 hosts
sudo mn --topo single,4 \
    --controller remote,ip=127.0.0.1,port=6633 \
    --switch ovsk,protocols=OpenFlow13
```

### 3. Accessing the Web Interface

#### Main Dashboard
Open your browser and navigate to:
- **Primary Controller**: http://localhost:8080/flow_monitor.html
- **Client Controller**: http://localhost:8081/flow_monitor.html

#### Key Interface Sections
- **Network Overview**: Real-time network statistics
- **DDoS Alerts**: Active and historical attack alerts
- **Switch Status**: Connected switches and their status
- **Flow Statistics**: Active flows and their metrics
- **ML Metrics**: Machine learning model performance

## 📊 Monitoring Network Activity

### 1. Real-Time Statistics

#### View Network Stats
```bash
# Get overall network statistics
curl http://localhost:8080/stats

# Get switch information
curl http://localhost:8080/switches

# Get flow statistics
curl http://localhost:8080/flows
```

#### Monitor Topology
```bash
# Get network topology
curl http://localhost:8080/topology

# Get link information
curl http://localhost:8080/links
```

### 2. Traffic Generation

#### Normal Traffic Patterns
```bash
# In Mininet CLI
mininet> h1 ping -c 10 h3
mininet> iperf h1 h2
mininet> h1 wget -O /dev/null http://h3/
```

#### Background Traffic
```bash
# Generate continuous background traffic
mininet> h1 ping h3 &
mininet> h2 ping h4 &
mininet> iperf h1 h3 &
```

### 3. Log Monitoring

#### View Controller Logs
```bash
# Real-time log monitoring
tail -f logs/ddos_controller_*.log

# Search for specific events
grep "DDoS" logs/ddos_controller_*.log
grep "mitigation" logs/ddos_controller_*.log
```

#### Activity Logs via API
```bash
# Get recent activity logs
curl http://localhost:8080/logs | python -m json.tool
```

## 🛡️ DDoS Detection and Testing

### 1. Understanding Detection

#### Detection Thresholds
- **Low Sensitivity**: 0.9 (fewer false positives)
- **Medium Sensitivity**: 0.7 (balanced)
- **High Sensitivity**: 0.5 (more detections)

#### Detection Methods
- **Packet-level**: Real-time packet analysis
- **Flow-level**: Statistical flow analysis
- **ML-based**: Machine learning anomaly detection

### 2. Simulating DDoS Attacks

#### TCP SYN Flood
```bash
# In Mininet CLI
mininet> h1 hping3 -S -p 80 --flood h3

# With specific rate
mininet> h1 hping3 -S -p 80 -i u100 h3
```

#### UDP Flood
```bash
# UDP flood attack
mininet> h1 hping3 -2 -p 53 --flood h3

# UDP with payload
mininet> h1 hping3 -2 -p 53 -d 1024 --flood h3
```

#### ICMP Flood
```bash
# ICMP ping flood
mininet> h1 ping -f h3

# High-rate ICMP
mininet> h1 hping3 -1 --flood h3
```

#### HTTP Flood
```bash
# Start simple HTTP server on h3
mininet> h3 python -m http.server 80 &

# Generate HTTP flood from h1
mininet> h1 while true; do wget -O /dev/null http://h3/; done
```

### 3. Monitoring DDoS Detection

#### Check DDoS Alerts
```bash
# Get current DDoS alerts
curl http://localhost:8080/ddos/alerts

# Get DDoS statistics
curl http://localhost:8080/ddos/stats

# Get active mitigation rules
curl http://localhost:8080/ddos/mitigation
```

#### Watch Real-Time Detection
```bash
# Monitor detection in real-time
watch -n 1 'curl -s http://localhost:8080/ddos/alerts | python -m json.tool'
```

## 🔧 Configuration and Tuning

### 1. Adjusting Detection Sensitivity

#### Via Configuration File
```python
# Edit controller configuration
DETECTION_CONFIG = {
    'threshold': 0.7,           # Detection threshold
    'training_interval': 300,   # Model retraining interval
    'buffer_size': 1000,        # Feature buffer size
    'mitigation_timeout': 60    # Mitigation rule timeout
}
```

#### Runtime Adjustment
```bash
# Adjust via API (if implemented)
curl -X POST http://localhost:8080/config/detection \
    -H "Content-Type: application/json" \
    -d '{"threshold": 0.8}'
```

### 2. Model Management

#### Check Model Status
```bash
# Get ML model information
curl http://localhost:8080/ml/status

# Get federated learning status
curl http://localhost:8080/federated/status
```

#### Model Training
```bash
# Trigger manual model training
curl -X POST http://localhost:8080/ml/train

# Upload custom model
curl -X POST http://localhost:8080/ml/upload \
    -F "model_file=@custom_model.pkl"
```

## 📈 Performance Monitoring

### 1. System Metrics

#### Resource Usage
```bash
# Monitor system resources
htop
iotop
nethogs

# Check controller process
ps aux | grep ryu-manager
```

#### Network Performance
```bash
# Monitor network interfaces
iftop
nload
vnstat
```

### 2. Application Metrics

#### Controller Performance
```bash
# Get performance metrics
curl http://localhost:8080/metrics

# Check processing latency
curl http://localhost:8080/stats | grep latency
```

#### Detection Performance
```bash
# Get detection statistics
curl http://localhost:8080/ddos/stats | python -m json.tool
```

## 🚨 Troubleshooting Common Issues

### 1. Controller Issues

#### Controller Won't Start
```bash
# Check port conflicts
sudo netstat -tlnp | grep :8080

# Check Python environment
which python
pip list | grep ryu
```

#### No Switches Connected
```bash
# Check OpenFlow port
sudo netstat -tlnp | grep :6633

# Restart Mininet
sudo mn -c
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633
```

### 2. Detection Issues

#### No DDoS Alerts
```bash
# Check detection threshold
curl http://localhost:8080/ddos/stats

# Generate more aggressive traffic
mininet> h1 hping3 -S --flood h3
```

#### False Positives
```bash
# Increase detection threshold
# Edit controller configuration
# Restart controller
```

### 3. Performance Issues

#### High CPU Usage
```bash
# Check process usage
top -p $(pgrep -f ryu-manager)

# Reduce detection frequency
# Increase training interval
```

#### Memory Issues
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Clear feature buffers
# Restart controller
```

## 📚 Next Steps

After mastering basic usage:

1. **Explore Advanced Features**: [DDoS Detection](../advanced/ddos-detection.md)
2. **Learn API Usage**: [API Reference](api-reference.md)
3. **Configure System**: [Configuration Guide](configuration.md)
4. **Deploy in Production**: [Production Deployment](../deployment/production.md)
5. **Try Examples**: [Advanced Examples](../examples/advanced.md)

---

**Estimated Learning Time**: 2-4 hours  
**Difficulty**: Beginner to Intermediate  
**Next**: [Web Interface Guide](web-interface.md)  
**Previous**: [Quick Start Guide](../getting-started/quick-start.md)
