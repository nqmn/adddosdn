# Mininet Host Scenario

This document details the Mininet host scenario for the DDoS dataset generation, outlining the roles of each host and the types of traffic generated.

## Topology Overview

The Mininet topology consists of a single OpenFlow switch (`s1`) connected to six hosts (`h1` through `h6`). Each host is assigned a unique IP address from `10.0.0.1` to `10.0.0.6`.

## Host Roles and Traffic Types

### Attackers

*   **h1 (Attacker 1):** Launches a **TCP-based DDoS attack (SYN Flood)** against the web server (`h6`). This is primarily a **Controller-based** attack, as it can overwhelm the controller's flow table and processing capabilities, and also has an **Application-based** impact by exhausting server resources.
*   **h2 (Attacker 2):** Launches multiple attacks, including traditional and adversarial DDoS attacks:
    *   A **TCP-based DDoS attack (SYN Flood)** against the web server (`h6`). This is primarily a **Controller-based** attack, as it can overwhelm the controller's flow table and processing capabilities, and also has an **Application-based** impact by exhausting server resources.
    *   A **UDP Flood attack** against the victim host (`h4`). This is a **Data Plane-based** attack, aiming to saturate the victim's network interface and consume bandwidth.
    *   An **ICMP Flood attack** against the victim host (`h4`). This is also a **Data Plane-based** attack, similar to UDP flood, focusing on overwhelming the victim's network resources.
    *   **Adversarial DDoS Attacks**: These attacks leverage advanced techniques to evade detection and mitigation, including:
        *   **Adversarial SYN Flood (e.g., TCP State Exhaustion)**: Mimics legitimate TCP handshakes to exhaust server resources.
        *   **Adversarial UDP Flood (e.g., Application Layer Attack)**: Generates traffic that appears legitimate at the network layer but targets resource-intensive application endpoints.
        *   **Adversarial ICMP Flood (e.g., Slow Read Attack)**: Establishes connections and reads data very slowly to tie up server resources.
        *   **Multi-vector Adversarial Attacks**: Combines multiple adversarial techniques simultaneously to increase effectiveness and evade detection.

### Victims

*   **h6 (Web Server Victim):** The target for TCP-based DDoS attacks (SYN Flood) from both `h1` and `h2`.
*   **h4 (General Victim):** The target for UDP Flood and ICMP Flood attacks from `h2`.

### Normal Traffic Generators

The remaining hosts are responsible for generating benign, normal network traffic to simulate a realistic network environment. This traffic helps in creating a balanced dataset with both normal and attack patterns.

*   **h3:** Generates normal traffic, including TCP packets to `h5`.
*   **h5:** Generates normal traffic, including UDP packets to `h3`.

## Traffic Generation Phases

The dataset generation process proceeds through distinct traffic generation phases:

1.  **Normal Traffic Period:** All hosts not designated as attackers or victims for a specific attack type will generate normal background traffic for a configured duration.
2.  **Attack Traffic Period:** During this phase, the configured attackers (`h1`, `h2`) will launch their respective DDoS attacks against their designated victims (`h4`, `h6`). These attacks run concurrently with any ongoing normal traffic.

This structured approach ensures that the generated dataset accurately reflects a mix of normal network operations and various types of DDoS attacks.

## Dataset Features

This project generates two primary datasets:

### `packet_features.csv`

A CSV file containing processed offline traffic data, derived from the raw `traffic.pcap` capture. This dataset provides **packet-level features** and is ideal for detailed analysis of individual packet characteristics and for building models that require granular network information.

*   `timestamp`: Packet capture timestamp.
*   `packet_length`: Total length of the captured packet in bytes.
*   `eth_type`: Ethernet type (e.g., 0x0800 for IPv4).
*   `ip_src`: Source IP address.
*   `ip_dst`: Destination IP address.
*   `ip_proto`: IP protocol number (e.g., 6 for TCP, 17 for UDP, 1 for ICMP).
*   `ip_ttl`: Time to Live.
*   `ip_id`: IP identification field.
*   `ip_flags`: IP flags (e.g., Don't Fragment, More Fragments).
*   `ip_len`: Total length of the IP packet (including IP header and data).
*   `src_port`: Source port (for TCP/UDP packets).
*   `dst_port`: Destination port (for TCP/UDP packets).
*   `tcp_flags`: TCP flags (e.g., SYN, ACK, FIN, RST, PSH, URG).
*   `tcp_seq`: TCP Sequence Number.
*   `tcp_ack`: TCP Acknowledgment Number.
*   `tcp_window`: TCP Window Size.
*   `icmp_type`: ICMP Type (for ICMP packets).
*   `icmp_code`: ICMP Code (for ICMP packets).
*   `Label_multi`: This column provides a multi-class label indicating the specific type of traffic or attack (e.g., 'normal', 'syn_flood', 'udp_flood', 'icmp_flood', 'ad_syn_flood', 'ad_udp_flood', 'ad_icmp_flood', 'ad_multi_vector'). This is useful for fine-grained classification tasks.
*   `Label_binary`: This column provides a binary label for traffic classification, where `0` indicates 'normal' traffic and `1` indicates any type of 'attack' traffic. This is suitable for binary classification (anomaly detection) models.

### `ryu_flow_features.csv`

A CSV file containing flow statistics polled from the Ryu controller. This dataset provides **flow-level features** directly from the SDN controller, making it suitable for real-time anomaly detection and control plane analysis.

*   `timestamp`: The timestamp when the flow statistics were polled.
*   `datapath_id`: The unique identifier of the OpenFlow switch (DPID).
*   `flow_id`: A unique identifier for the flow (Ryu's cookie).
*   `ip_src`: Source IP address of the flow.
*   `ip_dst`: Destination IP address of the flow.
*   `port_src`: Source port of the flow (TCP or UDP).
*   `port_dst`: Destination port of the flow (TCP or UDP).
*   `ip_proto`: IP protocol number of the flow.
*   `packet_count`: Number of packets that matched this flow entry.
*   `byte_count`: Number of bytes that matched this flow entry.
*   `duration_sec`: Duration of the flow in seconds.
*   `Label_multi`: This column provides a multi-class label indicating the specific type of traffic or attack (e.g., 'normal', 'syn_flood', 'udp_flood', 'icmp_flood', 'ad_syn_flood', 'ad_udp_flood', 'ad_icmp_flood', 'ad_multi_vector'). This is useful for fine-grained classification tasks.
*   `Label_binary`: This column provides a binary label for traffic classification, where `0` indicates 'normal' traffic and `1` indicates any type of 'attack' traffic. This is suitable for binary classification (anomaly detection) models.

### `cicflow_dataset.csv`

A CSV file generated from `traffic.pcap` using CICFlowMeter. This dataset provides **advanced flow-level features** derived from packet data, offering a richer set of statistical metrics for in-depth traffic analysis and machine learning model training. It contains 83 flow features extracted by CICFlowMeter and an additional `Label_multi` and `Label_binary` column.

**Generation:** This dataset is generated independently using the `generate_cicflow_dataset.py` script, which takes a PCAP file and a label as input.