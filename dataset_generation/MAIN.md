# Dataset Generation Framework

This document outlines the usage, logic, and expected outputs of the `main.py` script, which orchestrates the generation of a DDoS attack dataset within an SDN environment.

## Prerequisites

To run this script, ensure you have the following installed on an Ubuntu system:

*   **Python 3**
*   **Mininet:** A network emulator for rapid prototyping of SDN.
*   **Ryu:** An SDN controller framework.
*   **TShark:** A network protocol analyzer (part of Wireshark).
*   **Slowhttptest:** A tool for testing web servers for slow HTTP attacks.

You can typically install these using your system's package manager (e.g., `sudo apt-get install mininet ryu-manager tshark slowhttptest`).

## How to Run

The script requires root privileges to run Mininet. It also uses `config.json` for scenario durations.

```bash
sudo python3 main.py
```

## Script Logic and Flow

The `main.py` script automates the following steps:

1.  **Environment Setup:**
    *   **Cleanup:** Clears any previous Mininet instances to ensure a clean slate.
    *   **Tool Verification:** Checks for the presence of all necessary command-line tools (`ryu-manager`, `mn`, `tshark`, `slowhttptest`).
    *   **Ryu Controller Initialization:** Starts the Ryu SDN controller in the background, logging its output to `main_output/ryu.log`.
    *   **Controller Health Check:** Verifies that the Ryu controller is running and listening on its designated port (6653). It also tests a `/hello` endpoint to confirm API responsiveness.
    *   **Mininet Network Creation:** Builds a custom Mininet topology consisting of one OpenFlow switch (`s1`) and six hosts (`h1` to `h6`). The switch is connected to the remote Ryu controller. Mininet logs are saved to `main_output/mininet.log`.
    *   **Connectivity Test:** Runs `pingAll` within Mininet to confirm basic network connectivity between all hosts.

2.  **Traffic Generation Scenario:**
    The script orchestrates a multi-phase traffic generation process, capturing network traffic for each phase into separate PCAP files.

    *   **Phase 1: Initialization:** A brief pause before traffic generation begins. Duration is configurable via `config.json`.
    *   **Phase 2: Normal Traffic:**
        *   Captures benign traffic to `main_output/normal.pcap`.
        *   Generates various types of legitimate traffic (ICMP, TCP, UDP, Telnet, SSH, FTP, HTTP, HTTPS, DNS) between `h3` and `h5`. Duration is configurable via `config.json`.
    *   **Phase 3.1: Traditional DDoS Attacks:** Durations for each attack type are configurable via `config.json`.
        | Attack Type | Source | Destination | Affected Plane | Relevance |
        |---|---|---|---|---|
        | SYN Flood | `h1` | `h6` | Control/Data | Exploits TCP handshake to exhaust server resources. |
        | UDP Flood | `h2` | `h4` | Data | Overwhelms target with UDP traffic, often used in reflection/amplification attacks. |
        | ICMP Flood | `h2` | `h4` | Data | Consumes bandwidth and resources with ICMP echo requests. |
    *   **Phase 3.2: Adversarial DDoS Attacks:** Durations for each attack type are configurable via `config.json`.
        | Attack Type | Source | Destination | Affected Plane | Relevance |
        |---|---|---|---|---|
        | Adversarial TCP State Exhaustion | `h2` | `h6` | Control/Data | Advanced SYN flood variant designed to evade detection. |
        | Adversarial Application Layer | `h2` | `h6` | Application | Targets application layer vulnerabilities, harder to detect than volumetric attacks. |
        | Adversarial Slow Read | `h2` | `h6` | Application | Keeps connections open by reading data slowly, exhausting server resources. |
    *   **Phase 4: Cooldown:** A final pause after all traffic generation. Duration is configurable via `config.json`. For flow data collection, this phase is extended to cover the entire scenario duration, ensuring all lingering flow entries are labeled as normal.

3.  **Data Collection and Dataset Creation:**
    *   **Concurrent Flow Statistics Collection:** Simultaneously with traffic generation, the script continuously queries the Ryu controller's REST API (`/flows` endpoint) to collect real-time flow statistics. This data is saved to `main_output/flow_features.csv`.
    *   **PCAP Processing:** For each generated PCAP file:
        *   It performs an integrity check to ensure the PCAP is valid using `verify_pcap_integrity`.
        *   It validates and fixes any timestamp inconsistencies within the PCAP using `validate_and_fix_pcap_timestamps`.
        *   It extracts network features and applies appropriate labels (e.g., 'normal', 'syn_flood') based on the traffic type using `enhanced_process_pcap_to_csv`. This process generates temporary CSV files.
    *   **Packet-Level Dataset Consolidation:** All temporary labeled packet-level CSV files are concatenated into a single, comprehensive dataset.
    *   **Final Packet-Level CSV:** The combined packet-level dataset is saved as `main_output/packet_features.csv`.
    *   **Label Verification:** The `verify_labels_in_csv` function is used to ensure the correctness and consistency of labels in the generated CSV files.

4.  **Cleanup:**
    *   Gracefully terminates the Ryu controller process.
    *   Performs a final Mininet cleanup to release all network resources.

## Expected Outputs

Upon successful execution, the `main_output/` directory will contain:

*   **Log Files:**
    *   `main.log`: Main script execution logs.
    *   `ryu.log`: Logs from the Ryu SDN controller.
    *   `mininet.log`: Logs from the Mininet network simulation.
    *   `attack.log`: A dedicated log for details about the executed attacks.
*   **PCAP Files (Raw Traffic Captures):**
    *   `normal.pcap`
    *   `syn_flood.pcap`
    *   `udp_flood.pcap`
    *   `icmp_flood.pcap`
    *   `ad_syn.pcap`
    *   `ad_udp.pcap`
    *   `ad_slow.pcap`
*   **Labeled Dataset:**
    *   `packet_features.csv`: The final CSV file containing extracted packet-level network features and corresponding binary and multi-class labels for all traffic types.
    *   `flow_features.csv`: The CSV file containing flow-level statistics collected from the Ryu controller.
*   **Feature Names:**
    *   `packet_feature_names.txt`: A text file listing the column headers for `packet_features.csv`.
    *   `flow_feature_names.txt`: A text file listing the column headers for `flow_features.csv`.

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
1.  **Continuous Collection:** The `collect_flow_stats` function runs in a separate thread, continuously polling the Ryu controller's `/flows` API endpoint.
2.  **Real-time Timestamping:** Each time flow statistics are collected, the current system timestamp (`datetime.now().timestamp()`) is recorded for the flow entries.
3.  **Overall Scenario Timeline:** A single, comprehensive `flow_label_timeline` is defined in the `main` function. This timeline spans the entire duration of the traffic generation scenario, with precise start and end times for each phase (Initialization, Normal, Traditional Attacks, Adversarial Attacks, Cooldown).
4.  **Robust Time Matching:** To account for potential delays in flow reporting by the controller and the persistence of flow entries in the flow table (which can linger for several seconds after a phase's nominal end), a small epsilon (e.g., 0.1 seconds) is added to the `end_time` of each phase in the `flow_label_timeline`. This ensures that flow records collected slightly after a phase's nominal end are still correctly associated with that phase's label.
5.  **Label Assignment:** For each collected flow entry, its `timestamp` is compared against this overall `flow_label_timeline` using the `_get_label_for_timestamp` helper function.
    *   `Label_multi`: Assigned the specific attack type or 'normal' based on the current timestamp's position within the `flow_label_timeline`.
    *   `Label_binary`: Assigned `1` for any attack type and `0` for 'normal' traffic.
6.  **Direct Output:** All collected and labeled flow entries are directly written to `flow_features.csv`.

This dual-layer labeling approach ensures that both granular packet-level events and aggregated flow-level behaviors are accurately categorized according to the experimental design, providing a rich dataset for analysis.