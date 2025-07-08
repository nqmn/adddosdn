# AI Agent Onboarding: SDN DDoS Dataset Generation

**Objective:** This guide provides a comprehensive, step-by-step workflow for an AI agent to deploy and operate this dataset generation module. The goal is to produce `offline_dataset.csv` and `online_dataset.csv` by simulating a DDoS attack in a Mininet-emulated SDN environment.

## 1. Environment Verification and Setup

Before execution, verify that the following dependencies are installed and available in the system's `PATH`. Execute the following commands to check for their presence:

```bash
# 1.1. Verify Python and Pip
python3 --version
pip3 --version

# 1.2. Verify Mininet
sudo mn --version

# 1.3. Verify Ryu SDN Framework
ryu-manager --version



# 1.5. Verify dumpcap (or tcpdump on Linux)
dumpcap --version
```

If any of these commands fail, the dependency is not met. The agent must install the missing software before proceeding.

### 1.6. Install Python Libraries

Run the following command to install the required Python libraries:

```bash
pip3 install requests mininet
```

### 1.7. Sudo Configuration for Mininet and Ryu

Mininet and Ryu often require `sudo` privileges to operate, especially when running in non-interactive environments (e.g., via SSH scripts). If you encounter `sudo: no tty present and no askpass program specified` errors, you need to configure `sudoers` to allow passwordless execution for the commands `mn` and `ryu-manager`.

**Steps to configure `sudoers`:**

1.  **Access the remote server:** Log in to your remote server via an interactive SSH session.
2.  **Edit `sudoers`:** Use `sudo visudo` to safely edit the `sudoers` file.
    ```bash
    sudo visudo
    ```
3.  **Add NOPASSWD entries:** Add the following lines to the `sudoers` file, replacing `your_username` with the actual username you are using on the remote server. These lines allow `your_username` to execute `mn` and `ryu-manager` without a password.

    ```
    # Allow passwordless sudo for Mininet
    your_username ALL=(ALL) NOPASSWD: /usr/bin/mn

    # Allow passwordless sudo for Ryu Manager
    your_username ALL=(ALL) NOPASSWD: /usr/local/bin/ryu-manager
    ```
    *   **Note:** The paths `/usr/bin/mn` and `/usr/local/bin/ryu-manager` are common, but you should verify the exact paths on your system using `which mn` and `which ryu-manager` on the remote server.
    *   **Security Warning:** Allowing `NOPASSWD` for `ALL` commands (`your_username ALL=(ALL) NOPASSWD: ALL`) is generally discouraged due to security risks. Only use it if you fully understand the implications and are in a controlled environment.

4.  **Save and Exit:** Save the changes and exit the `visudo` editor (usually by pressing `Ctrl+X`, then `Y` to confirm, then `Enter` for the filename).

## 2. Configuration

The `config.json` file is the single source of truth for this operation.



**Example `config.json`:**
```json
{
    "mininet_topology": "dataset_generation/topology.py",
    "ryu_app": "dataset_generation/controller/ryu_controller_app.py",
    "controller_port": 6633,
    "api_port": 8080,
    "traffic_types": {
        "normal": {
            "duration": 60,
            "scapy_commands": [
                {"host": "h3", "command": "sendp(Ether()/IP(dst='10.0.0.5')/TCP(dport=80, flags='S'), loop=1, inter=0.1)"},
                {"host": "h5", "command": "sendp(Ether()/IP(dst='10.0.0.3')/UDP(dport=53), loop=1, inter=0.1)"}
            ]
        },
        "attacks": [
            {
                "type": "syn_flood",
                "duration": 30,
                "attacker": "h1",
                "victim": "h6",
                "script_name": "gen_syn_flood.py"
            },
            {
                "type": "syn_flood",
                "duration": 30,
                "attacker": "h2",
                "victim": "h6",
                "script_name": "gen_syn_flood.py"
            },
            {
                "type": "udp_flood",
                "duration": 30,
                "attacker": "h2",
                "victim": "h4",
                "script_name": "gen_udp_flood.py"
            },
            {
                "type": "icmp_flood",
                "duration": 30,
                "attacker": "h2",
                "victim": "h4",
                "script_name": "gen_icmp_flood.py"
            }
        ]
    },
    "offline_collection": {
        "pcap_file": "traffic.pcap",
        "output_file": "offline_dataset.csv"
    },
    "online_collection": {
        "output_file": "online_dataset.csv",
        "poll_interval": 2
    },
    "label_timeline_file": "label_timeline.csv"
}
```

## 3. Execution Workflow

Execute the main script with `sudo` privileges. This is non-negotiable, as Mininet requires root access to create and manage virtual network interfaces.

```bash
sudo python3 dataset_generation/main.py
```

### Expected Execution Sequence:

1.  **Ryu Controller Launch**: The script will first launch the Ryu controller application in the background.
2.  **Mininet Initialization**: The custom 6-host topology will be loaded, and the Mininet network will start.
3.  **Data Collector Activation**: Two background threads will be initiated:
    - **Offline Collector**: `dumpcap` will start capturing all network traffic on the `any` interface, saving it to `traffic.pcap`.
    - **Online Collector**: A polling mechanism will begin querying the Ryu controller's REST API every 2 seconds for flow statistics.
4.  **Traffic Generation**: The script will proceed through two phases:
    - **Normal Traffic Period (60s)**: The simulation will run for 60 seconds with only benign background traffic.
    - **Attack Traffic Period (30s)**: Multiple attacks will be launched:
        - A SYN flood from `h1` to `h6` (Controller-based / Application-based).
        - A SYN flood from `h2` to `h6` (Controller-based / Application-based).
        - A UDP flood from `h2` to `h4` (Data Plane-based).
        - An ICMP flood from `h2` to `h4` (Data Plane-based).
5.  **Shutdown and Cleanup**: Once traffic generation is complete, the script will:
    - Stop the data collection threads.
    - Process `traffic.pcap` to generate `offline_dataset.csv`.
    - Terminate the Mininet network.
    - Stop the Ryu controller.

## 4. Adding New Attacks

To add a new attack type to the dataset generation process, follow these steps:

1.  **Create an Attack Script**: In the `attacks/` directory, create a new Python file (e.g., `gen_new_attack.py`). This script must contain a function named `run_attack` that accepts three arguments:
    -   `attacker_host`: The Mininet host object from which the attack will originate.
    -   `victim_ip`: The IP address of the target victim.
    -   `duration`: The duration (in seconds) for which the attack should run.

    Example structure for `gen_new_attack.py`:
    ```python
    from scapy.all import Ether, IP, TCP, sendp
    import time

    def run_attack(attacker_host, victim_ip, duration):
        print(f"Starting New Attack from {attacker_host.name} to {victim_ip} for {duration} seconds.")
        start_time = time.time()
        while time.time() - start_time < duration:
            # Your attack logic here, e.g., sendp(Ether()/IP(dst=victim_ip)/TCP(dport=80, flags='S'))
            pass
        print(f"New Attack from {attacker_host.name} to {victim_ip} finished.")
    ```

2.  **Update `config.json`**: Open `config.json` and add a new entry to the `traffic_types.attacks` array. This entry should specify the `type` of the attack, its `duration`, the `attacker` host, the `victim` host, and the `script_name` (the filename of your new attack script).

    Example addition to `config.json`:
    ```json
    {
        "type": "new_attack_type",
        "duration": 45,
        "attacker": "h1",
        "victim": "h3",
        "script_name": "gen_new_attack.py"
    }
    ```

By following these steps, `main.py` will automatically discover and execute your new attack script during the dataset generation process.

## 5. Deliverables Verification

Upon successful completion, verify that the following files have been created in the `dataset_generation` directory:

-   `packet_features.csv`: A CSV file containing processed offline traffic data. This dataset provides **packet-level features** and is ideal for detailed analysis of individual packet characteristics and for building models that require granular network information.
    -   `timestamp`: Packet capture timestamp.
    -   `packet_length`: Total length of the captured packet in bytes.
    -   `eth_type`: Ethernet type (e.g., 0x0800 for IPv4).
    -   `ip_src`: Source IP address.
    -   `ip_dst`: Destination IP address.
    -   `ip_proto`: IP protocol number (e.g., 6 for TCP, 17 for UDP, 1 for ICMP).
    -   `ip_ttl`: Time to Live.
    -   `ip_id`: IP identification field.
    -   `ip_flags`: IP flags (e.g., Don't Fragment, More Fragments).
    -   `ip_len`: Total length of the IP packet (including IP header and data).
    -   `src_port`: Source port (for TCP/UDP packets).
    -   `dst_port`: Destination port (for TCP/UDP packets).
    -   `tcp_flags`: TCP flags (e.g., SYN, ACK, FIN, RST, PSH, URG).
    -   `tcp_seq`: TCP Sequence Number.
    -   `tcp_ack`: TCP Acknowledgment Number.
    -   `tcp_window`: TCP Window Size.
    -   `icmp_type`: ICMP Type (for ICMP packets).
    -   `icmp_code`: ICMP Code (for ICMP packets).
    -   `Label`: The label indicating the traffic type (e.g., 'normal', 'syn_flood').

-   `ryu_flow_features.csv`: A CSV file containing flow statistics polled from the Ryu controller. This dataset provides **flow-level features** directly from the SDN controller, making it suitable for real-time anomaly detection and control plane analysis.
    -   `timestamp`: The timestamp when the flow statistics were polled.
    -   `datapath_id`: The unique identifier of the OpenFlow switch (DPID).
    -   `flow_id`: A unique identifier for the flow (Ryu's cookie).
    -   `ip_src`: Source IP address of the flow.
    -   `ip_dst`: Destination IP address of the flow.
    -   `port_src`: Source port of the flow (TCP or UDP).
    -   `port_dst`: Destination port of the flow (TCP or UDP).
    -   `ip_proto`: IP protocol number of the flow.
    -   `packet_count`: Number of packets that matched this flow entry.
    -   `byte_count`: Number of bytes that matched this flow entry.
    -   `duration_sec`: Duration of the flow in seconds.
    -   `Label`: The label indicating the traffic type (e.g., 'normal', 'syn_flood').

-   `traffic.pcap`: The raw packet capture from the simulation.
-   `label_timeline.csv`: A CSV file containing the timeline of normal and attack traffic labels.

-   `cicflow_dataset.csv`: A CSV file generated from `traffic.pcap` using CICFlowMeter. This dataset provides **advanced flow-level features** derived from packet data, offering a richer set of statistical metrics for in-depth traffic analysis and machine learning model training. It contains 83 flow features extracted by CICFlowMeter and an additional `Label` column. This dataset is generated independently and can be used for advanced flow-based analysis.

If these files are present, the operation was a success.