# Project Logical Flow Analysis

This document outlines a comprehensive review of the project's logical flow, focusing on the `dataset_generation/main.py` script, from environment setup to data generation, ensuring consistency and coherence.

## 1. `dataset_generation/main.py` Review

*   **Purpose:** `dataset_generation/main.py` serves as the central orchestrator for the entire dataset generation process. It reads scenario configurations from `config.json`, sets up the Mininet environment, deploys the Ryu controller, generates various types of network traffic (benign and attack), captures packets, collects flow statistics, and processes the data into final datasets.
*   **Privileges:** Correctly checks for `sudo` privileges, which is essential for Mininet operations.
*   **Configuration:** Externalizes traffic phase durations and other parameters into `config.json`, allowing for easy modification of scenarios without changing the code.
*   **Ryu & Mininet Management:** Starts and stops both components in a logical order, ensuring the network environment is properly set up and torn down.
*   **Traffic Generation (`run_traffic_scenario`):**
    *   Initiates separate packet captures (`tshark`) for each traffic phase, saving them to individual `.pcap` files.
    *   Generates benign traffic.
    *   Launches various traditional DDoS attacks (SYN Flood, UDP Flood, ICMP Flood).
    *   Launches advanced adversarial DDoS attacks, including TCP State Exhaustion, Application Layer, and a new **Slow Read** attack.
    *   Includes cooldown periods between phases.
*   **Data Processing:**
    *   **Flow-level Data:** A background thread (`collect_flow_stats`) periodically queries the Ryu controller's REST API to gather flow statistics throughout the scenario. This data is labeled in real-time and saved to `flow_features.csv`.
    *   **Packet-level Data:** After the scenario completes, the script processes each individual `.pcap` file. It verifies integrity, fixes timestamps, and converts the captures into labeled CSV data. All individual CSVs are then concatenated into a final `packet_features.csv`.

## 2. Attack Scripts (`src/attacks/` directory) Review

*   The attack scripts (`gen_syn_flood.py`, `gen_udp_flood.py`, `gen_icmp_flood.py`, `gen_advanced_adversarial_ddos_attacks.py`) consistently expose a `run_attack` function. This standardized interface is correctly utilized by `main.py` for dynamic execution.
*   The content of these scripts aligns with the described attack types, including traditional floods and sophisticated adversarial techniques like the Slow Read attack, which uses the `slowhttptest` tool.

## 3. Utility Scripts (`src/utils/` directory) Review

*   `process_pcap_to_csv.py`: Responsible for converting raw PCAP files into a structured CSV format with packet-level features.
*   `enhanced_pcap_processing.py`: Provides advanced functionalities for handling PCAP files, including timestamp validation, integrity checks, and reliable capture methods.

## 4. Deliverables/Outputs

Upon successful execution, `dataset_generation/main.py` generates the following key outputs in the `dataset_generation/main_output/` directory:

-   **Packet-level Data:**
    -   `normal.pcap`, `syn_flood.pcap`, etc.: Raw packet capture files for each phase.
    -   `packet_features.csv`: The primary packet-level dataset with extracted features and labels.
-   **Flow-level Data:**
    -   `flow_features.csv`: A new dataset containing flow-based statistics collected from the Ryu controller.
-   **Logs:**
    -   `ryu.log`: Log file for the Ryu SDN controller.
    -   `mininet.log`: Log file for Mininet.
    -   `main.log`: The main log file for the `main.py` script itself.
    -   `attack.log`: A dedicated log for details about the executed attacks.

## Conclusion

The overall flow of the project, orchestrated by `dataset_generation/main.py`, is **logical, robust, and highly configurable**. The script seamlessly integrates Mininet, Ryu, traffic generation, and data collection for both packet and flow-level features. The clear separation of concerns, combined with the use of a `config.json` file, enhances maintainability, extensibility, and user-friendliness. The design effectively supports the generation of comprehensive and accurately labeled DDoS datasets for various analytical and machine learning applications.
