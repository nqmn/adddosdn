# AdDDoSDN Dataset Framework

A comprehensive Python-based framework for generating, capturing, processing, and documenting network traffic datasets in a Software-Defined Networking (SDN) environment using Mininet and Ryu controller.

## 🚀 Features

- **Multiple Attack Vectors**: SYN Flood, UDP Flood, ICMP Flood, Slow Read, and advanced adversarial attacks.
- **SDN Integration**: Native support for OpenFlow/SDN environments via Ryu controller, with REST API for flow monitoring.
- **Rich Dataset Output**: Generates both packet-level and flow-level feature datasets (`packet_features.csv`, `flow_features.csv`).
- **Configurable Scenarios**: Easily configure traffic generation durations and parameters via `config.json`.
- **Advanced Evasion Techniques**: Includes TCP State Exhaustion, Application Layer Mimicry, and Slow Read attacks.
- **Modular and Extensible**: Cleanly structured with separate modules for attacks, controller logic, and utilities.

## 📦 Repository Structure

```
.
├── dataset_generation/      # Dataset generation module
│   ├── main_output/        # Default output directory for main.py
│   ├── src/                # Source code for dataset generation
│   │   ├── attacks/        # Attack implementations
│   │   ├── controller/     # Ryu controller application
│   │   └── utils/          # Utility functions
│   ├── config.json         # Configuration file for traffic scenarios
│   ├── main.py             # Primary script for dataset generation
│   ├── test.py             # Script for quick testing
│   └── requirements.txt    # Python dependencies
├── LICENSE
├── README.md
└── .git/...
```

## 🛠️ Installation

1.  **Prerequisites**
    ```bash
    # On Ubuntu/Debian
    sudo apt update
    sudo apt install -y python3-pip python3-venv git default-jre tshark slowhttptest
    ```

2.  **Clone the repository**
    ```bash
    git clone https://github.com/nqmn/AdDDoSSDN-novel_adversarial_ddos_sdn_dataset.git
    cd AdDDoSSDN-novel_adversarial_ddos_sdn_dataset
    ```

3.  **Create and activate virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install dependencies**
    ```bash
    pip install -r dataset_generation/requirements.txt
    ```

## 🚀 Quick Start

1.  **(Optional) Configure the scenario**
    - Edit `dataset_generation/config.json` to change the duration of traffic phases.

2.  **Run the dataset generator**
    ```bash
    sudo python3 dataset_generation/main.py
    ```
    - The generated datasets (`packet_features.csv`, `flow_features.csv`) and logs will be saved in `dataset_generation/main_output/`.

3.  **Run a quick test**
    - For a shorter, non-configurable test run, use `test.py`.
    ```bash
    sudo python3 dataset_generation/test.py
    ```
    - Test outputs will be saved in `dataset_generation/test_output/`.



## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📄 Citation

If you use this dataset or framework in your research, please cite our work.
