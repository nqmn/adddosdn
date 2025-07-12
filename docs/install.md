# ⚙️ Installation and Setup Guide

This guide walks you through setting up the AdDDoSDN framework from scratch. Whether you're a student, researcher, or security professional, this guide will get you up and running safely.

## 🎯 Quick Overview

**What you'll install:**
- Virtual network simulation tools (Mininet)
- SDN controller software (Ryu)
- Network analysis tools (Wireshark/tshark)
- Python libraries for data processing
- The AdDDoSDN framework itself

**What you'll be able to do:**
- Generate cybersecurity datasets safely
- Study DDoS attacks in a controlled environment
- Create training data for machine learning models
- Learn about SDN security

## 📋 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Operating System** | Ubuntu 18.04+ | Ubuntu 20.04+ or 22.04+ |
| **RAM** | 4GB | 8GB+ |
| **CPU** | 2 cores | 4+ cores |
| **Disk Space** | 10GB free | 50GB+ free |
| **Network** | Internet connection | High-speed broadband |

### User Requirements
- **Sudo access** (required for network simulation)
- **Basic command line familiarity** (helpful but not required)
- **No prior SDN experience needed** (we'll guide you through it)

## 🚀 Installation Steps

### Step 1: Update Your System

```bash
# Update package lists
sudo apt update

# Upgrade existing packages (optional but recommended)
sudo apt upgrade -y
```

### Step 2: Install Core Dependencies

```bash
# Install essential system tools
sudo apt install -y python3-pip python3-venv git curl wget

# Install network simulation tools
sudo apt install -y mininet

# Install SDN controller
sudo apt install -y ryu-manager

# Install network analysis tools
sudo apt install -y tshark wireshark

# Install attack simulation tools
sudo apt install -y slowhttptest

# Install additional utilities
sudo apt install -y net-tools htop
```

### Step 3: Verify Core Installations

```bash
# Check Mininet
sudo mn --version
# Expected output: mininet 2.x.x

# Check Ryu
ryu-manager --version
# Expected output: ryu-manager 4.x.x

# Check tshark
tshark --version
# Expected output: TShark (Wireshark) x.x.x

# Check slowhttptest
slowhttptest -h
# Expected output: Help message for slowhttptest
```

### Step 4: Get the Framework

```bash
# Clone the repository
git clone https://github.com/nqmn/AdDDoSSDN_dataset.git

# Navigate to the project directory
cd AdDDoSSDN_dataset

# Check that you have the right files
ls
# You should see: dataset_generation/, examples/, docs/, README.md, etc.
```

### Step 5: Set Up Python Environment

```bash
# Create isolated Python environment
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Your prompt should now start with (venv)

# Install Python dependencies
pip install -r dataset_generation/requirements.txt
```

### Step 6: Verify Framework Installation

```bash
# Quick test to check if everything is working
# This will test the framework without generating data
sudo python3 -c "
import sys
sys.path.append('dataset_generation/src')
print('✅ Python imports working')

import subprocess
result = subprocess.run(['which', 'mn'], capture_output=True)
if result.returncode == 0:
    print('✅ Mininet found')
else:
    print('❌ Mininet not found')

result = subprocess.run(['which', 'ryu-manager'], capture_output=True)
if result.returncode == 0:
    print('✅ Ryu controller found')
else:
    print('❌ Ryu controller not found')
"
```

## 🧪 Test Your Installation

### Quick Test (5 minutes)

```bash
# Make sure you're in the project directory and venv is activated
source venv/bin/activate

# Run the quick test script
sudo python3 dataset_generation/test.py
```

**What should happen:**
1. You'll see startup messages about cleaning Mininet
2. Tools verification will run
3. Ryu controller will start
4. Mininet network will be created
5. Various attacks will run for 5 seconds each
6. You'll see "Dataset generation complete"

**Expected output location:**
```bash
# Check that files were created
ls dataset_generation/test_output/
# You should see: *.pcap files, *.csv files, *.log files
```

### Verify Test Results

```bash
# Check packet features file
head -5 dataset_generation/test_output/packet_features.csv
# Should show CSV header and data rows

# Check flow features file  
head -5 dataset_generation/test_output/flow_features.csv
# Should show CSV header and data rows

# Check attack log for any issues
tail -20 dataset_generation/test_output/attack.log
# Should show attack completion messages
```

## 🔧 Troubleshooting

### Common Issue 1: "Permission denied" errors

**Problem:** Getting permission errors when running the framework

**Solution:**
```bash
# Make sure you're using sudo for the main commands
sudo python3 dataset_generation/test.py

# Check that you can access Mininet
sudo mn --test pingall
```

### Common Issue 2: "Command not found" errors

**Problem:** System can't find `mn`, `ryu-manager`, or other tools

**Solution:**
```bash
# For Mininet
sudo apt install -y mininet
which mn  # Should show /usr/bin/mn

# For Ryu
sudo apt install -y ryu-manager  
which ryu-manager  # Should show /usr/bin/ryu-manager

# For tshark
sudo apt install -y tshark
which tshark  # Should show /usr/bin/tshark
```

### Common Issue 3: Python import errors

**Problem:** Python can't find required modules

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Your prompt should show (venv)

# Reinstall dependencies
pip install --upgrade pip
pip install -r dataset_generation/requirements.txt

# Check specific imports
python3 -c "import scapy; print('Scapy OK')"
python3 -c "import pandas; print('Pandas OK')"
```

### Common Issue 4: Network setup failures

**Problem:** Mininet fails to create network or controller won't start

**Solution:**
```bash
# Clean up any leftover processes
sudo mn -c

# Kill any ryu processes
sudo pkill -f ryu-manager

# Remove any leftover network interfaces
sudo ip link del s1 2>/dev/null || true

# Try the test again
sudo python3 dataset_generation/test.py
```

### Common Issue 5: No data generated

**Problem:** Scripts run but no CSV files are created

**Solution:**
```bash
# Check permissions on output directory
ls -la dataset_generation/test_output/

# Check logs for errors
cat dataset_generation/test_output/test.log
cat dataset_generation/test_output/attack.log

# Verify PCAP files exist
ls -la dataset_generation/test_output/*.pcap
```

## 🔍 Advanced Setup Options

### Remote Server Installation

If you're installing on a remote server (like the example in the original docs):

```bash
# Connect to remote server
ssh user@your-server -p your-port

# Follow the same installation steps above

# Transfer project files if needed
scp -r /local/path/to/AdDDoSSDN_dataset user@your-server:/remote/path/
```

### Docker Installation (Advanced)

For users who prefer containerized environments:

```bash
# Note: This requires Docker to be installed
# Create a Dockerfile (advanced users only)
# The framework requires privileged access for Mininet
```

### Performance Tuning

For better performance on production datasets:

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network buffers
echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## ✅ Installation Verification Checklist

Before proceeding to generate datasets, verify:

- [ ] **Ubuntu system** with sudo access
- [ ] **Mininet installed** and `sudo mn --test pingall` works
- [ ] **Ryu controller installed** and `ryu-manager --version` works
- [ ] **tshark installed** and accessible
- [ ] **slowhttptest installed** and accessible  
- [ ] **Python virtual environment** created and activated
- [ ] **Framework dependencies** installed via pip
- [ ] **Test script runs successfully** and creates output files
- [ ] **Output directory** contains PCAP and CSV files
- [ ] **Log files** show no critical errors

## 🎯 Next Steps

Once installation is complete:

1. **📖 Read the [scenario documentation](scenario.md)** to understand what attacks the framework generates
2. **🔧 Customize `config.json`** to adjust attack durations for your needs
3. **🚀 Run `main.py`** to generate full research datasets
4. **📊 Explore [analysis documentation](analysis.md)** to understand the generated features

## 🆘 Getting Additional Help

### If You're Still Having Issues:

1. **Check system logs:**
   ```bash
   dmesg | tail -20
   journalctl -xe | tail -20
   ```

2. **Verify resource availability:**
   ```bash
   free -h  # Check RAM
   df -h    # Check disk space
   ```

3. **Test individual components:**
   ```bash
   # Test Mininet separately
   sudo mn --test pingall
   
   # Test Ryu separately
   timeout 10s ryu-manager ryu.app.simple_switch_13
   ```

4. **Look for detailed error messages** in the log files located in your output directory

### Resources for Learning More:

- **Mininet Documentation:** http://mininet.org/
- **Ryu SDN Framework:** https://ryu-sdn.org/
- **Wireshark/tshark Guide:** https://www.wireshark.org/docs/
- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html

---

**🎉 Congratulations! If you've completed this guide successfully, you're ready to generate cybersecurity datasets. Next, check out the [scenario documentation](scenario.md) to understand what your framework will create.**