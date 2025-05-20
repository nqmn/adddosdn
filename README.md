# AD-DDoSDN2025 Dataset Workflow

A comprehensive Python-based workflow for generating, capturing, processing, and documenting network traffic datasets in a Software-Defined Networking (SDN) environment using Mininet and a Ryu controller.

This is a unified Python toolkit that lets you:

1. **Launch a suite of adversarial DDoS attacks** (TCP SYN, UDP, ICMP, HTTP floods) with evasion, hybrid, randomized timing, and adaptive-rate options. This covers both high rate and low rate DDoS attacks. 
2. **Automate an SDN dataset pipeline** in Mininet + Ryu (or remote) controller: topology setup, traffic capture, CICFlowMeter flow extraction, labeling, merging, REST flow stats, and Markdown docs.

---

## 📦 Repository Structure

```
├── sdn_dataset_workflow.py   # Main script
├── README.md                 # This documentation
└── examples/                 # (Optional) Sample Ryu app & config files
```

---

## 🔧 Prerequisites

- **Operating System:** Linux (Ubuntu recommended)
- **Python 3.7+**
- **Mininet**:
  ```bash
  sudo apt-get install mininet
  ```
- **Ryu SDN Framework** (if using Ryu controller):
  ```bash
  pip install ryu
  ```
- **Python dependencies**:
  ```bash
  pip install psutil pandas requests scapy
  ```
- **CICFlowMeter** (for feature extraction):
  - Download and install from [CICFlowMeter GitHub](https://github.com/ahlashkari/CICFlowMeter)
  - Ensure `cicflowmeter` CLI is in your `PATH`.

---

## 🚀 Usage Examples

### 1. Run full SDN dataset workflow (with Ryu)

```bash
python sdn_dataset_workflow.py \
  --controller-type ryu \
  --ryu-app ryu/app/simple_switch_13.py \
  --controller-port 6633 \
  --output ./sdn_datasets
```

This will:
1. Launch Ryu (`ryu-manager`) with the specified app.  
2. Start Mininet topology (3 switches, 6 hosts).  
3. Generate normal + attack traffic, capture PCAPs.  
4. Extract flows via CICFlowMeter, label & merge datasets.  
5. Collect flow stats from controller via REST.  
6. Produce final CSV & Markdown documentation in `./sdn_datasets/`.

### 2. Connect to existing remote controller

```bash
python sdn_dataset_workflow.py \
  --controller-type remote \
  --controller-ip 192.168.56.101 \
  --controller-port 6653 \
  --output ./sdn_datasets
```

---

### 3. Run adversarial attack suite

Choose one or fire them all:

- **TCP SYN Flood** (`--run-all` or call `send_hybrid_attack`, `send_packet_randomized`, `send_mimic_traffic`, `send_evasive_traffic`, `adaptive_attack` directly in code)
- **UDP Flood** (with randomized ports)
- **ICMP Ping Flood**
- **HTTP Request Mimicry**
- **Hybrid Mix**: interleave normal ICMP ping + TCP SYN flood
- **Randomized Timing**: random delays (10–100 ms)
- **Evasion Techniques**: random TTL and window sizes, fragmentation
- **Adaptive Rate**: adjust flood rate based on CPU usage of attack host

**Quick Attack-Only Run**:
```bash
python sdn_dataset_workflow.py --run-all
```

This fires all custom attack variants (hybrid, evasive, randomized, mimic, adaptive) between host `10.0.0.1` and `10.0.0.2`.

---

## 🔍 Customization

- **Topology:** Modify `create_topology()` to add more switches/hosts or different link characteristics.
- **Ryu App:** Swap the `--ryu-app` argument to point to your own controller logic.
- **Attack Profile:** Tweak traffic volume, durations, and parameters in the various `send_*` functions.
- **Feature Extraction:** Configure additional flags or plug in alternative flow extractors.

---

## Updated with Advanced Adversarial Attacks

**Here are the major improvements:**
1. Advanced Evasion Mechanisms

- **IP Rotation System:** Implements a systematic IP address rotation system that avoids reusing source IPs too frequently
- Protocol Fingerprinting Evasion: Randomizes TCP parameters (window sizes, TTL, sequence numbers) to avoid signature-based detection
- Temporal Pattern Avoidance: Uses variable timing between packets and connections to prevent timing-based detection

2. Sophisticated Attack Vectors

Slow Read Attack: Implements the "Slowloris" technique that establishes legitimate connections but reads responses extremely slowly, exhausting server connection pools
TCP State Exhaustion: Advanced version that correctly manipulates TCP state by sending valid handshakes but keeping connections half-open
Distributed Application Layer Attack: Targets resource-intensive endpoints with semantically valid HTTP requests

3. Legitimate Traffic Mimicry

HTTP Header Manipulation: Uses realistic HTTP headers, User-Agents, and referrers to appear legitimate
Session Maintenance: Creates and maintains persistent sessions with cookies and realistic browsing patterns
Request Diversity: Varies HTTP methods, paths, and parameters to mimic real user behavior

4. Intelligent Adaptation

Defensive Countermeasure Detection: Probes for WAFs, rate limiting, or other defenses
Adaptive Attack Parameters: Adjusts attack intensity and technique based on target response times
Multi-threaded Coordination: Executes multiple attack vectors simultaneously with coordinated timing

5. Monitoring and Feedback Loop

Response Time Monitoring: Tracks target performance to gauge attack effectiveness
Defense Detection: Identifies when protection mechanisms activate (Cloudflare, captchas, WAFs)
Dynamic Strategy Switching: Changes attack vectors when current methods are detected or blocked


## 📝 License

This project is provided under the MIT License. Feel free to adapt and extend for research purposes.

---

*Generated by the SDN Dataset Workflow team.*

