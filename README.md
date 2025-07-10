# AdDDoSDN Dataset Framework

A comprehensive Python-based framework for generating, capturing, processing, and documenting network traffic datasets in a Software-Defined Networking (SDN) environment using Mininet and Ryu controller.

## 🚀 Features

- **Multiple Attack Vectors**: SYN Flood, UDP Flood, ICMP Flood, and advanced adversarial attacks
- **SDN Integration**: Native support for OpenFlow/SDN environments via Ryu controller
- **Rich Dataset Output**: Generates packet-level features, flow statistics, and CICFlowMeter-compatible datasets
- **Advanced Evasion Techniques**: IP rotation, protocol fingerprinting evasion, and temporal pattern avoidance
- **Legitimate Traffic Mimicry**: Realistic HTTP headers, sessions, and request patterns

## 📦 Repository Structure

```
.
├── dataset_generation/      # Dataset generation module
│   ├── output/             # Output directory for generated data
│   ├── src/                # Source code for dataset generation
│   │   ├── attacks/        # Attack implementations
│   │   ├── controller/     # Ryu controller application
│   │   └── utils/          # Utility functions
│   ├── TEST.md             # Documentation for test.py
│   ├── test.py             # Main script for dataset generation
│   └── requirements.txt    # Python dependencies for dataset generation
├── LICENSE
├── README.md
└── .git/...
```

## 🛠️ Installation

1.  **Prerequisites**
    ```bash
    # On Ubuntu/Debian
    sudo apt update
    sudo apt install -y python3-pip python3-venv git default-jre
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

### Run the dataset generator
```bash
python dataset_generation/test.py
```



## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📄 Citation

If you use this dataset or framework in your research, please cite our work.
