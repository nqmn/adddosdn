# Ryu Flow Monitor Setup Guide

This guide will help you set up and run the Ryu Flow Monitor system with both the controller and web interface.

## Prerequisites

### System Requirements
- Python 3.7 or higher
- Ryu SDN Framework
- Web browser (Chrome, Firefox, Safari, or Edge)
- OpenFlow-enabled switches or Mininet for testing

### Installation

1. **Install Ryu Framework**
```bash
# Install via pip
pip install ryu

# Or install from source
git clone https://github.com/faucetsdn/ryu.git
cd ryu
pip install -e .
```

2. **Install additional dependencies**
```bash
pip install webob eventlet
```

3. **Install Mininet (for testing)**
```bash
# Ubuntu/Debian
sudo apt-get install mininet

# Or install from source
git clone https://github.com/mininet/mininet
cd mininet
sudo ./util/install.sh -nfv
```

## Quick Start

### Method 1: Using the Complete Setup

1. **Save the Ryu Controller Code**
   - Save the Python controller code as `flow_monitor_controller.py`
   
2. **Save the Web Interface**
   - Save the HTML code as `flow_monitor.html`

3. **Run the Controller**
```bash
# Basic run
ryu-manager flow_monitor_controller.py --observe-links

# With specific port and verbose logging
ryu-manager flow_monitor_controller.py --observe-links --wsapi-port 8080 --verbose
```

4. **Open Web Interface**
   - Open `flow_monitor.html` in your web browser
   - Click "Start Monitoring" to connect to the controller

### Method 2: Using Mininet for Testing

1. **Start the Controller**
```bash
ryu-manager flow_monitor_controller.py --observe-links
```

2. **In another terminal, start Mininet**
```bash
# Simple 3-switch topology
sudo mn --topo linear,3 --controller remote,ip=127.0.0.1,port=6633 --switch ovsk,protocols=OpenFlow13

# Or custom topology
sudo mn --custom your_topology.py --topo custom --controller remote
```

3. **Generate traffic in Mininet**
```bash
# In Mininet CLI
mininet> h1 ping h3
mininet> iperf h1 h2
```

4. **Open Web Monitor**
   - Open the web interface and start monitoring
   - You should see real-time flow data and statistics

## Configuration

### Controller Configuration

The controller accepts several command-line options:

```bash
# Basic usage
ryu-manager flow_monitor_controller.py

# With topology discovery
ryu-manager flow_monitor_controller.py --observe-links

# Custom port and logging
ryu-manager flow_monitor_controller.py --observe-links --wsapi-port 8080 --verbose

# Multiple applications
ryu-manager flow_monitor_controller.py ryu.app.gui_topology.gui_topology --observe-links
```

### Web Interface Configuration

The web interface can be configured by clicking the "Controller Config" button or by modifying the JavaScript:

```javascript
// Default configuration
const config = {
    controllerUrl: 'http://localhost:8080',  // Ryu REST API URL
    endpoints: {
        switches: '/switches',
        flows: '/flows', 
        stats: '/stats',
        topology: '/topology',
        logs: '/logs',
        portStats: '/port_stats'
    }
};
```

## REST API Endpoints

The controller provides the following REST API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/switches` | GET | Get switch information |
| `/flows` | GET | Get flow statistics |
| `/stats` | GET | Get network statistics |
| `/topology` | GET | Get topology data |
| `/logs` | GET | Get activity logs |
| `/port_stats` | GET | Get port statistics |
| `/port_stats/{dpid}` | GET | Get port stats for specific switch |

### Example API Calls

```bash
# Get switch information
curl http://localhost:8080/switches

# Get flow statistics
curl http://localhost:8080/flows

# Get network statistics
curl http://localhost:8080/stats

# Get topology data
curl http://localhost:8080/topology
```

## Features

### Real-time Monitoring
- **Flow Tables**: View OpenFlow rules with match conditions and actions
- **Switch Status**: Monitor switch connections and port states
- **Network Statistics**: Track packet counts, byte rates, and throughput
- **Topology Visualization**: See network topology with switch connections

### Interactive Controls
- **Start/Stop Monitoring**: Connect/disconnect from controller
- **Refresh Intervals**: Configure update frequency (5s to 1min)
- **Manual Refresh**: Force immediate data update
- **Log Management**: View and clear activity logs

### Advanced Features
- **Automatic Fallback**: Switches to simulation mode if controller unavailable
- **CORS Support**: Cross-origin requests for web interface
- **Responsive Design**: Works on desktop and mobile devices
- **Keyboard Shortcuts**: Ctrl+R (refresh), Ctrl+M (start/stop monitoring)

## Troubleshooting

### Common Issues

1. **Connection Failed Error**
   - Check if Ryu controller is running
   - Verify the controller URL in web interface
   - Ensure no firewall blocking port 8080

2. **No Flow Data**
   - Generate traffic in your network
   - Check if switches are connected
   - Verify OpenFlow version compatibility

3. **Topology Not Showing**
   - Run controller with `--observe-links` flag
   - Ensure switches support LLDP
   - Check network topology configuration

4. **CORS Issues**
   - Use a local web server for the HTML file
   - Enable CORS in browser for local files
   - Consider using browser extensions for CORS

### Browser Compatibility

The web interface has been tested with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Advanced Usage

### Custom Topologies

Create custom Mininet topologies:

```python
# custom_topo.py
from mininet.topo import Topo

class CustomTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)
        self.addLink(s1, s2)
        self.addLink(s2, s3)

topos = {'custom': (lambda: CustomTopo())}
```

### Production Deployment

For production use:

1. **Secure the REST API**
   - Add authentication
   - Use HTTPS
   - Implement rate limiting

2. **Database Integration**
   - Store historical data
   - Add data persistence
   - Implement data retention policies

3. **Monitoring Integration**
   - Add Prometheus metrics
   - Integrate with Grafana
   - Set up alerting

## Support

For issues and questions:
- Check Ryu documentation: https://ryu.readthedocs.io/
- Mininet documentation: http://mininet.org/
- OpenFlow specification: https://www.opennetworking.org/

## License

This project is open source and available under the MIT License.