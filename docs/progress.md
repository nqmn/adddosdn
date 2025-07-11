# Adversarial DDoS Attacks SDN Dataset - Progress

## Current Status

The project has been significantly refactored to improve modularity, configurability, and the richness of the generated datasets. The core functionality is now driven by `dataset_generation/main.py`, which uses `dataset_generation/config.json` to define traffic scenarios.

## Recent Progress

-   **Primary Script Refactoring**: Introduced `main.py` as the main, configurable dataset generation script. `test.py` is now used for quick, non-configurable testing.
-   **Configuration File**: Added `config.json` to allow users to easily define the duration of each traffic and attack phase without modifying the source code.
-   **Flow-Level Feature Generation**: Implemented a new data collection mechanism (`collect_flow_stats`) that uses the Ryu controller's REST API to gather and label flow statistics, producing `flow_features.csv`.
-   **New Adversarial Attack**: Added a "Slow Read" DDoS attack (`ad_slow`) to the adversarial arsenal, utilizing the `slowhttptest` tool.
-   **Modular PCAP Generation**: The framework now generates separate `.pcap` files for each traffic phase (e.g., `normal.pcap`, `syn_flood.pcap`), which are then processed and combined into the final `packet_features.csv`.
-   **Enhanced Logging**: Improved logging by creating separate log files for the main script (`main.log`), attacks (`attack.log`), Ryu (`ryu.log`), and Mininet (`mininet.log`).
-   **Documentation Overhaul**: Updated all documentation (`README.md`, `docs/*`) to reflect the new architecture, scripts, features, and outputs.

## Next Steps

-   Continue to refine the data processing and feature engineering for both packet and flow-level datasets.
-   Explore the addition of more sophisticated adversarial attack vectors.
-   Further enhance documentation with more detailed analysis of the generated datasets.