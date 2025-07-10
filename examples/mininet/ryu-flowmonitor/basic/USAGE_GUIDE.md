# 🌐 SDN Web GUI - Complete Usage Guide

## 📋 What You Now Have

I've created a comprehensive web-based GUI for your SDN setup that includes:

### 🎯 Core Components
- **`web_gui.py`** - Main Flask web application with WebSocket support
- **`templates/index.html`** - Modern, responsive web interface
- **`start_gui.py`** - Easy startup script with dependency checking
- **`test_setup.py`** - Setup verification script
- **`requirements.txt`** - Python dependencies

### 🚀 Features
- **Real-time monitoring** of both Ryu controller and Mininet network
- **Interactive controls** to start/stop services
- **Live command execution** in Mininet CLI
- **System logging** with color-coded messages
- **Network topology visualization**
- **WebSocket-based updates** for real-time status

## 🛠️ Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify Setup
```bash
python test_setup.py
```

### Step 3: Start the Web GUI
```bash
python start_gui.py
```

### Step 4: Access the Interface
Open your browser and go to: **http://localhost:5000**

## 🎮 How to Use the Web GUI

### 1. Starting Your SDN System

**Order is important:**

1. **Start Ryu Controller First**
   - Click "▶️ Start Controller" in the left panel
   - Wait for green status indicator
   - Controller runs `simple_switch_13.py`

2. **Configure Network Interface**
   - Enter your hardware interface (default: `ens32`)
   - Common options: `eth0`, `ens32`, `enp0s3`

3. **Start Mininet Network**
   - Click "▶️ Start Network" in the right panel
   - Network creates topology from `custom5.py`

### 2. Using Mininet Commands

Once network is running, try these commands:

```bash
# Test all host connectivity
pingall

# Ping between specific hosts
h2 ping h3

# Show network topology
net

# Display all information
dump

# Check host IPs
h2 ifconfig
```

### 3. Monitoring

- **Status Indicators**: 🟢 Green = Running, 🔴 Red = Stopped
- **Live Logs**: Scroll down to see real-time system messages
- **Network Topology**: Visual representation of your 4-host setup

## 🏗️ Your Network Topology

```
Hardware Interface (ens32)
│
🔄 OpenFlow Switch (s1)
├── 💻 Host h2 (10.0.0.2/24)
├── 💻 Host h3 (10.0.0.3/24)
├── 💻 Host h4 (10.0.0.4/24)
└── 💻 Host h5 (10.0.0.5/24)
```

## 🔧 Customization Options

### Change Controller IP
Edit `custom5.py` line 37:
```python
c0 = net.addController('c0', controller=RemoteController, ip='YOUR_IP', port=6633)
```

### Add More Hosts
Modify `custom5.py`:
```python
h6 = net.addHost('h6', ip='10.0.0.6/24')
net.addLink(h6, s1)
```

### Change Web Server Port
Edit `start_gui.py` or `web_gui.py`:
```python
socketio.run(app, host='0.0.0.0', port=YOUR_PORT)
```

## 🐛 Troubleshooting

### Common Issues & Solutions

**"Interface does not exist"**
```bash
# Check available interfaces
ip link show
# Update interface name in web GUI
```

**Permission denied**
```bash
# Run with elevated privileges
sudo python start_gui.py
```

**Controller connection failed**
- Ensure Ryu controller started first
- Check firewall settings
- Verify IP in `custom5.py`

**Web interface not loading**
- Check if port 5000 is available
- Try different port
- Check firewall settings

## 📊 Advanced Features

### Real-time Updates
- Status changes appear instantly
- Logs update in real-time
- No need to refresh the page

### Command History
- Previous commands are logged
- Results shown in real-time
- Error messages highlighted

### System Monitoring
- Process status tracking
- Resource usage display
- Connection monitoring

## 🎯 Best Practices

1. **Always start controller before network**
2. **Use `pingall` to test connectivity**
3. **Monitor logs for troubleshooting**
4. **Stop network before stopping controller**
5. **Use proper interface names**

## 📝 File Structure Summary

```
basic/
├── 🌐 web_gui.py              # Main web application
├── 🎛️ simple_switch_13.py     # Your Ryu controller
├── 🔗 custom5.py              # Your Mininet topology
├── 🚀 start_gui.py            # Easy startup script
├── 🧪 test_setup.py           # Setup verification
├── 📋 requirements.txt        # Dependencies
├── 📖 README.md              # Detailed documentation
├── 📘 USAGE_GUIDE.md         # This guide
└── 📁 templates/
    └── 🎨 index.html         # Web interface
```

## 🎉 What's Next?

Your web GUI is now ready! You can:

1. **Start using it immediately** with the existing setup
2. **Customize the topology** by modifying `custom5.py`
3. **Enhance the controller** by extending `simple_switch_13.py`
4. **Add more features** to the web interface

The web GUI provides a modern, user-friendly way to manage your SDN setup without needing to remember command-line syntax or manage multiple terminal windows.

## 🆘 Need Help?

- Check the logs in the web interface
- Run `python test_setup.py` to verify setup
- Review the README.md for detailed information
- Ensure all dependencies are installed
