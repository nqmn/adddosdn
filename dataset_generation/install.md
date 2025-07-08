# Installation and Deployment Guide

This guide outlines the steps to set up and run the SDN DDoS dataset generation module.

## 1. Study and Understand the Code

Before proceeding, it is recommended to familiarize yourself with the project's code structure and requirements. Key files to review include:

-   `main.py`: The main execution script.
-   `config.json`: Configuration settings for the dataset generation.
-   `topology.py`: Defines the Mininet network topology.
-   `attacks/`: Directory containing various attack scripts.
-   `controller/`: Contains the Ryu controller application.

## 2. Remote Server Access and Environment Setup

### 2.1. Accessing the Remote Server

Connect to the remote server via SSH using the provided credentials:

```bash
ssh user@jtmksrv -p 656
```

### 2.2. Prerequisites

Mininet and Ryu SDN Framework are already installed on the remote server. Python 3, Pip, and dumpcap (or tcpdump on Linux) are also confirmed to be installed.

### 2.3. Install Python Libraries

Install the required Python libraries using pip:

```bash
pip3 install ryu mininet requests webob scapy
```

### 2.4. Transferring the Project Files

Transfer the `adversarial-ddos-attacks-sdn-dataset/dataset_generation` directory to the remote server. You can use `scp` from your local machine:

```bash
scp -P 656 -r C:/Users/Intel/Desktop/InSDN_ddos_dataset/adversarial-ddos-attacks-sdn-dataset/dataset_generation user@jtmksrv:/path/to/remote/directory/
```

Replace `/path/to/remote/directory/` with the desired location on the remote server.

## 3. Deploy and Implement the Dataset Generation

### 3.1. Configuration

The `config.json` file is crucial for the operation. You must update the `cicflowmeter_path` to the absolute path of your `cicflowmeter.sh` executable.

**Example `config.json` snippet:**
```json
{
    "offline_collection": {
        "pcap_file": "traffic.pcap",
        
        "output_file": "offline_dataset.csv"
    }
}
```

### 3.2. Execution

Execute the main script with `sudo` privileges, as Mininet requires root access:

```bash
sudo python3 dataset_generation/main.py
```

#### Expected Workflow:

1.  **Ryu Controller Launch**: The Ryu controller application starts in the background.
2.  **Mininet Initialization**: A 6-host topology is loaded, and the Mininet network starts.
3.  **Data Collector Activation**: Two background threads initiate:
    -   **Offline Collector**: `dumpcap` captures network traffic to `traffic.pcap`.
    -   **Online Collector**: Polls the Ryu controller's REST API for flow statistics every 2 seconds.
4.  **Traffic Generation**:
    -   **Normal Traffic Period**: 60 seconds of benign background traffic.
    -   **Attack Traffic Period**: `hping3` executes a SYN flood attack from `h1` to `h2` for 30 seconds.
5.  **Shutdown and Cleanup**: Data collection stops, Mininet terminates, and the Ryu controller stops.
6.  **Offline Data Processing**: CICFlowMeter processes `traffic.pcap` to generate `offline_dataset.csv`.

## 4. Deliver Results to the User

### 4.1. Deliverables Verification

Upon successful completion, verify the presence of the following files in the `dataset_generation` directory:

-   `offline_dataset.csv`: CSV file with flow features.
-   `online_dataset.csv`: CSV file with flow statistics.
-   `traffic.pcap`: Raw packet capture.

### 4.2. Adding New Attacks (Optional)

To add a new attack type:

1.  **Create an Attack Script**: In `attacks/`, create a new Python file (e.g., `gen_new_attack.py`) with a `run_attack` function:
    ```python
    def run_attack(attacker_host, victim_ip, duration):
        # Your attack logic here
        pass
    ```

2.  **Update `config.json`**: Add a new entry to `traffic_types.attacks` specifying the `type`, `duration`, `attacker`, `victim`, and `script_name` (e.g., `"script_name": "gen_new_attack.py"`).
