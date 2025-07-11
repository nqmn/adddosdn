# Dataset Generation Test Framework

This document outlines the usage, logic, and expected outputs of the `test.py` script, which orchestrates the generation of a DDoS attack dataset within an SDN environment.

## Prerequisites

To run this script, ensure you have the following installed on an Ubuntu system:

*   **Python 3**
*   **Mininet:** A network emulator for rapid prototyping of SDN.
*   **Ryu:** An SDN controller framework.
*   **TShark:** A network protocol analyzer (part of Wireshark).
*   **Slowhttptest:** A tool for testing web servers for slow HTTP attacks.

You can typically install these using your system's package manager (e.g., `sudo apt-get install mininet ryu-manager tshark slowhttptest`).

## How to Run

The script requires root privileges to run Mininet.

```bash
sudo python3 test.py
```

## Script Logic and Flow

The `test.py` script automates the following steps:

1.  **Environment Setup:**
    *   **Cleanup:** Clears any previous Mininet instances to ensure a clean slate.
    *   **Tool Verification:** Checks for the presence of all necessary command-line tools (`ryu-manager`, `mn`, `tshark`, `slowhttptest`).
    *   **Ryu Controller Initialization:** Starts the Ryu SDN controller in the background, logging its output to `output/ryu.log`.
    *   **Controller Health Check:** Verifies that the Ryu controller is running and listening on its designated port (6653). It also tests a `/hello` endpoint to confirm API responsiveness.
    *   **Mininet Network Creation:** Builds a custom Mininet topology consisting of one OpenFlow switch (`s1`) and six hosts (`h1` to `h6`). The switch is connected to the remote Ryu controller. Mininet logs are saved to `output/mininet.log`.
    *   **Connectivity Test:** Runs `pingAll` within Mininet to confirm basic network connectivity between all hosts.

2.  **Traffic Generation Scenario:**
    The script orchestrates a multi-phase traffic generation process, capturing network traffic for each phase into separate PCAP files.

    *   **Phase 1: Initialization (5 seconds):** A brief pause before traffic generation begins.
    *   **Phase 2: Normal Traffic (5 seconds):**
        *   Captures benign traffic to `output/normal.pcap`.
        *   Generates various types of legitimate traffic (ICMP, TCP, UDP, Telnet, SSH, FTP, HTTP) between `h3` and `h5`.
    *   **Phase 3.1: Traditional DDoS Attacks (15 seconds total):**
        | Attack Type | Source | Destination | Affected Plane | Relevance |
        |---|---|---|---|---|
        | SYN Flood | `h1` | `h6` | Control/Data | Exploits TCP handshake to exhaust server resources. |
        | UDP Flood | `h2` | `h4` | Data | Overwhelms target with UDP traffic, often used in reflection/amplification attacks. |
        | ICMP Flood | `h2` | `h4` | Data | Consumes bandwidth and resources with ICMP echo requests. |
    *   **Phase 3.2: Adversarial DDoS Attacks (20 seconds total):**
        | Attack Type | Source | Destination | Affected Plane | Relevance |
        |---|---|---|---|---|
        | Adversarial TCP State Exhaustion | `h2` | `h6` | Control/Data | Advanced SYN flood variant designed to evade detection. |
        | Adversarial Application Layer | `h2` | `h6` | Application | Targets application layer vulnerabilities, harder to detect than volumetric attacks. |
        | Adversarial Slow Read | `h2` | `h6` | Application | Keeps connections open by reading data slowly, exhausting server resources. |
    *   **Phase 4: Cooldown (5 seconds):** A final pause after all traffic generation.

3.  **Data Collection and Dataset Creation:**
    *   **Concurrent Flow Statistics Collection:** Simultaneously with traffic generation, the script continuously queries the Ryu controller's REST API (`/flows` endpoint) to collect real-time flow statistics. This data is saved to `output/flow_features.csv`.
    *   **PCAP Processing:** For each generated PCAP file:
        *   It performs an integrity check to ensure the PCAP is valid.
        *   It validates and fixes any timestamp inconsistencies within the PCAP.
        *   It extracts network features and applies appropriate labels (e.g., 'normal', 'syn_flood') based on the traffic type. This process generates temporary CSV files.
    *   **Packet-Level Dataset Consolidation:** All temporary labeled packet-level CSV files are concatenated into a single, comprehensive dataset.
    *   **Final Packet-Level CSV:** The combined packet-level dataset is saved as `output/packet_features.csv`.

4.  **Cleanup:**
    *   Gracefully terminates the Ryu controller process.
    *   Performs a final Mininet cleanup to release all network resources.

## Expected Outputs

Upon successful execution, the `output/` directory will contain:

*   **Log Files:**
    *   `test.log`: Main script execution logs.
    *   `ryu.log`: Logs from the Ryu SDN controller.
    *   `mininet.log`: Logs from the Mininet network simulation.
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

*   `flow_features.csv`: The CSV file containing flow-level statistics collected from the Ryu controller.

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

## Verification

The script includes internal verification steps, such as `verify_tools()`, `check_controller_health()`, `run_mininet_pingall_test()`, and `verify_pcap_integrity()`. Additionally, the `verify_labels_in_csv` function (though not called in `main` for the final combined CSV) demonstrates the logic for ensuring that the generated `packet_features.csv` contains the expected labels and that binary labels are consistent with multi-class labels.