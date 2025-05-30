# Common Issues and Solutions

Comprehensive troubleshooting guide for the Enhanced Ryu Flow Monitor system.

## 🚨 Installation Issues

### Python Import Errors

#### Problem: "No module named 'ryu'"
```
ImportError: No module named 'ryu'
```

**Solutions**:
```bash
# Check virtual environment
source ddos_env/bin/activate
which python

# Reinstall Ryu
pip uninstall ryu
pip install ryu>=4.34

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Problem: "No module named 'sklearn'"
```
ImportError: No module named 'sklearn'
```

**Solutions**:
```bash
# Install scikit-learn
pip install scikit-learn>=1.0.0

# For older systems
pip install scikit-learn==1.0.2
```

### System Dependencies

#### Problem: "tcpdump: command not found"
**Solutions**:
```bash
# Ubuntu/Debian
sudo apt install tcpdump wireshark-common

# CentOS/RHEL
sudo yum install tcpdump wireshark
```

#### Problem: "Java not found" (CICFlowMeter)
**Solutions**:
```bash
# Install OpenJDK
sudo apt install default-jdk

# Check Java installation
java -version
which java
```

## 🔧 Controller Issues

### Controller Startup Problems

#### Problem: Controller won't start
```
ERROR: Address already in use
```

**Solutions**:
```bash
# Check port usage
sudo netstat -tlnp | grep :8080
sudo netstat -tlnp | grep :6633

# Kill existing processes
sudo pkill -f ryu-manager
sudo pkill -f flow_monitor_controller

# Use different ports
ryu-manager flow_monitor_controller.py --wsapi-port 8081
```

#### Problem: "Permission denied" errors
**Solutions**:
```bash
# Fix file permissions
chmod +x *.py *.sh
sudo chown -R $USER:$USER .

# Run without sudo (recommended)
# Avoid: sudo ryu-manager ...
```

### Import and Module Issues

#### Problem: "NameError: name 'set_ev_cls' is not defined"
This is fixed in the current version. If you encounter this:

**Solutions**:
```bash
# Update to latest version
git pull origin main

# Check if Ryu is properly installed
python -c "from ryu.controller.handler import set_ev_cls; print('OK')"
```

#### Problem: Controller starts but no functionality
**Solutions**:
```bash
# Check warnings in startup logs
ryu-manager flow_monitor_controller.py --verbose

# Verify all dependencies
python -c "
import flow_monitor_controller
print('Controller imported successfully')
"
```

## 🌐 Network Connectivity Issues

### Mininet Connection Problems

#### Problem: Mininet can't connect to controller
```
*** Error connecting to controller
```

**Solutions**:
```bash
# Check controller is running
ps aux | grep ryu-manager

# Check OpenFlow port
sudo netstat -tlnp | grep :6633

# Restart with correct controller IP
sudo mn -c
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633
```

#### Problem: "No route to host" in multi-server setup
**Solutions**:
```bash
# Test connectivity
ping 192.168.1.100
telnet 192.168.1.100 6633

# Check firewall
sudo ufw status
sudo ufw allow 6633/tcp

# Check routing
ip route show
```

### Switch Connection Issues

#### Problem: Switches not appearing in web interface
**Solutions**:
```bash
# Check switch status in Mininet
mininet> net
mininet> dump

# Verify OpenFlow version
sudo ovs-vsctl show
sudo ovs-vsctl get bridge s1 protocols

# Force OpenFlow 1.3
sudo mn --switch ovsk,protocols=OpenFlow13
```

#### Problem: Intermittent switch disconnections
**Solutions**:
```bash
# Check system resources
htop
free -h

# Increase OpenFlow timeouts
# Edit controller configuration
# Restart with more verbose logging
ryu-manager flow_monitor_controller.py --verbose
```

## 🛡️ DDoS Detection Issues

### Detection Not Working

#### Problem: No DDoS alerts generated
**Solutions**:
```bash
# Check detection threshold
curl http://localhost:8080/ddos/stats

# Lower detection threshold (more sensitive)
# Edit controller configuration:
# detection_threshold = 0.5

# Generate more aggressive traffic
mininet> h1 hping3 -S --flood h3
```

#### Problem: Too many false positives
**Solutions**:
```bash
# Increase detection threshold (less sensitive)
# detection_threshold = 0.9

# Check normal traffic patterns
curl http://localhost:8080/flows

# Retrain model with current traffic
curl -X POST http://localhost:8080/ml/train
```

### ML Model Issues

#### Problem: "Model not found" errors
**Solutions**:
```bash
# Check model files
ls -la ddos_model_*.pkl

# Regenerate models
python create_sample_models.py

# Check ML dependencies
python -c "import sklearn; print('ML available')"
```

#### Problem: Poor detection accuracy
**Solutions**:
```bash
# Collect more training data
# Run system for longer periods
# Generate diverse traffic patterns

# Check model performance
curl http://localhost:8080/ml/models

# Upload better model
curl -X POST http://localhost:8080/ml/upload -F "model_file=@better_model.pkl"
```

## 🌐 Web Interface Issues

### Interface Not Loading

#### Problem: "Connection refused" on web interface
**Solutions**:
```bash
# Check if controller is running
curl http://localhost:8080/stats

# Check webob installation
pip list | grep webob
pip install webob

# Check firewall
sudo ufw allow 8080/tcp
```

#### Problem: API returns empty responses
**Solutions**:
```bash
# Check controller logs
tail -f logs/ddos_controller_*.log

# Verify switches are connected
curl http://localhost:8080/switches

# Generate some traffic first
mininet> pingall
```

### CORS and Browser Issues

#### Problem: CORS errors in browser console
**Solutions**:
```bash
# CORS is enabled by default
# Check browser developer tools
# Try different browser
# Clear browser cache
```

#### Problem: JavaScript errors
**Solutions**:
```bash
# Check browser compatibility
# Use modern browser (Chrome, Firefox, Safari)
# Disable browser extensions
# Check network connectivity
```

## 📊 Performance Issues

### High CPU Usage

#### Problem: Controller consuming too much CPU
**Solutions**:
```bash
# Check process usage
top -p $(pgrep -f ryu-manager)

# Reduce detection frequency
# Increase training_interval in config
# Limit packet processing rate
```

#### Problem: System becomes unresponsive
**Solutions**:
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart controller
sudo pkill -f ryu-manager
ryu-manager flow_monitor_controller.py

# Reduce buffer sizes in configuration
```

### Memory Issues

#### Problem: "Out of memory" errors
**Solutions**:
```bash
# Check memory usage
free -h
cat /proc/meminfo

# Clear feature buffers
# Restart controller
# Reduce buffer_size in configuration

# Add swap space (temporary fix)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Disk Space Issues

#### Problem: "No space left on device"
**Solutions**:
```bash
# Check disk usage
df -h
du -sh logs/ traffic_captures/

# Clean old files
find logs/ -name "*.log" -mtime +7 -delete
find traffic_captures/ -name "*.pcap" -mtime +7 -delete

# Configure log rotation
sudo cp config/logrotate.conf /etc/logrotate.d/ddos-controller
```

## 🔄 Multi-Server Issues

### Federated Learning Problems

#### Problem: Controllers not communicating
**Solutions**:
```bash
# Check network connectivity
telnet 192.168.1.100 9999

# Check federated learning status
curl http://localhost:8080/federated/status

# Verify firewall settings
sudo ufw allow 9999/tcp
```

#### Problem: Model synchronization failing
**Solutions**:
```bash
# Check controller logs on both servers
grep "federated" logs/ddos_controller_*.log

# Restart both controllers
# Check network latency
ping -c 10 192.168.1.100
```

## 🧪 Testing and Validation

### Test Environment Issues

#### Problem: Tests failing
**Solutions**:
```bash
# Run basic tests
python -m pytest tests/ -v

# Check test dependencies
pip install pytest pytest-cov

# Run specific test
python test_simple_import.py
```

#### Problem: Inconsistent behavior
**Solutions**:
```bash
# Clean environment
sudo mn -c
sudo pkill -f ryu-manager

# Restart from clean state
source ddos_env/bin/activate
ryu-manager flow_monitor_controller.py --verbose
```

## 🆘 Getting Help

### Diagnostic Information

When reporting issues, include:

```bash
# System information
uname -a
python --version
pip list | grep -E "(ryu|sklearn|pandas)"

# Controller status
ps aux | grep ryu-manager
curl http://localhost:8080/health

# Network status
sudo netstat -tlnp | grep -E "(6633|8080)"
sudo ovs-vsctl show

# Recent logs
tail -50 logs/ddos_controller_*.log
```

### Log Collection Script

```bash
#!/bin/bash
# collect_diagnostics.sh
echo "=== System Info ===" > diagnostics.txt
uname -a >> diagnostics.txt
python --version >> diagnostics.txt
echo "=== Controller Status ===" >> diagnostics.txt
ps aux | grep ryu-manager >> diagnostics.txt
echo "=== Network Status ===" >> diagnostics.txt
sudo netstat -tlnp | grep -E "(6633|8080)" >> diagnostics.txt
echo "=== Recent Logs ===" >> diagnostics.txt
tail -100 logs/ddos_controller_*.log >> diagnostics.txt
```

### Emergency Recovery

#### Complete System Reset
```bash
# Stop all processes
sudo pkill -f ryu-manager
sudo mn -c

# Clean temporary files
rm -f ddos_model_*.pkl
rm -f logs/*.log

# Restart from scratch
source ddos_env/bin/activate
ryu-manager flow_monitor_controller.py --verbose
```

---

**Next**: [Error Messages Guide](error-messages.md)  
**Previous**: [API Reference](../user-guides/api-reference.md)
