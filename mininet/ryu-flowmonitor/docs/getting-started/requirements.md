# System Requirements

Detailed system requirements for the Enhanced Ryu Flow Monitor with DDoS Detection system.

## 🖥️ Hardware Requirements

### Single Server Deployment

#### Minimum Configuration
- **CPU**: 2 cores, 2.0 GHz (Intel i3 or AMD equivalent)
- **RAM**: 4 GB
- **Storage**: 20 GB available space
- **Network**: 100 Mbps Ethernet connection
- **Architecture**: x86_64 (64-bit)

#### Recommended Configuration
- **CPU**: 4+ cores, 2.5+ GHz (Intel i5/i7 or AMD Ryzen)
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: 1 Gbps Ethernet connection
- **Architecture**: x86_64 (64-bit)

#### High-Performance Configuration
- **CPU**: 8+ cores, 3.0+ GHz (Intel i7/i9 or AMD Ryzen 7/9)
- **RAM**: 16+ GB
- **Storage**: 100+ GB NVMe SSD
- **Network**: 10 Gbps Ethernet connection
- **GPU**: Optional CUDA-compatible GPU for ML acceleration

### Multi-Server Deployment

#### Ryu Controller Server
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: 1+ Gbps with low latency to client servers

#### Mininet Client Server
- **CPU**: 4+ cores, 2.5+ GHz
- **RAM**: 8+ GB (16+ GB for large topologies)
- **Storage**: 100+ GB SSD (for traffic captures)
- **Network**: 1+ Gbps with low latency to controller

#### Network Infrastructure
- **Latency**: < 10ms between servers
- **Bandwidth**: 1+ Gbps dedicated bandwidth
- **Reliability**: Redundant network paths recommended

## 💻 Software Requirements

### Operating System Support

#### Fully Supported
- **Ubuntu**: 20.04 LTS, 22.04 LTS
- **Debian**: 10 (Buster), 11 (Bullseye)
- **CentOS**: 8, 9 (Stream)
- **Red Hat Enterprise Linux**: 8, 9

#### Partially Supported
- **Fedora**: 35, 36, 37
- **openSUSE**: Leap 15.3+
- **Arch Linux**: Rolling release
- **Other Linux**: Manual dependency installation required

#### Not Supported
- **Windows**: Not supported (use WSL2 or VM)
- **macOS**: Limited support (development only)
- **FreeBSD/OpenBSD**: Not tested

### Python Requirements

#### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.9 or 3.10
- **Maximum**: Python 3.11 (some ML libraries may have compatibility issues)

#### Python Packages (Core)
```
ryu >= 4.34
webob >= 1.8.7
eventlet >= 0.33.0
scikit-learn >= 1.0.0
pandas >= 1.3.0
numpy >= 1.21.0
```

#### Python Packages (Optional)
```
torch >= 1.10.0          # Advanced ML features
cicflowmeter >= 0.1.4    # Traffic analysis
flask >= 2.0.0           # Web interface
psutil >= 5.8.0          # System monitoring
scapy >= 2.4.5           # Packet analysis
```

### System Dependencies

#### Network Tools
- **tcpdump**: Packet capture
- **wireshark-common**: Network analysis tools
- **libpcap-dev**: Packet capture library
- **netcat**: Network testing

#### SDN Tools
- **Open vSwitch**: OpenFlow switch implementation
- **Mininet**: Network emulation platform
- **OpenFlow**: Protocol support

#### Development Tools
- **build-essential**: Compilation tools
- **python3-dev**: Python development headers
- **git**: Version control
- **curl/wget**: Download utilities

#### Java Runtime
- **OpenJDK 11+**: Required for CICFlowMeter
- **Oracle JDK 11+**: Alternative Java runtime

## 🔧 Performance Specifications

### CPU Performance

#### Single-Threaded Performance
- **Minimum**: 2000 PassMark CPU score
- **Recommended**: 3000+ PassMark CPU score
- **High-Performance**: 4000+ PassMark CPU score

#### Multi-Threaded Performance
- **Minimum**: 4000 PassMark CPU score
- **Recommended**: 8000+ PassMark CPU score
- **High-Performance**: 15000+ PassMark CPU score

### Memory Requirements

#### Base System
- **OS + Base Services**: 1-2 GB
- **Python Runtime**: 500 MB - 1 GB
- **Ryu Controller**: 500 MB - 2 GB

#### ML Components
- **Scikit-learn Models**: 100-500 MB
- **PyTorch Models**: 500 MB - 2 GB
- **Training Data**: 1-5 GB
- **Feature Buffers**: 100-500 MB

#### Traffic Analysis
- **CICFlowMeter**: 500 MB - 2 GB
- **Packet Captures**: 1-10 GB
- **Flow Statistics**: 100 MB - 1 GB

### Storage Requirements

#### System Installation
- **Operating System**: 10-20 GB
- **Python Environment**: 2-5 GB
- **Application Code**: 100-500 MB

#### Data Storage
- **Traffic Captures**: 10-100 GB (configurable retention)
- **ML Models**: 100 MB - 1 GB
- **Log Files**: 1-10 GB (with rotation)
- **Temporary Files**: 1-5 GB

#### Performance Considerations
- **SSD Recommended**: For better I/O performance
- **RAID Configuration**: Optional for redundancy
- **Network Storage**: Supported for captures and logs

### Network Requirements

#### Bandwidth
- **Control Traffic**: 1-10 Mbps
- **Data Plane**: Depends on simulated network
- **ML Synchronization**: 1-100 Mbps
- **Web Interface**: 1-10 Mbps

#### Latency
- **Controller-Switch**: < 10ms recommended
- **Inter-Controller**: < 50ms for federated learning
- **Web Interface**: < 100ms for good UX

#### Ports and Protocols
- **TCP 6633**: OpenFlow (primary controller)
- **TCP 6634**: OpenFlow (client controller)
- **TCP 8080**: Web interface (primary)
- **TCP 8081**: Web interface (client)
- **TCP 9999**: Federated learning communication

## 🔒 Security Requirements

### System Security
- **User Privileges**: Non-root user recommended
- **Firewall**: Configure appropriate port access
- **SSH Access**: Secure remote access
- **File Permissions**: Proper file system permissions

### Network Security
- **VPN/Private Network**: For multi-server communication
- **SSL/TLS**: For web interface (optional)
- **Authentication**: Basic auth for web interface
- **Access Control**: IP-based restrictions

## 📊 Scalability Limits

### Single Server Limits
- **Switches**: Up to 100 OpenFlow switches
- **Flows**: Up to 10,000 concurrent flows
- **Packets/Second**: Up to 10,000 pps
- **Detection Latency**: 50-200ms

### Multi-Server Limits
- **Controllers**: Up to 10 federated controllers
- **Switches**: Up to 1,000 OpenFlow switches
- **Flows**: Up to 100,000 concurrent flows
- **Packets/Second**: Up to 100,000 pps
- **Detection Latency**: 100-500ms

### Performance Tuning
- **CPU Cores**: More cores improve ML training
- **Memory**: More RAM allows larger models
- **Storage**: SSD improves I/O performance
- **Network**: Higher bandwidth reduces latency

## 🧪 Testing Requirements

### Development Environment
- **CPU**: 2+ cores
- **RAM**: 4+ GB
- **Storage**: 20+ GB
- **Network**: Local network sufficient

### Testing Environment
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB
- **Network**: Isolated test network

### Production Environment
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Storage**: 100+ GB
- **Network**: Production network with monitoring

## ⚠️ Known Limitations

### Platform Limitations
- **Windows**: Not natively supported
- **ARM Architecture**: Limited testing
- **32-bit Systems**: Not supported

### Software Limitations
- **Python 3.12+**: May have compatibility issues
- **Old Linux Kernels**: < 4.0 not recommended
- **Limited IPv6**: Primarily IPv4 focused

### Performance Limitations
- **Single-threaded**: Some components not multi-threaded
- **Memory Usage**: ML models can be memory-intensive
- **Disk I/O**: Heavy logging can impact performance

---

**Next**: [Architecture Overview](architecture.md)  
**Previous**: [Installation Guide](installation.md)
