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
        *   **SYN Flood (5 seconds):** `h1` launches a SYN flood attack on `h6`. Captured to `output/syn_flood.pcap`.
        *   **UDP Flood (5 seconds):** `h2` launches a UDP flood attack on `h4`. Captured to `output/udp_flood.pcap`.
        *   **ICMP Flood (5 seconds):** `h2` launches an ICMP flood attack on `h4`. Captured to `output/icmp_flood.pcap`.
    *   **Phase 3.2: Adversarial DDoS Attacks (20 seconds total):**
        *   **Adversarial TCP State Exhaustion (5 seconds):** `h2` launches an adversarial SYN attack on `h6`. Captured to `output/ad_syn.pcap`.
        *   **Adversarial Application Layer (5 seconds):** `h2` launches an adversarial UDP attack on `h6`. Captured to `output/ad_udp.pcap`.
        *   **Adversarial Slow Read (5 seconds):** `h2` launches a slow read attack on `h6`. Captured to `output/ad_slow.pcap`.
    *   **Phase 4: Cooldown (5 seconds):** A final pause after all traffic generation.

3.  **PCAP Processing and Dataset Creation:**
    *   **Individual PCAP Processing:** For each generated PCAP file:
        *   It performs an integrity check to ensure the PCAP is valid.
        *   It validates and fixes any timestamp inconsistencies within the PCAP.
        *   It extracts network features and applies appropriate labels (e.g., 'normal', 'syn_flood') based on the traffic type. This process generates temporary CSV files.
    *   **Dataset Consolidation:** All temporary labeled CSV files are concatenated into a single, comprehensive dataset.
    *   **Final Labeled CSV:** The combined dataset is saved as `output/labeled_packet_features.csv`.

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
    *   `labeled_packet_features.csv`: The final CSV file containing extracted network features and corresponding binary and multi-class labels for all traffic types.

## Verification

The script includes internal verification steps, such as `verify_tools()`, `check_controller_health()`, `run_mininet_pingall_test()`, and `verify_pcap_integrity()`. Additionally, the `verify_labels_in_csv` function (though not called in `main` for the final combined CSV) demonstrates the logic for ensuring that the generated CSV contains the expected labels and that binary labels are consistent with multi-class labels.