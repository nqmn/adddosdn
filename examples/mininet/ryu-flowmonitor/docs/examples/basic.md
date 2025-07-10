# Basic Examples

Practical examples for getting started with the Enhanced Ryu Flow Monitor system.

## 🎯 Example 1: Simple Network Monitoring

### Scenario
Monitor a basic 3-node linear network and observe normal traffic patterns.

### Setup
```bash
# Terminal 1: Start controller
source ddos_env/bin/activate
ryu-manager flow_monitor_controller.py --wsapi-port 8080 --verbose

# Terminal 2: Start Mininet
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13
```

### Basic Operations
```bash
# In Mininet CLI
mininet> pingall
mininet> h1 ping -c 5 h3
mininet> iperf h1 h2
```

### Monitoring
```bash
# Terminal 3: Monitor via API
watch -n 2 'curl -s http://localhost:8080/stats | python -m json.tool'

# Check switches
curl http://localhost:8080/switches | python -m json.tool

# View flows
curl http://localhost:8080/flows | python -m json.tool
```

### Expected Results
- 3 switches connected
- Ping success between all hosts
- Flow entries created for learned MAC addresses
- Statistics updating in real-time

## 🛡️ Example 2: Basic DDoS Detection

### Scenario
Generate a simple DDoS attack and observe detection and mitigation.

### Setup
```bash
# Use same setup as Example 1
# Ensure controller is running with DDoS detection enabled
```

### Generate Normal Traffic
```bash
# In Mininet CLI
mininet> h1 ping -c 10 h3
mininet> h2 ping -c 10 h3
```

### Generate DDoS Attack
```bash
# TCP SYN flood
mininet> h1 hping3 -S -p 80 --flood h3

# Or ICMP flood
mininet> h1 ping -f h3
```

### Monitor Detection
```bash
# Watch for DDoS alerts
watch -n 1 'curl -s http://localhost:8080/ddos/alerts | python -m json.tool'

# Check detection statistics
curl http://localhost:8080/ddos/stats | python -m json.tool

# View mitigation rules
curl http://localhost:8080/ddos/mitigation | python -m json.tool
```

### Expected Results
- DDoS alerts generated within seconds
- Mitigation rules automatically applied
- Attack traffic blocked or rate-limited
- Normal traffic continues to flow

## 📊 Example 3: Web Interface Usage

### Scenario
Use the web interface to monitor network activity and DDoS detection.

### Access Web Interface
1. Open browser: http://localhost:8080/flow_monitor.html
2. Navigate through different sections

### Key Interface Features
- **Dashboard**: Real-time network overview
- **Switches**: Connected switch status
- **Flows**: Active flow entries
- **DDoS Alerts**: Attack detection history
- **Statistics**: Performance metrics

### Interactive Testing
```bash
# Generate traffic while watching web interface
mininet> h1 ping h3 &
mininet> h2 ping h3 &

# Generate attack traffic
mininet> h1 hping3 -S --flood h3
```

### Web Interface Sections
1. **Network Status**: Switch count, flow count, uptime
2. **Real-time Alerts**: DDoS detection notifications
3. **Traffic Graphs**: Visual representation of network activity
4. **Mitigation Status**: Active blocking rules

## 🔧 Example 4: API Integration

### Scenario
Integrate with the REST API for automated monitoring and response.

### Basic API Queries
```bash
# Get system health
curl http://localhost:8080/health

# Get network statistics
curl http://localhost:8080/stats

# Get topology information
curl http://localhost:8080/topology
```

### Automated Monitoring Script
```bash
#!/bin/bash
# monitor.sh - Basic monitoring script

while true; do
    echo "=== $(date) ==="
    
    # Check system health
    health=$(curl -s http://localhost:8080/health)
    echo "Health: $health"
    
    # Check for DDoS alerts
    alerts=$(curl -s http://localhost:8080/ddos/alerts | jq length)
    echo "DDoS Alerts: $alerts"
    
    # Check active mitigations
    mitigations=$(curl -s http://localhost:8080/ddos/mitigation | jq length)
    echo "Active Mitigations: $mitigations"
    
    echo "---"
    sleep 10
done
```

### Alert Processing Script
```bash
#!/bin/bash
# process_alerts.sh - Process DDoS alerts

# Get recent alerts
alerts=$(curl -s http://localhost:8080/ddos/alerts)

# Process each alert
echo "$alerts" | jq -r '.[] | select(.confidence > 0.8) | .source_ip' | while read ip; do
    echo "High confidence attack from: $ip"
    # Add custom response logic here
done
```

## 🌐 Example 5: Multi-Server Setup

### Scenario
Set up federated learning between two controllers.

### Server 1 (Root Controller)
```bash
# On 192.168.1.100
cd ryu-flowmonitor
source ddos_env/bin/activate

# Start root controller
ryu-manager flow_monitor_controller.py \
    --wsapi-port 8080 \
    --ofp-tcp-listen-port 6633 \
    --verbose
```

### Server 2 (Client Controller)
```bash
# On 192.168.1.101
cd ryu-flowmonitor
source ddos_env/bin/activate

# Start client controller
ryu-manager mininet_client_controller.py \
    --wsapi-port 8081 \
    --ofp-tcp-listen-port 6634 \
    --verbose

# Start Mininet network
sudo mn --topo tree,depth=2,fanout=2 \
    --controller remote,ip=127.0.0.1,port=6634 \
    --switch ovsk,protocols=OpenFlow13
```

### Monitor Federated Learning
```bash
# Check federated status on root
curl http://192.168.1.100:8080/federated/status

# Check federated status on client
curl http://192.168.1.101:8081/federated/status

# Monitor model synchronization
watch -n 30 'curl -s http://192.168.1.100:8080/federated/status | jq .global_model_version'
```

## 🧪 Example 6: Custom Traffic Patterns

### Scenario
Generate various traffic patterns to test detection capabilities.

### HTTP Traffic Simulation
```bash
# Start HTTP server on h3
mininet> h3 python -m http.server 80 &

# Generate normal HTTP requests
mininet> h1 wget -O /dev/null http://10.0.0.3/
mininet> h2 wget -O /dev/null http://10.0.0.3/

# Generate HTTP flood
mininet> h1 while true; do wget -O /dev/null http://10.0.0.3/; done &
```

### Mixed Protocol Attack
```bash
# TCP SYN flood
mininet> h1 hping3 -S -p 80 --flood h3 &

# UDP flood
mininet> h1 hping3 -2 -p 53 --flood h3 &

# ICMP flood
mininet> h1 ping -f h3 &
```

### Gradual Attack Escalation
```bash
# Start with normal traffic
mininet> h1 ping -i 1 h3 &

# Gradually increase rate
mininet> h1 ping -i 0.5 h3 &
mininet> h1 ping -i 0.1 h3 &
mininet> h1 ping -f h3 &
```

## 📈 Example 7: Performance Testing

### Scenario
Test system performance under various load conditions.

### Load Generation
```bash
# Multiple concurrent flows
mininet> h1 iperf -s &
mininet> h2 iperf -c h1 -t 60 &
mininet> h3 iperf -c h1 -t 60 &

# High packet rate
mininet> h1 hping3 -i u1000 h3  # 1000 packets/second
```

### Performance Monitoring
```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor controller performance
curl http://localhost:8080/metrics | python -m json.tool

# Check processing latency
time curl http://localhost:8080/stats
```

### Stress Testing
```bash
# Maximum rate traffic
mininet> h1 hping3 --flood h3 &
mininet> h2 hping3 --flood h3 &

# Monitor detection performance
watch -n 1 'curl -s http://localhost:8080/ddos/stats | jq .total_detections'
```

## 🔍 Example 8: Log Analysis

### Scenario
Analyze system logs for troubleshooting and optimization.

### Real-time Log Monitoring
```bash
# Monitor controller logs
tail -f logs/ddos_controller_*.log

# Filter for specific events
tail -f logs/ddos_controller_*.log | grep -E "(DDoS|mitigation|error)"

# Monitor with timestamps
tail -f logs/ddos_controller_*.log | while read line; do echo "$(date): $line"; done
```

### Log Analysis Scripts
```bash
#!/bin/bash
# analyze_logs.sh

LOG_FILE="logs/ddos_controller_*.log"

echo "=== DDoS Detection Summary ==="
grep -c "DDoS DETECTED" $LOG_FILE
echo "Total detections: $(grep -c 'DDoS DETECTED' $LOG_FILE)"
echo "Mitigations applied: $(grep -c 'mitigation applied' $LOG_FILE)"
echo "False positives: $(grep -c 'false positive' $LOG_FILE)"

echo "=== Top Attack Sources ==="
grep "DDoS DETECTED" $LOG_FILE | grep -o "from [0-9.]*" | sort | uniq -c | sort -nr | head -5

echo "=== Attack Types ==="
grep "attack_type" $LOG_FILE | grep -o "attack_type: [a-z_]*" | sort | uniq -c
```

## 🎓 Learning Exercises

### Exercise 1: Detection Tuning
1. Start with high detection threshold (0.9)
2. Generate mild attack traffic
3. Gradually lower threshold until detection occurs
4. Find optimal balance between sensitivity and false positives

### Exercise 2: Custom Topology
1. Create custom Mininet topology
2. Connect to controller
3. Generate traffic between specific hosts
4. Analyze flow patterns and detection behavior

### Exercise 3: API Automation
1. Write script to automatically detect attacks
2. Implement custom mitigation responses
3. Create dashboard using API data
4. Set up alerting system

---

**Next**: [Advanced Examples](advanced.md)  
**Previous**: [Troubleshooting](../troubleshooting/common-issues.md)
