# Project Logical Flow Analysis

This document outlines a comprehensive review of the project's logical flow, from configuration to execution and data generation, ensuring consistency and coherence.

## 1. `README.md` Review

*   **Purpose:** Clearly states the project's goal: generating a DDoS dataset in an SDN environment with normal, traditional, and advanced attacks.
*   **Attack Descriptions:** The recent updates clarify the nature of advanced attacks, distinguishing them from traditional high-rate floods and explaining that advanced attacks can encompass both high-rate and low-rate characteristics due to their sophistication and evasion techniques.
*   **Dataset Rationale:** The explanation for the three dataset types (packet, Ryu flow, CICFlow) provides good justification for their existence and different use cases, highlighting their distinct granularities and analytical benefits.
*   **Setup & Configuration:** Steps are clear, including dependency checks and `sudoers` configuration. The `config.json` example is well-placed.
*   **Execution Workflow:** The sequence of events (Ryu, Mininet, collectors, traffic generation, shutdown) is logical and matches the `main.py` implementation.
*   **Adding New Attacks:** Provides a clear guide for extending functionality.
*   **Deliverables:** Lists expected output files and their contents.

## 2. `config.json` Review

*   The structure aligns perfectly with `main.py`'s expectations for `mininet_topology`, `ryu_app`, `controller_port`, `api_port`, `traffic_types` (normal and attacks), and `collection` settings.
*   The `script_name` in attack configurations directly maps to the Python files in the `attacks/` directory, ensuring proper dynamic loading.

## 3. `main.py` Review

*   **Orchestration:** This script acts as the central orchestrator, managing the lifecycle of the Mininet environment, Ryu controller, traffic generation, and data collection.
*   **Privileges:** Correctly checks for `sudo` privileges, which is essential for Mininet operations.
*   **Ryu & Mininet Management:** Starts and stops both components in a logical order, ensuring the network environment is properly set up and torn down.
*   **Data Collection (`_collect_offline_data` and `_collect_online_data`):** Initiates offline (`dumpcap` for PCAP) and online (Ryu API polling for flow stats) collection concurrently using threading. This is an appropriate design for continuous data capture from different sources.
*   **Traffic Generation (`_generate_traffic`):**
    *   Handles normal traffic first, then iterates through configured attacks, maintaining a clear sequence of events.
    *   Dynamically imports attack scripts and calls their `run_attack` function, passing necessary parameters (`attacker_host`, `victim_ip`, `duration`). This approach offers high flexibility for defining and executing diverse attack scenarios.
    *   Uses `attack_thread.join()` to ensure each attack completes before moving to the next. This is crucial for accurate labeling of distinct attack phases and preventing overlap that could complicate analysis.
*   **Labeling:** The `label_timeline` mechanism correctly records the start/end times and labels for each traffic phase. This is critical for post-processing and accurately labeling the generated datasets, allowing for correlation across different data granularities despite their inherent timestamping differences.
*   **Offline Processing:** Calls `process_pcap_to_csv` at the end, ensuring the raw PCAP is converted into the `packet_features.csv` and `cicflow_dataset.csv` (via an external tool like CICFlowMeter).

## 4. Attack Scripts (`attacks/` directory) Review

*   The attack scripts (`gen_syn_flood.py`, `gen_udp_flood.py`, `gen_icmp_flood.py`, `gen_advanced_adversarial_ddos_attacks.py`) consistently expose a `run_attack(attacker_host, victim_ip, duration)` function. This standardized interface is correctly utilized by `main.py` for dynamic execution.
*   The content of these scripts aligns with the described attack types, including both traditional floods and more sophisticated adversarial techniques.

## 5. `process_pcap_to_csv.py` Review

*   Its role is clearly defined: to process the raw PCAP file (`traffic.pcap`) and convert it into a structured CSV format (`packet_features.csv`), integrating the labels from the `label_timeline`. `main.py` correctly calls this script at the end of the data collection phase.

## Conclusion

The overall flow of the project is **logical, robust, and well-structured**. The `main.py` script serves as an effective orchestrator, seamlessly integrating Mininet, Ryu, traffic generation, and data collection. The configuration file provides a flexible and intuitive way to define simulation parameters and attack scenarios. The clear separation of concerns among different modules (topology, controller app, attack scripts, main orchestrator, data processing) enhances maintainability and extensibility. The design effectively supports the generation of a comprehensive and accurately labeled DDoS dataset for various analytical and machine learning applications.