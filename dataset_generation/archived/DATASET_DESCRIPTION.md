The AdDDoSDN dataset is a comprehensive collection of network traffic data specifically designed for defensive security research in Software-Defined Networking (SDN) environments, capturing sophisticated DDoS attacks and normal network behavior through controlled experimentation using Mininet emulation and Ryu SDN controller to provide researchers with high-quality, labeled data for developing and evaluating DDoS detection systems. The dataset is generated using a carefully designed SDN topology consisting of six hosts connected through an OpenFlow 1.3 switch controlled by a Ryu controller, including two dedicated attackers (h1: 10.0.0.1, h2: 10.0.0.2), two normal traffic generators (h3: 10.0.0.3, h5: 10.0.0.5), and two victim servers (h4: 10.0.0.4, h6: 10.0.0.6), enabling realistic simulation of both attack and benign traffic patterns while maintaining complete observability through the centralized SDN controller.

The dataset follows a structured 7-phase attack sequence spanning approximately 6.5 hours per dataset generation cycle, with each phase representing a distinct traffic pattern including network initialization, normal traffic baseline (1 hour), SYN flood attack (5 minutes), UDP flood attack (5 minutes), ICMP flood attack (5 minutes), adversarial TCP state exhaustion (2 hours), adversarial application layer mimicry (80 minutes), and adversarial slow read attack (1 hour), ensuring comprehensive coverage of different attack vectors while maintaining realistic temporal patterns. The dataset uniquely differentiates between Traditional attacks and Adversarial attacks, where Traditional attacks incorporate human-like timing patterns (80-150ms intervals), protocol compliance (RFC-compliant TCP options, realistic DNS queries), and session modeling while maintaining detectability through rate-based rules (~25 packets/second), while Adversarial attacks focus on ML evasion techniques with low packet rates (~0.3 packets/second), IP rotation, burst patterns with jitter, and sophisticated mimicry techniques designed to bypass detection systems.

The dataset provides three synchronized data formats extracted from the same network traffic, optimized for both real-time and offline analysis:

**1. Packet-Level Data (178K records, 15 features)**
- Individual network packets with protocol headers and flags
- **Real-time use**: PCAP files for live packet replay and feature extraction
- **Offline use**: CSV format for batch processing and model training
- Features include packet length, protocol types, ports, and TCP flags

**2. SDN Flow-Level Data (2.7M records, 18 features)**
- OpenFlow statistics from the controller perspective
- **Real-time use**: Direct controller integration for live flow monitoring
- **Offline use**: Flow statistics analysis and temporal pattern recognition
- Features include flow duration, packet counts, byte counts, and flow flags

**3. CICFlow Aggregated Data (34K records, 85 features)**
- Bidirectional flow statistics with comprehensive behavioral features
- **Real-time use**: Sliding window aggregation for behavioral analysis
- **Offline use**: Advanced ML training with statistical flow features
- Features include flow duration statistics, packet size distributions, and timing patterns

Each format serves complementary purposes: packet-level for immediate detection, flow-level for SDN-specific analysis, and CICFlow for advanced behavioral modeling at different temporal abstractions.

The dataset demonstrates exceptional quality containing 2.9 million total records across dataset instances, each representing different temporal scenarios spanning two consecutive days with seven distinct traffic types including normal traffic, SYN flood, UDP flood, ICMP flood, adversarial SYN, adversarial UDP, and adversarial slow attacks.