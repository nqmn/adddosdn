# Installation and Deployment Guide

This guide outlines the steps to set up and run the SDN DDoS dataset generation module.

## 1. Study and Understand the Code

Before proceeding, it is recommended to familiarize yourself with the project's code structure. The primary script for dataset generation is `dataset_generation/main.py`, which is configured via `dataset_generation/config.json`. Key directories and files to review include:

-   `dataset_generation/main.py`: The main execution script for dataset generation.
-   `dataset_generation/config.json`: Configuration file for scenario durations.
-   `dataset_generation/test.py`: A smaller, self-contained script for testing purposes.
-   `dataset_generation/src/attacks/`: Directory containing various attack scripts.
-   `dataset_generation/src/controller/`: Contains the Ryu controller application.
-   `dataset_generation/src/utils/`: Contains utility functions for PCAP processing and other tasks.

## 2. Remote Server Access and Environment Setup

### 2.1. Accessing the Remote Server

Connect to the remote server via SSH using the provided credentials:

```bash
ssh user@jtmksrv -p 656
```

### 2.2. Prerequisites

Ensure that Mininet, Ryu, Python 3, Pip, and the following command-line tools are installed on the remote server. On a fresh Ubuntu system, you can install them with:

```bash
sudo apt-get update
sudo apt-get install -y mininet ryu-bin python3-pip tshark slowhttptest
```

### 2.3. Install Python Libraries

Install the required Python libraries using pip:

```bash
pip3 install -r dataset_generation/requirements.txt
```

### 2.4. Transferring the Project Files

Transfer the entire `adversarial-ddos-attacks-sdn-dataset` directory to the remote server. You can use `scp` from your local machine:

```bash
scp -P 656 -r C:/Users/Intel/Desktop/InSDN_ddos_dataset/adversarial-ddos-attacks-sdn-dataset user@jtmksrv:/path/to/remote/directory/
```

Replace `/path/to/remote/directory/` with the desired location on the remote server.

## 3. Deploy and Implement the Dataset Generation

### 3.1. Configuration

Before running the main script, you can customize the duration of each traffic phase by editing `dataset_generation/config.json`.

### 3.2. Execution

Execute the main dataset generation script with `sudo` privileges, as Mininet requires root access:

```bash
sudo python3 dataset_generation/main.py
```

#### Expected Workflow (Orchestrated by `main.py`):

1.  **Cleanup**: Clears any previous Mininet instances.
2.  **Tool Verification**: Checks for essential tools (`ryu-manager`, `mn`, `tshark`, `slowhttptest`).
3.  **Ryu Controller Startup**: Starts the `ryu_controller_app.py` and verifies its health via its REST API.
4.  **Mininet Topology Setup**: Starts a custom Mininet topology with a Ryu controller.
5.  **Connectivity Test**: Runs `pingall` to confirm network connectivity.
6.  **Traffic Generation Scenario**:
    *   Starts a background thread to collect **flow statistics** from the Ryu controller's API.
    *   For each phase in `config.json` (normal, syn_flood, etc.):
        *   Starts a dedicated packet capture (`tshark`).
        *   Executes the corresponding traffic/attack script.
        *   Stops the packet capture.
7.  **Data Processing**:
    *   The flow statistics collector saves its data to `flow_features.csv`.
    *   Each individual `.pcap` file is processed to fix timestamps and extract packet-level features.
    *   The resulting data is combined into a single `packet_features.csv` file.
8.  **Cleanup**: Terminates the Ryu controller and cleans up the Mininet environment.

## 4. Deliver Results to the User

### 4.1. Deliverables Verification

Upon successful completion, verify the presence of the following files in the `dataset_generation/main_output/` directory:

-   `packet_features.csv`: The primary packet-level dataset.
-   `flow_features.csv`: The flow-level dataset.
-   Individual `.pcap` files for each phase (e.g., `normal.pcap`, `syn_flood.pcap`).
-   Log files: `main.log`, `ryu.log`, `mininet.log`, `attack.log`.
