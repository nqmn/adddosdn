# TEST.md: Comprehensive Test and Dataset Generation Framework

This document describes `test.py`, a core script within the AdDDoSDN project responsible for orchestrating the entire dataset generation process. It covers environment verification, network setup, traffic generation (benign and attack), packet capture, and data processing.

## 1. Purpose of `test.py`

`test.py` serves as a comprehensive framework for:
- Setting up a Mininet-based Software-Defined Networking (SDN) environment.
- Deploying a Ryu SDN controller.
- Generating various types of network traffic, including normal benign traffic, traditional DDoS attacks (SYN Flood, UDP Flood, ICMP Flood), and advanced adversarial DDoS attacks (TCP State Exhaustion, Application Layer, Multi-Vector).
- Capturing network traffic in PCAP format.
- Processing captured PCAP files into labeled CSV datasets for machine learning analysis.
- Ensuring the integrity and proper timestamping of captured data.

The script aims to automate the creation of a diverse dataset for research and development in DDoS detection within SDN environments.

## 2. Dependencies

`test.py` relies on a combination of Python libraries, local modules, and external command-line tools.

### 2.1. Python Libraries

-   **Standard Libraries**:
    -   `io`, `sys`, `re`, `os`, `signal`, `time`, `logging`, `argparse`, `subprocess`, `pathlib`, `shutil`
-   **Third-Party Libraries**:
    -   `scapy`: For packet manipulation and reading PCAP files (`rdpcap`).
    -   `mininet`: For creating and managing the virtual network topology (`Mininet`, `Topo`, `OVSKernelSwitch`, `RemoteController`, `CLI`, `setLogLevel`, `info`).
    -   `requests`: Used for checking the Ryu controller's `/hello` endpoint.

### 2.2. Local Modules

-   `src/utils/process_pcap_to_csv.py`: This module is responsible for converting raw PCAP (Packet Capture) files into a structured CSV (Comma Separated Values) format. It extracts relevant packet features, such as timestamps, source/destination IPs and ports, protocols, and packet lengths, making the data suitable for analysis.
-   `src/utils/enhanced_pcap_processing.py`: This module provides advanced functionalities for handling PCAP files, ensuring data quality and reliability. It includes:
    -   `validate_and_fix_pcap_timestamps`: A function to identify and correct issues with packet timestamps within PCAP files, such as out-of-order or corrupted timestamps, which is crucial for accurate timeline-based labeling.
    -   `enhanced_process_pcap_to_csv`: An integrated function that combines PCAP to CSV conversion with timestamp validation, ensuring that the generated CSV dataset has accurate time-series information.
    -   `improve_capture_reliability`: Manages the `tshark` packet capture process, enhancing its robustness and ensuring consistent data collection during traffic generation.
    -   `verify_pcap_integrity`: A utility to check the overall integrity of captured PCAP files, detecting issues like zero-byte files or significant timestamp corruption.
-   `src/attacks/gen_syn_flood.py`: This module contains the logic for generating SYN Flood attacks. It simulates a large number of SYN requests to a target host, aiming to exhaust its connection resources.
-   `src/attacks/gen_udp_flood.py`: This module implements the generation of UDP Flood attacks. It sends a high volume of UDP packets to a target, often to random ports, to consume bandwidth and overwhelm the target's resources.
-   `src/attacks/gen_icmp_flood.py`: This module is used to generate ICMP Flood attacks. It sends a large number of ICMP (ping) requests to a target, aiming to saturate network bandwidth and consume target resources.
-   `src/attacks/gen_advanced_adversarial_ddos_attacks.py`: This module is designed to generate more sophisticated adversarial DDoS attacks. It includes various attack variants (e.g., `ad_syn`, `ad_udp`, `multivector`) that employ advanced techniques to evade detection or mimic legitimate traffic patterns.
-   `src/controller/ryu_controller_app.py`: This file contains the Ryu application code that functions as the SDN controller for the Mininet network. It manages network flows, handles switch-controller communication, and enforces network policies.

### 2.3. External Command-Line Tools

-   `ryu-manager`: The Ryu SDN controller's executable.
-   `mn`: The Mininet command-line tool.
-   `tshark`: The command-line network protocol analyzer (part of Wireshark) used for packet capture and CSV export.
-   `ss` or `netstat`: Used for checking controller port health.

## 3. Architecture and Workflow

The `test.py` script follows a structured, multi-phase workflow to generate the dataset:

1.  **Initialization and Setup**:
    -   **Cleanup**: Clears any previous Mininet instances (`mn -c`) to ensure a clean slate.
    -   **Tool Verification**: Checks for the presence of essential command-line tools (`ryu-manager`, `mn`, `tshark`).
    -   **Ryu Controller Startup**: Starts the `ryu_controller_app.py` as a background process and verifies its health by checking if it's listening on port 6653 and responding to a `/hello` API endpoint.
    -   **Mininet Topology Setup**:
        -   Defines a custom `ScenarioTopo` with one Open vSwitch (OVSKernelSwitch) and six hosts (`h1` through `h6`).
        -   Connects to the remote Ryu controller.
        -   Builds and starts the Mininet network.
    -   **Connectivity Test**: Runs `net.pingAll()` to confirm basic network connectivity within the Mininet environment.

2.  **Traffic Generation Scenario (`run_traffic_scenario`)**:
    -   **Packet Capture Initiation**: Starts `tshark` on `h1` to capture all network traffic to a PCAP file (`capture.pcap`) and simultaneously exports selected fields to a CSV file (`packet_features.csv`).
    -   **Phase 1: Initialization (5 seconds)**: A brief period for the network to settle.
    -   **Phase 2: Normal Traffic (5 seconds)**: Generates diverse benign traffic using Scapy, including ICMP pings, TCP, UDP, Telnet, SSH, FTP, and HTTP, primarily between `h3` and `h5`.
    -   **Phase 3.1: Traditional DDoS Attacks (15 seconds)**:
        -   SYN Flood (`h1` -> `h6`)
        -   UDP Flood (`h2` -> `h4`)
        -   ICMP Flood (`h2` -> `h4`)
    -   **Phase 3.2: Adversarial DDoS Attacks (15 seconds)**:
        -   Adversarial TCP State Exhaustion (`h2` -> `h6`)
        -   Adversarial Application Layer (`h2` -> `h6`)
        -   Adversarial Multi-Vector (`h2` -> `h6`)
    -   **Phase 4: Cooldown (5 seconds)**: A period after attacks for traffic to subside.
    -   **Packet Capture Termination**: Stops the `tshark` process.

3.  **Data Processing**:
    -   **PCAP Integrity Check**: Verifies the captured PCAP file for issues like zero-byte size or high timestamp corruption.
    -   **Timestamp Validation and Fixing**: Uses `validate_and_fix_pcap_timestamps` to correct any corrupted or out-of-order timestamps in the PCAP.
    -   **PCAP to Labeled CSV Conversion**:
        -   Defines a `label_timeline` based on the start and end times of each traffic phase (Initialization, Normal, Traditional Attacks, Adversarial Attacks, Cooldown).
        -   Uses `enhanced_process_pcap_to_csv` to convert the captured PCAP data into a labeled CSV file (`labeled_packet_features.csv`), associating each packet with its corresponding traffic phase label.

4.  **Cleanup**:
    -   Terminates the Ryu controller process.
    -   Performs a final Mininet cleanup (`mn -c`).

## 4. Configuration

Key configurable paths and network parameters are defined at the top of the script:

-   `BASE_DIR`: Root directory of the script.
-   `SRC_DIR`: Source code directory.
-   `ATTACKS_DIR`: Directory containing attack scripts.
-   `UTILS_DIR`: Directory containing utility scripts.
-   `OUTPUT_DIR`: Directory for all generated output files (PCAP, CSV, logs).
-   `PCAP_FILE`: Path for the raw PCAP capture.
-   `OUTPUT_CSV_FILE`: Path for the intermediate CSV output (not directly used for final labeled output).
-   `OUTPUT_LABELED_CSV_FILE`: Path for the final labeled CSV dataset.
-   `RYU_CONTROLLER_APP`: Path to the Ryu controller application.
-   `HOST_IPS`: A dictionary mapping host names (`h1` to `h6`) to their respective IP addresses (`10.0.0.1` to `10.0.0.6`).

## 5. Configuration

Key configurable paths and network parameters are defined at the top of the script:

-   `BASE_DIR`: Root directory of the script.
-   `SRC_DIR`: Source code directory.
-   `ATTACKS_DIR`: Directory containing attack scripts.
-   `UTILS_DIR`: Directory containing utility scripts.
-   `OUTPUT_DIR`: Directory for all generated output files (PCAP, CSV, logs).
-   `PCAP_FILE`: Path for the raw PCAP capture.
-   `OUTPUT_CSV_FILE`: Path for the intermediate CSV output (not directly used for final labeled output).
-   `OUTPUT_LABELED_CSV_FILE`: Path for the final labeled CSV dataset.
-   `RYU_CONTROLLER_APP`: Path to the Ryu controller application.
-   `HOST_IPS`: A dictionary mapping host names (`h1` to `h6`) to their respective IP addresses (`10.0.0.1` to `10.0.0.6`).

## 6. Deliverables/Outputs

Upon successful execution, `test.py` generates the following key outputs in the `output/` directory:

-   `capture.pcap`: The raw packet capture file in PCAP format, containing all network traffic generated during the scenario.
-   `labeled_packet_features.csv`: The primary output dataset. This CSV file contains extracted packet features and a corresponding label for each packet, indicating the traffic phase (e.g., `normal`, `syn_flood`, `ad_application_layer`). This file is ready for machine learning model training and analysis.
-   `ryu.log`: Log file for the Ryu SDN controller, capturing its operational messages.
-   `mininet.log`: Log file for Mininet, detailing the network setup and events.
-   `test.log`: The main log file for the `test.py` script itself, recording the execution flow, warnings, and errors.
-   `capture.csv.log`: Error log specifically for the `tshark` capture process, useful for debugging capture issues.

These files collectively provide the generated dataset and comprehensive logs for verifying the experiment and analyzing the results.

## 7. Usage

To run `test.py`:

```bash
sudo python3 test.py
```

**Note**: The script requires root privileges to run Mininet and `tshark` commands.
