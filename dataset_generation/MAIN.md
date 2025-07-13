# Dataset Generation Framework

This document outlines the usage, logic, and expected outputs of the `main.py` script, which orchestrates the generation of a comprehensive DDoS attack dataset within an SDN environment using Mininet emulation and Ryu controller.

## Prerequisites

To run this script, ensure you have the following installed on an Ubuntu system:

*   **Python 3** with required packages (see `requirements.txt`)
*   **Mininet:** A network emulator for rapid prototyping of SDN
*   **Ryu:** An SDN controller framework 
*   **TShark:** A network protocol analyzer (part of Wireshark)
*   **Slowhttptest:** A tool for testing web servers for slow HTTP attacks

Install system dependencies:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git default-jre tshark slowhttptest
sudo apt install -y mininet ryu-manager
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

The script requires root privileges to run Mininet. It uses configurable durations from `config.json` for production dataset generation.

```bash
sudo python3 main.py
```

### Key Features
- **Production Ready**: Uses realistic attack durations from config.json
- **Dual-Level Data Collection**: Captures both packet-level and flow-level features
- **Comprehensive Logging**: Detailed execution logs with timing summaries
- **Advanced PCAP Processing**: Timestamp validation and integrity checks
- **Real-time Flow Collection**: Concurrent flow statistics gathering via REST API
- **Configurable**: All attack durations customizable via config.json

## Script Logic and Flow

The `main.py` script automates the following steps:

1.  **Environment Setup:**
    *   **Cleanup:** Clears any previous Mininet instances to ensure a clean slate
    *   **Tool Verification:** Checks for required tools (`ryu-manager`, `mn`, `tshark`, `slowhttptest`) and logs versions
    *   **Ryu Controller Initialization:** Starts the Ryu SDN controller application (`src/controller/ryu_controller_app.py`) in background
    *   **Controller Health Check:** Verifies controller is listening on port 6653 and tests `/hello` REST endpoint
    *   **Mininet Network Creation:** Builds custom topology with 1 switch (`s1`) and 6 hosts (`h1`-`h6`) using ScenarioTopo class
    *   **Connectivity Test:** Runs `pingAll` to confirm network connectivity between all hosts

2.  **Traffic Generation Scenario:**
    The script orchestrates a multi-phase traffic generation process with concurrent packet and flow data collection:

    *   **Phase 1: Initialization:** Brief startup phase. Duration: configurable via `config.json` (default: 5s)
    *   **Phase 2: Normal Traffic:**
        *   Captures benign traffic to `main_output/normal.pcap`
        *   Generates legitimate traffic between hosts using `run_benign_traffic`
        *   Duration: configurable via `config.json` (varies by configuration)
    *   **Phase 3.1: Traditional DDoS Attacks:**
        | Attack Type | Source | Destination | Implementation | Attack Script |
        |---|---|---|---|---|
        | SYN Flood | `h1` | `h6` | TCP handshake exhaustion | `gen_syn_flood.py` |
        | UDP Flood | `h2` | `h4` | UDP traffic overwhelming | `gen_udp_flood.py` |
        | ICMP Flood | `h2` | `h4` | ICMP echo request flood | `gen_icmp_flood.py` |
    *   **Phase 3.2: Adversarial DDoS Attacks:**
        | Attack Type | Source | Destination | Implementation | Attack Script |
        |---|---|---|---|---|
        | Adversarial TCP State Exhaustion | `h2` | `h6` | Advanced SYN flood evasion | `gen_advanced_adversarial_ddos_attacks.py` |
        | Adversarial Application Layer | `h2` | `h6` | Application layer mimicry | `gen_advanced_adversarial_ddos_attacks.py` |
        | Adversarial Slow Read | `h2` | `h6` | Slow HTTP read attack with server setup | `gen_advanced_adversarial_ddos_attacks.py` |
    *   **Phase 4: Cooldown:** Final phase to collect remaining flow data. Duration: configurable via `config.json` (default: 10s)

3.  **Data Collection and Dataset Creation:**
    *   **Concurrent Flow Statistics Collection:** 
        *   Background thread continuously polls Ryu controller's REST API (`/flows` endpoint)
        *   Real-time flow statistics collection with timestamp synchronization
        *   Data saved to `main_output/flow_features.csv` with calculated metrics (packet rate, byte rate, avg packet size)
    *   **Advanced PCAP Processing:** For each generated PCAP file:
        *   **Integrity Verification:** `verify_pcap_integrity` checks for corruption and valid packet structure
        *   **Timestamp Validation:** `validate_and_fix_pcap_timestamps` corrects timing inconsistencies
        *   **Enhanced Feature Extraction:** `enhanced_process_pcap_to_csv` extracts comprehensive network features
        *   **Dynamic Labeling:** Real-time timeline matching for accurate phase-based labeling
    *   **Packet-Level Dataset Consolidation:** 
        *   All temporary CSV files concatenated into unified dataset
        *   Consistent labeling across all traffic phases
        *   Final output: `main_output/packet_features.csv`
    *   **Specialized Analysis:**
        *   TCP connection analysis for slow read attacks (`analyze_pcap_for_tcp_issues`)
        *   Inter-packet arrival time analysis (`analyze_inter_packet_arrival_time`)
        *   Additional capture for h6 during slow read attacks (`h6_slow_read.pcap`)

4.  **Comprehensive Logging and Monitoring:**
    *   **Multi-Level Logging:** Main execution, attack details, Ryu controller, and Mininet logs
    *   **Timing Analysis:** Phase-by-phase execution timing with comprehensive summaries
    *   **Dataset Statistics:** Automatic generation of feature counts and class distribution
    *   **Error Handling:** Graceful failure handling with detailed error reporting

5.  **Cleanup:**
    *   HTTP server termination (for slow read attacks)
    *   Graceful Ryu controller process termination
    *   Complete Mininet network cleanup and resource release

## Configuration Format

The `config.json` file controls all attack durations:

```json
{
  "scenario_durations": {
    "initialization": 5,
    "normal_traffic": 1200,
    "syn_flood": 600,
    "udp_flood": 600,
    "icmp_flood": 600,
    "ad_syn": 600,
    "ad_udp": 600,
    "ad_slow": 600,
    "cooldown": 10
  },
  "flow_collection_retry_delay": 5
}
```

**Total Default Duration**: ~80 minutes (5s + 20min + 6×10min + 10s)

## Expected Outputs

Upon successful execution, the `main_output/` directory will contain:

*   **Log Files:**
    *   `main.log`: Main script execution logs with timing summaries and dataset statistics
    *   `ryu.log`: Logs from the Ryu SDN controller application 
    *   `mininet.log`: Logs from the Mininet network simulation
    *   `attack.log`: Dedicated log for attack execution details and parameters
*   **PCAP Files (Raw Traffic Captures):**
    *   `normal.pcap`: Benign traffic capture
    *   `syn_flood.pcap`: Traditional SYN flood attack
    *   `udp_flood.pcap`: Traditional UDP flood attack  
    *   `icmp_flood.pcap`: Traditional ICMP flood attack
    *   `ad_syn.pcap`: Adversarial TCP state exhaustion attack
    *   `ad_udp.pcap`: Adversarial application layer attack
    *   `ad_slow.pcap`: Adversarial slow read attack (h2 perspective)
    *   `h6_slow_read.pcap`: Slow read attack from h6 (victim) perspective
*   **Labeled Datasets:**
    *   `packet_features.csv`: Unified packet-level features with comprehensive network metadata
    *   `flow_features.csv`: Flow-level statistics with calculated rates and temporal features
*   **Feature Documentation:**
    *   `packet_feature_names.txt`: Column headers and descriptions for packet dataset
    *   `flow_feature_names.txt`: Column headers and descriptions for flow dataset

    ### Packet-Level Features
    | Feature Name | Description | Relevance |
    |---|---|---|
    | `timestamp` | Timestamp of the packet capture. | Essential for temporal analysis and correlating events. |
    | `packet_length` | Length of the captured packet in bytes. | Indicates packet size, useful for identifying anomalies (e.g., unusually large or small packets). |
    | `eth_type` | Ethernet type of the packet (e.g., IP, ARP). | Identifies the network layer protocol, crucial for protocol-specific analysis. |
    | `ip_src` | Source IP address of the packet. | Identifies the sender, vital for tracing attack sources. |
    | `ip_dst` | Destination IP address of the packet. | Identifies the receiver, vital for tracing attack targets. |
    | `ip_proto` | IP protocol number (e.g., TCP, UDP, ICMP). | Specifies the transport layer protocol, fundamental for classifying traffic types. |
    | `ip_ttl` | IP Time-To-Live value. | Can indicate network topology or unusual routing paths, sometimes manipulated in attacks. |
    | `ip_id` | IP identification field. | Used for reassembling fragmented IP packets, can be used in some attack patterns. |
    | `ip_flags` | IP flags (e.g., Don't Fragment). | Indicates fragmentation status, relevant for certain attack types. |
    | `ip_len` | Total length of the IP packet. | Similar to `packet_length` but specific to the IP layer, useful for anomaly detection. |
    | `src_port` | Source port number (TCP/UDP). | Identifies the application sending the traffic, crucial for application-layer attack detection. |
    | `dst_port` | Destination port number (TCP/UDP). | Identifies the application receiving the traffic, crucial for application-layer attack detection. |
    | `tcp_flags` | TCP flags (e.g., SYN, ACK, FIN). | Essential for analyzing TCP connection states and identifying SYN floods or other TCP-based attacks. |
    | `Label_multi` | Multi-class label indicating the type of traffic (e.g., 'normal', 'syn_flood', 'udp_flood'). | Primary label for multi-class classification tasks. |
    | `Label_binary` | Binary label indicating whether the traffic is normal (0) or attack (1). | Primary label for binary classification tasks. |

    ### Flow-Level Features
    | Feature Name | Description | Relevance |
    |---|---|---|
    | `timestamp` | Timestamp when the flow statistics were collected. | Essential for temporal analysis of flow dynamics. |
    | `switch_id` | Datapath ID of the OpenFlow switch. | Identifies the switch where the flow was observed, crucial for network-wide analysis. |
    | `table_id` | ID of the flow table where the flow entry resides. | Indicates the processing stage of the flow within the switch. |
    | `cookie` | Opaque value used by the controller to identify the flow. | Can be used for internal tracking by the controller. |
    | `priority` | Priority of the flow entry. | Determines the order of matching, higher priority flows are matched first. |
    | `in_port` | Ingress port of the flow. | Identifies the port through which traffic entered the switch for this flow. |
    | `eth_src` | Ethernet source address of the flow. | Identifies the source MAC address of the traffic in the flow. |
    | `eth_dst` | Ethernet destination address of the flow. | Identifies the destination MAC address of the traffic in the flow. |
    | `out_port` | Egress port of the flow. | Identifies the port through which traffic exited the switch for this flow. |
    | `packet_count` | Number of packets matched by the flow entry. | Direct measure of traffic volume for the flow, key for anomaly detection. |
    | `byte_count` | Number of bytes matched by the flow entry. | Direct measure of traffic volume in bytes, key for anomaly detection. |
    | `duration_sec` | Time in seconds since the flow entry was added. | Indicates the longevity of the flow, useful for identifying short-lived attack flows. |
    | `duration_nsec` | Time in nanoseconds since the flow entry was added (fractional part). | Provides higher precision for flow duration. |
    | `avg_pkt_size` (calculated) | Average packet size for the flow (`byte_count / packet_count`). | Helps characterize the nature of traffic within a flow (e.g., small packets in SYN floods). |
    | `pkt_rate` (calculated) | Rate of packets per second for the flow (`packet_count / total_duration`). | Indicates the intensity of traffic, crucial for detecting high-rate attacks. |
    | `byte_rate` (calculated) | Rate of bytes per second for the flow (`byte_count / total_duration`). | Indicates the bandwidth consumption, crucial for detecting high-bandwidth attacks. |
    | `Label_multi` | Multi-class label indicating the type of traffic (e.g., 'normal', 'syn_flood', 'udp_flood'). | Primary label for multi-class classification tasks. |
    | `Label_binary` | Binary label indicating whether the traffic is normal (0) or attack (1). | Primary label for binary classification tasks. |

## Labeling Process

The dataset generation employs a time-based labeling mechanism to assign appropriate attack or normal labels to both packet-level and flow-level data. This ensures that each data point is correctly categorized based on the traffic scenario phase it belongs to.

### Packet-Level Labeling

For packet-level data, labeling occurs during the processing of individual PCAP files:
1.  **Individual PCAP Files:** Each PCAP file (`normal.pcap`, `syn_flood.pcap`, etc.) is generated during a specific, isolated traffic phase.
2.  **Timestamp Baseline:** Before feature extraction, `validate_and_fix_pcap_timestamps` is used to establish a reliable baseline timestamp for the packets within that specific PCAP file.
3.  **Phase-Specific Timeline:** A `label_timeline` is created for each PCAP. This timeline is simple, typically covering the entire duration of the PCAP with a single label corresponding to the traffic type captured (e.g., 'normal' for `normal.pcap`, 'syn_flood' for `syn_flood.pcap`).
4.  **Feature Extraction and Label Assignment:** The `enhanced_process_pcap_to_csv` function extracts features from the packets. For each packet, its timestamp is compared against the phase-specific `label_timeline` using the `_get_label_for_timestamp` helper function.
    *   `Label_multi`: Assigned the specific attack type (e.g., 'syn_flood', 'ad_slow') or 'normal'.
    *   `Label_binary`: Assigned `1` for any attack type and `0` for 'normal' traffic.
5.  **Consolidation:** After individual processing, all temporary CSVs are concatenated into the final `packet_features.csv`.

### Flow-Level Labeling

Flow-level data is labeled concurrently with the entire traffic generation scenario:
1.  **Continuous Collection:** The `collect_flow_stats` function runs in a background thread, continuously polling the Ryu controller's REST API (`/flows` endpoint) every second
2.  **Real-time Timestamping:** Each flow statistics collection uses `datetime.now().timestamp()` for precise temporal correlation
3.  **Dynamic Timeline Updates:** The `flow_label_timeline` is updated in real-time using `update_flow_timeline()` as each traffic phase begins
4.  **Synchronized Labeling:** Flow entries are labeled using `_get_label_for_timestamp()` matching their collection timestamp against the dynamic timeline
5.  **Enhanced Flow Metrics:** Calculated features include:
    *   `avg_pkt_size`: `byte_count / packet_count`
    *   `pkt_rate`: `packet_count / total_duration`  
    *   `byte_rate`: `byte_count / total_duration`
6.  **Direct Output:** All collected and labeled flow entries written to `flow_features.csv` with ordered columns

### Advanced Features

**PCAP Integrity and Analysis:**
- **Timestamp Validation:** Automatic detection and correction of timestamp corruption
- **TCP Connection Analysis:** Specialized analysis for slow read attacks detecting RST counts and retransmissions  
- **Inter-Packet Timing:** Statistical analysis of packet arrival patterns (mean, median, standard deviation)

**Execution Monitoring:**
- **Phase Timing Tracking:** Precise measurement of each attack phase duration vs configured duration
- **Real-time Progress Updates:** Dynamic timeline updates with execution status logging
- **Comprehensive Summaries:** Detailed timing breakdowns and dataset statistics upon completion

This comprehensive approach ensures accurate labeling, robust data collection, and detailed monitoring of the entire dataset generation process.