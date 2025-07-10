# 🚀 Quick Start Guide - SDN Web GUI

## ✅ For Your Environment (Flask 1.1.4 + Python 2.7/3.x)

Since you already have Flask 1.1.4 installed, you can use the **minimal version** which is compatible with your setup.

### 🎯 Option 1: Minimal Web GUI (Recommended for your setup)

This version works with your existing Flask installation and doesn't require additional dependencies.

```bash
# 1. Navigate to the basic directory
cd ~/ryu-script/basic

# 2. Start the minimal web GUI
python3 run_minimal.py
```

**Access the interface at:** `http://localhost:5000`

### 🎯 Option 2: Full Web GUI (If you want real-time features)

If you want the full-featured version with real-time updates, you'll need to install compatible dependencies:

```bash
# 1. Install compatible versions
pip3 install --user "Flask>=1.1.0,<3.0.0" "Flask-SocketIO>=4.0.0,<6.0.0" "psutil>=5.0.0"

# 2. Start the full web GUI
python3 start_gui.py
```

## 🎮 How to Use

### Step 1: Start Ryu Controller
1. Click "▶️ Start Controller" 
2. Wait for status to show "Running"

### Step 2: Start Mininet Network
1. Enter your interface name (default: `ens32`)
2. Click "▶️ Start Network"
3. Wait for status to show "Running"

### Step 3: Test Your Network
Use the command box to run:
- `pingall` - Test connectivity between all hosts
- `h2 ping h3` - Ping from host h2 to h3
- `net` - Show network topology
- `dump` - Display all network information

## 📁 Files Created for You

```
basic/
├── 🌐 minimal_gui.py           # Minimal web interface (Flask 1.1.4 compatible)
├── 🚀 run_minimal.py           # Easy startup for minimal version
├── 🎨 templates/
│   ├── minimal_index.html      # Simple web interface
│   ├── simple_index.html       # Alternative interface
│   └── index.html              # Full-featured interface
├── 📋 web_gui.py               # Full web application (needs newer Flask)
├── 🛠️ start_gui.py             # Startup script for full version
├── 🧪 test_setup.py            # Setup verification
├── 📖 requirements.txt         # Dependencies (flexible versions)
├── 📘 README.md               # Detailed documentation
├── 📋 USAGE_GUIDE.md          # Complete usage guide
└── 🚀 QUICK_START.md          # This file
```

## 🔧 Troubleshooting

### "Interface does not exist" Error
```bash
# Check available interfaces
ip link show

# Common interface names:
# - ens32, ens33 (VMware)
# - eth0, eth1 (Traditional)
# - enp0s3, enp0s8 (VirtualBox)
```

### Permission Issues
```bash
# Run with sudo if needed
sudo python3 run_minimal.py
```

### Port 5000 Already in Use
```bash
# Check what's using port 5000
sudo netstat -tulpn | grep :5000

# Kill the process or edit the script to use a different port
```

## 🎯 What Each Version Offers

### Minimal Version (`minimal_gui.py`)
- ✅ Works with Flask 1.1.4
- ✅ Start/stop controller and network
- ✅ Execute Mininet commands
- ✅ View logs and status
- ✅ Auto-refresh every 30 seconds
- ❌ No real-time updates

### Full Version (`web_gui.py`)
- ✅ All minimal features
- ✅ Real-time WebSocket updates
- ✅ Live status monitoring
- ✅ Advanced logging
- ❌ Requires newer Flask/dependencies

## 🎉 Success Indicators

When everything is working, you should see:
1. **Green status** for both controller and network
2. **Logs showing** successful starts
3. **Commands executing** without errors
4. **Ping tests** showing connectivity

## 📞 Quick Commands to Test

Once your network is running, try these in the web interface:

```bash
# Test all connectivity
pingall

# Test specific hosts
h2 ping -c 3 h3

# Show network info
net

# Display topology
dump

# Check host IPs
h2 ifconfig
```

## 🎯 Next Steps

1. **Start with minimal version** to ensure everything works
2. **Test basic functionality** with pingall
3. **Experiment with commands** in the web interface
4. **Upgrade to full version** if you want real-time features

Your SDN web GUI is now ready to use! 🎉
