# Installation and Deployment Guide

This guide outlines the steps to set up and run the SDN DDoS dataset generation module.

## 1. Study and Understand the Code

Before proceeding, it is recommended to familiarize yourself with the project's code structure and requirements. The primary script for dataset generation is `dataset_generation/test.py`. Key directories and files to review include:

-   `dataset_generation/test.py`: The main execution script for dataset generation.
-   `dataset_generation/src/attacks/`: Directory containing various attack scripts used by `test.py`.
-   `dataset_generation/src/controller/`: Contains the Ryu controller application used by `test.py`.
-   `dataset_generation/src/utils/`: Contains utility functions for PCAP processing and other tasks.

## 2. Remote Server Access and Environment Setup

### 2.1. Accessing the Remote Server

Connect to the remote server via SSH using the provided credentials:

```bash
ssh user@jtmksrv -p 656
```

### 2.2. Prerequisites

Mininet and Ryu SDN Framework are already installed on the remote server. Python 3, Pip, and `tshark` (or `tcpdump` on Linux) are also confirmed to be installed.

### 2.3. Install Python Libraries

Install the required Python libraries using pip:

```bash
pip3 install -r dataset_generation/requirements.txt
```

Note: `ryu` and `mininet` are system-level prerequisites and should be installed separately if not already present, as detailed in the main `README.md`.

### 2.4. Transferring the Project Files

Transfer the entire `adversarial-ddos-attacks-sdn-dataset` directory to the remote server. You can use `scp` from your local machine:

```bash
scp -P 656 -r C:/Users/Intel/Desktop/InSDN_ddos_dataset/adversarial-ddos-attacks-sdn-dataset user@jtmksrv:/path/to/remote/directory/
```

Replace `/path/to/remote/directory/` with the desired location on the remote server.

## 3. Deploy and Implement the Dataset Generation

### 3.1. Execution

Execute the main dataset generation script with `sudo` privileges, as Mininet requires root access:

```bash
sudo python3 dataset_generation/test.py
```

#### Expected Workflow (Orchestrated by `dataset_generation/test.py`):

1.  **Cleanup**: Clears any previous Mininet instances.
2.  **Tool Verification**: Checks for the presence of essential command-line tools (`ryu-manager`, `mn`, `tshark`).
3.  **Ryu Controller Startup**: Starts the `ryu_controller_app.py` as a background process and verifies its health.
4.  **Mininet Topology Setup**: Defines and starts a custom Mininet topology with a Ryu controller.
5.  **Connectivity Test**: Runs Mininet's `pingall` test to confirm basic network connectivity.
6.  **Traffic Generation Scenario**:
    -   Initiates packet capture using `tshark`.
    -   Generates benign traffic.
    -   Launches various traditional DDoS attacks (SYN Flood, UDP Flood, ICMP Flood).
    -   Launches advanced adversarial DDoS attacks (TCP State Exhaustion, Application Layer, Multi-Vector).
    -   Includes cooldown periods between phases.
    -   Terminates packet capture.
7.  **Data Processing**:
    -   Verifies PCAP integrity.
    -   Validates and fixes PCAP timestamps.
    -   Converts the captured PCAP data into a labeled CSV file (`labeled_packet_features.csv`), associating each packet with its corresponding traffic phase label.
8.  **Cleanup**: Terminates the Ryu controller process and performs a final Mininet cleanup.

## 4. Deliver Results to the User

### 4.1. Deliverables Verification

Upon successful completion, verify the presence of the following files in the `dataset_generation/output/` directory:

-   `capture.pcap`: The raw packet capture file.
-   `labeled_packet_features.csv`: The primary output dataset with extracted packet features and labels.
-   `ryu.log`: Log file for the Ryu SDN controller.
-   `mininet.log`: Log file for Mininet.
-   `test.log`: The main log file for the `test.py` script.
-   `capture.csv.log`: Error log specifically for the `tshark` capture process.
