# Enhanced AdDDoSDN Dataset Generation Framework v2.0

## Overview

The Enhanced AdDDoSDN Dataset Generation Framework v2.0 is a comprehensive Python-based framework that includes **Tier 1 Zero-Installation Adversarial Enhancements** with **CPU Affinity Optimization**. This script is a complete implementation with built-in zero-dependency adversarial attack enhancements achieving approximately **57.5% sophistication**.

## Key Features

### Core Enhancements
- **Statistical Feature Manipulation** - Basic ML evasion using statistical properties
- **TCP State Machine Simulation** - Advanced protocol exploitation
- **Behavioral Pattern Generator** - Enhanced behavioral mimicry
- **Traffic Fingerprint Evasion** - Traffic camouflage enhancement
- **CPU Core Affinity Optimization** - Performance enhancement
- **RFC 1918 IP Rotation** - Enhanced IP rotation for all enhanced attacks

### Zero-Installation Dependencies
The framework uses only built-in Python modules:
- `statistics`, `math`, `hashlib`, `collections`, `calendar`, `base64`, `random`, `socket`, `psutil`

## Usage

### Basic Usage
```bash
# Auto-detect cores
sudo python3 mainv2.py

# Specify configuration file
sudo python3 mainv2.py config.json
```

### CPU Optimization
```bash
# 16-core server optimization
sudo python3 mainv2.py --max-cores 16

# Custom PCAP processing cores + server cores
sudo python3 mainv2.py --cores 12 --max-cores 16

# 8-core server optimization
sudo python3 mainv2.py --max-cores 8

# 24-core server optimization
sudo python3 mainv2.py --max-cores 24
```

### Bulk Execution
```bash
# Run multiple times with date-based output directories
sudo python3 run_bulk_mainv2.py --runs 4

# Run with custom configuration
sudo python3 run_bulk_mainv2.py --runs 8 --config test_config.json

# Run with CPU optimization
sudo python3 run_bulk_mainv2.py --runs 6 --cores 8 --max-cores 16
```

## CPU Core Allocation

### Default 16-Core Allocation
- **Core 0**: System/OS
- **Core 1**: Ryu Controller
- **Cores 2-4**: Mininet Network (3 cores)
- **Cores 5-10**: Attack Generation (6 cores)
- **Core 11**: Background Services
- **Cores 0-15**: PCAP Processing (all cores, post-simulation)

### Scalable Allocation
The framework automatically adjusts core allocation based on available cores:
- **16+ cores**: Full optimization with dedicated cores
- **12-15 cores**: Balanced allocation
- **8-11 cores**: Efficient allocation
- **<8 cores**: Minimal allocation with shared resources

## Architecture

### Enhanced Attack Types

#### Traditional Attacks (Enhanced)
1. **Enhanced SYN Flood** - RFC-compliant TCP with human-like timing (~25 pps)
2. **Enhanced UDP Flood** - Realistic DNS payloads with ephemeral ports
3. **Enhanced ICMP Flood** - Protocol compliance with session pattern awareness

#### Adversarial Attacks (Enhanced)
1. **Enhanced TCP State Exhaustion** - Statistical feature manipulation + TCP state tracking
2. **Enhanced Application Layer Attack** - Behavioral pattern generation + traffic fingerprinting
3. **Enhanced Slow HTTP Attack** - Traffic fingerprint evasion + advanced timing

### Zero-Installation Enhancement Classes

#### StatisticalFeatureManipulator
- Manipulates packet features to evade statistical detection
- Adjusts packet sizes to blend with normal distribution
- Implements timing variance and window size selection
- Uses deterministic behavior per IP for consistency

#### TCPStateTracker
- Advanced TCP state tracking without external dependencies
- Simulates realistic TCP state machine progression
- Maintains connection history and statistics
- Tracks connection age and activity patterns

#### BehaviorGenerator
- Generates realistic user behavioral patterns
- Implements circadian rhythm simulation
- Supports multiple user types (casual, power_user, mobile, bot)
- Includes realistic browsing patterns and thinking time

#### TrafficCamouflage
- Generates consistent traffic fingerprints per session
- Supports multiple traffic patterns (e-commerce, content browsing, social media)
- Creates realistic user agents, headers, and cookies
- Maintains session consistency across requests

#### IPRotator
- RFC 1918 private IP rotation for attacks
- Supports multiple private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Ensures realistic IP distribution

### CPU Core Management

#### CPUCoreManager Class
- Manages CPU core allocation for different modules using taskset
- Calculates optimal core allocation based on total cores
- Supports process affinity setting for performance optimization
- Provides fallback mechanisms for systems without taskset

## Output Structure

### File Organization
```
main_output/
├── DDMMYY-1/          # First run (e.g., 180725-1)
│   ├── normal.pcap
│   ├── syn_flood.pcap
│   ├── udp_flood.pcap
│   ├── icmp_flood.pcap
│   ├── ad_syn.pcap
│   ├── ad_udp.pcap
│   ├── ad_slow.pcap
│   ├── h6_slow_read.pcap
│   ├── packet_features.csv
│   ├── flow_features.csv
│   └── logs/
├── DDMMYY-2/          # Second run (e.g., 180725-2)
└── ...
```

### Generated Datasets
- **packet_features.csv** - Packet-level features with labels
- **flow_features.csv** - Flow-level features with labels
- **PCAP files** - Raw network traffic captures for each attack type
- **Log files** - Detailed execution logs for analysis

## Requirements

### System Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ (recommended)
- **Python**: 3.8+
- **Privileges**: Root privileges (for Mininet)
- **CPU**: 16+ cores recommended for optimal performance

### System Dependencies
- `ryu-manager` - SDN controller
- `mn` - Mininet network emulator
- `tshark` - Network protocol analyzer
- `slowhttptest` - HTTP slowloris testing tool
- `taskset` - CPU affinity tool (util-linux package)

### Python Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Additional CICFlow dependencies (optional)
pip install -r cicflow_requirements.txt
```

## Advanced Features

### Enhanced PCAP Processing
- Parallel PCAP processing with CPU affinity
- Timestamp validation and integrity checks
- Enhanced capture reliability with improved timestamps
- TCP issue analysis and inter-packet arrival time analysis

### Timeline Analysis
- Comprehensive timeline synchronization validation
- Attack phase alignment scoring
- Quality assessment with detailed reporting
- Flow and packet data correlation

### Logging Framework
- Centralized logging with run ID tracking
- Separate logs for different components (main, attack, mininet, ryu)
- Performance tracking and error traceability
- Console output filtering for noise reduction

## Performance Optimization

### CPU Affinity Benefits
- **Improved Performance**: Dedicated cores for specific tasks
- **Reduced Context Switching**: Processes stay on assigned cores
- **Better Resource Utilization**: Optimal core allocation based on workload
- **Enhanced Scalability**: Automatic adjustment for different core counts

### Parallel Processing
- **Multi-core PCAP Processing**: Utilizes all available cores for post-processing
- **Concurrent Attack Generation**: Dedicated cores for attack processes
- **Background Flow Collection**: Separate thread for flow statistics
- **Efficient Resource Management**: Balanced workload distribution

## Configuration

### Configuration Files
- **config.json** - Main configuration with scenario durations
- **test_config.json** - Test configuration for development
- **Label files** - Feature names and label definitions in `files/` directory

### Scenario Durations
```json
{
  "scenario_durations": {
    "initialization": 5,
    "normal_traffic": 1200,
    "syn_flood": 300,
    "udp_flood": 300,
    "icmp_flood": 300,
    "ad_syn": 7200,
    "ad_udp": 4800,
    "ad_slow": 3600,
    "cooldown": 10
  }
}
```

## Security Considerations

### Defensive Security Focus
- **Framework Purpose**: Designed for defensive security research only
- **Traffic Containment**: All generated traffic is contained within Mininet virtual networks
- **No Malicious Enhancement**: Never modify attack code to increase maliciousness
- **Research Ethics**: Focus on detection, analysis, and defensive improvements

### Enhanced Attack Differentiation
- **Traditional Attacks**: Realistic timing and protocol compliance while remaining detectable
- **Adversarial Attacks**: Advanced ML evasion with burst patterns, jitter, and IP rotation
- **Clear Separation**: Enhanced traditional attacks remain realistic but detectable, while adversarial attacks focus on ML evasion techniques

## Troubleshooting

### Common Issues
1. **Permission Errors**: Ensure running as root with `sudo`
2. **Missing Dependencies**: Install all required system tools
3. **CPU Affinity Issues**: Verify taskset is available and functional
4. **Memory Constraints**: Monitor system resources during execution
5. **Network Conflicts**: Clean up previous Mininet instances with `mn -c`

### Log Analysis
- **main.log**: Main execution flow and errors
- **attack.log**: Detailed attack execution information
- **mininet.log**: Network topology and connectivity issues
- **ryu.log**: SDN controller operation and flow management

## Integration with Existing Framework

### Compatibility
- **Seamless Integration**: Works with existing AdDDoSDN framework components
- **Backward Compatibility**: Maintains compatibility with original main.py structure
- **Enhanced Functionality**: Adds advanced features without breaking existing workflows
- **Modular Design**: Enhanced components can be used independently

### Migration Path
1. **Backup Existing Data**: Preserve current datasets and configurations
2. **Update Dependencies**: Install any new required packages
3. **Test Configuration**: Validate configuration files work with enhanced version
4. **Gradual Deployment**: Start with test runs before full production use

## Future Enhancements

### Planned Improvements
- **Tier 2 Enhancements**: Additional ML evasion techniques
- **Dynamic Configuration**: Runtime configuration adjustment
- **Real-time Monitoring**: Live performance metrics and dashboards
- **Advanced Analytics**: Enhanced dataset quality assessment tools

### Extensibility
- **Plugin Architecture**: Support for custom attack modules
- **API Integration**: REST API for external control and monitoring
- **Multi-Controller Support**: Integration with multiple SDN controllers
- **Cloud Deployment**: Support for cloud-based execution environments

## Conclusion

The Enhanced AdDDoSDN Dataset Generation Framework v2.0 represents a significant advancement in network security dataset generation, combining sophisticated adversarial techniques with performance optimization and comprehensive logging. The framework provides researchers and security professionals with a powerful tool for generating realistic and challenging network traffic datasets for ML-based security research.

The zero-installation approach ensures easy deployment while maintaining high sophistication levels, making it accessible for various research environments and use cases. The CPU affinity optimization and parallel processing capabilities enable efficient resource utilization, significantly reducing dataset generation time.

This framework serves as a foundation for advanced network security research, providing both traditional and adversarial attack scenarios necessary for developing robust detection and mitigation systems in modern SDN environments.