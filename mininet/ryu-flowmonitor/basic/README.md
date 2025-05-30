# SDN Web GUI - Mininet & Ryu Controller Management

A comprehensive web-based interface for managing and monitoring your Software-Defined Network (SDN) setup with Mininet and Ryu controller.

## 🌟 Features

### Ryu Controller Management
- ▶️ Start/Stop Ryu controller (`simple_switch_13.py`)
- 📊 Real-time controller status monitoring
- 🔄 OpenFlow 1.3 support with MAC learning switch functionality
- 📋 Live logging and status updates

### Mininet Network Management
- 🌐 Start/Stop Mininet network topology (`custom5.py`)
- ⚙️ Configurable hardware interface selection
- 💻 Network topology with 4 hosts (h2-h5) connected to switch (s1)
- 🖥️ Interactive command execution in Mininet CLI
- 📡 Real-time network status monitoring

### Web Interface Features
- 🎨 Modern, responsive design
- 🔄 Real-time updates using WebSockets
- 📱 Mobile-friendly interface
- 📋 Live system logs with color-coded messages
- 📊 System status indicators
- 🎛️ Interactive control panels

## 📋 Prerequisites

- Python 3.6 or higher
- Mininet installed and configured
- Ryu controller framework
- Root/sudo access for Mininet operations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Web GUI

```bash
# Method 1: Using the startup script (recommended)
python start_gui.py

# Method 2: Direct execution
python web_gui.py
```

### 3. Access the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

## 🎮 Usage Guide

### Starting the SDN System

1. **Start Ryu Controller First**
   - Click "▶️ Start Controller" in the Ryu Controller panel
   - Wait for the status to show "Running" with green indicator

2. **Configure Network Interface**
   - Enter your hardware interface name (default: `ens32`)
   - Common interfaces: `eth0`, `ens32`, `enp0s3`

3. **Start Mininet Network**
   - Click "▶️ Start Network" in the Mininet Network panel
   - The network will start with the specified interface

### Using Mininet Commands

Once the network is running, you can execute Mininet commands:

```bash
# Test connectivity between all hosts
pingall

# Ping from h2 to h3
h2 ping h3

# Check network interfaces
net

# Display topology
dump
```

### Monitoring

- **Status Indicators**: Green = Running, Red = Stopped
- **System Logs**: Real-time logs appear at the bottom
- **Network Topology**: Visual representation of your network

## 🏗️ Network Topology

```
Hardware Interface (ens32)
│
🔄 Switch (s1)
├── 💻 Host h2 (10.0.0.2/24)
├── 💻 Host h3 (10.0.0.3/24)
├── 💻 Host h4 (10.0.0.4/24)
└── 💻 Host h5 (10.0.0.5/24)
```

## 📁 File Structure

```
basic/
├── web_gui.py              # Main web application
├── simple_switch_13.py     # Ryu controller application
├── custom5.py              # Mininet topology script
├── start_gui.py            # Startup script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── templates/
    └── index.html         # Web interface template
```

## 🔧 Configuration

### Changing the Controller IP

Edit `custom5.py` line 37 to change the controller IP:
```python
c0 = net.addController('c0', controller=RemoteController, ip='YOUR_IP', port=6633)
```

### Changing the Web Server Port

Edit `web_gui.py` or `start_gui.py` to change the port:
```python
socketio.run(app, host='0.0.0.0', port=YOUR_PORT, debug=False)
```

### Adding More Hosts

Modify `custom5.py` to add more hosts to the topology:
```python
h6 = net.addHost('h6', ip='10.0.0.6/24')
net.addLink(h6, s1)
```

## 🐛 Troubleshooting

### Common Issues

1. **"Interface does not exist" Error**
   - Check available interfaces: `ip link show`
   - Update the interface name in the web GUI

2. **Permission Denied**
   - Run with sudo: `sudo python start_gui.py`
   - Ensure user has network privileges

3. **Controller Connection Failed**
   - Verify Ryu controller is running
   - Check firewall settings
   - Ensure correct IP address in `custom5.py`

4. **Web Interface Not Loading**
   - Check if port 5000 is available
   - Try a different port
   - Check firewall settings

### Debug Mode

Enable debug mode by editing `web_gui.py`:
```python
socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

## 📝 Logs

System logs are displayed in real-time in the web interface and include:
- Controller start/stop events
- Network creation/destruction
- Command execution results
- Error messages and warnings

## 🤝 Contributing

Feel free to enhance this web GUI by:
- Adding more monitoring features
- Implementing flow table visualization
- Adding network statistics
- Improving the user interface

## 📄 License

This project is part of the SDN research framework and follows the same licensing terms as the parent project.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the system logs in the web interface
3. Ensure all prerequisites are met
4. Verify file permissions and network configuration
