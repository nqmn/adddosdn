# InSDN DDoS Dataset Generation Framework

This framework is designed to generate a comprehensive dataset of both traditional and advanced adversarial DDoS attacks in a simulated Software-Defined Networking (SDN) environment. It automates the entire process, from setting up the network topology to generating, capturing, and labeling network traffic.

## Overview

The core of this framework is a set of Python scripts that leverage Mininet for network emulation, Ryu as the SDN controller, and various traffic generation tools to simulate a realistic network environment. The framework generates two primary types of datasets:

*   **Packet-Level Dataset:** Contains detailed information for each captured packet, including protocol-specific features and labels.
*   **Flow-Level Dataset:** Contains aggregated flow statistics collected from the SDN controller, providing a higher-level view of network traffic.

The framework is designed to be flexible and extensible, allowing researchers and developers to customize the network topology, traffic generation scenarios, and feature extraction process to suit their specific needs.

## Prerequisites

Before you begin, ensure you have the following installed on an Ubuntu system:

*   **Python 3**
*   **Mininet:** A network emulator for rapid prototyping of SDN.
*   **Ryu:** An SDN controller framework.
*   **TShark:** A network protocol analyzer (part of Wireshark).
*   **Slowhttptest:** A tool for testing web servers for slow HTTP attacks.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/adversarial-ddos-attacks-sdn-dataset.git
    cd adversarial-ddos-attacks-sdn-dataset/dataset_generation
    ```

2.  **Install dependencies:**
    *   **System Dependencies:**
        ```bash
        sudo apt-get update
        sudo apt-get install -y mininet ryu-manager tshark slowhttptest
        ```
    *   **Python Dependencies:**
        ```bash
        pip install -r requirements.txt
        ```

## Usage

The framework provides two main scripts for dataset generation: `main.py` for the full dataset and `test.py` for a smaller, test version.

### Generating the Full Dataset

The `main.py` script generates the complete dataset using the durations specified in `config.json`.

```bash
sudo python3 main.py
```

### Generating the Test Dataset

The `test.py` script generates a smaller dataset with fixed, shorter durations, ideal for quick testing and validation.

```bash
sudo python3 test.py
```

### Analyzing the Dataset

After generation, you can use the `calculate_percentages.py` script to get a statistical overview of the generated data.

```bash
python3 calculate_percentages.py [main_output | test_output]
```

## Directory Structure

```
.
├── config.json                 # Configuration for traffic generation durations
├── main.py                     # Main script for full dataset generation
├── test.py                     # Script for test dataset generation
├── requirements.txt            # Python dependencies
├── calculate_percentages.py    # Script for dataset statistics
├── files/
│   ├── Label_binary.txt
│   ├── Label_multi.txt
│   ├── packet_feature_names.txt
│   └── flow_feature_names.txt
├── src/
│   ├── attacks/                # Scripts for generating attack traffic
│   ├── controller/             # Ryu controller application
│   └── utils/                  # Utility functions for PCAP processing
├── main_output/                # Output directory for main.py
│   ├── flow_features.csv
│   ├── packet_features.csv
│   └── *.pcap
└── test_output/                # Output directory for test.py
    ├── flow_features.csv
    ├── packet_features.csv
    └── *.pcap
```

## Documentation

For a detailed explanation of the dataset generation logic, traffic scenarios, and feature sets, please refer to the following documents:

*   **[MAIN.md](MAIN.md):** Comprehensive documentation for the `main.py` script and the full dataset generation process.
*   **[TEST.md](TEST.md):** Documentation for the `test.py` script and the test dataset generation process.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.