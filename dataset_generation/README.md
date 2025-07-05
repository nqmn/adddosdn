# AI Agent Onboarding: SDN DDoS Dataset Generation

**Objective:** This guide provides a comprehensive, step-by-step workflow for an AI agent to deploy and operate this dataset generation module. The goal is to produce `offline_dataset.csv` and `online_dataset.csv` by simulating a DDoS attack in a Mininet-emulated SDN environment.

## 1. Environment Verification and Setup

Before execution, verify that the following dependencies are installed and available in the system's `PATH`. Execute the following commands to check for their presence:

```bash
# 1.1. Verify Python and Pip
python3 --version
pip3 --version

# 1.2. Verify Mininet
sudo mn --version

# 1.3. Verify Ryu SDN Framework
ryu-manager --version



# 1.5. Verify dumpcap (or tcpdump on Linux)
dumpcap --version
```

If any of these commands fail, the dependency is not met. The agent must install the missing software before proceeding.

### 1.6. Install Python Libraries

Run the following command to install the required Python libraries:

```bash
pip3 install requests mininet
```

## 2. Configuration

The `config.json` file is the single source of truth for this operation. The critical value to configure is `cicflowmeter_path`.

- **Action:** You must locate the `cicflowmeter.sh` (or equivalent) executable on the system and update the `cicflowmeter_path` value in `config.json` with its absolute path.

**Example `config.json`:**
```json
{
    "mininet_topology": "dataset_generation/topology.py",
    "ryu_app": "dataset_generation/controller/ryu_controller_app.py",
    "controller_port": 6633,
    "api_port": 8080,
    "traffic_types": {
        "normal": {
            "duration": 60
        },
        "attack": {
            "type": "syn_flood",
            "duration": 30,
            "hping3_options": "-S --flood -V"
        }
    },
    "offline_collection": {
        "pcap_file": "traffic.pcap",
        "cicflowmeter_path": "/path/to/your/cicflowmeter/bin/cicflowmeter.sh",
        "output_file": "offline_dataset.csv"
    },
    "online_collection": {
        "output_file": "online_dataset.csv",
        "poll_interval": 2
    }
}
```

## 3. Execution Workflow

Execute the main script with `sudo` privileges. This is non-negotiable, as Mininet requires root access to create and manage virtual network interfaces.

```bash
sudo python3 dataset_generation/main.py
```

### Expected Execution Sequence:

1.  **Ryu Controller Launch**: The script will first launch the Ryu controller application in the background.
2.  **Mininet Initialization**: The custom 6-host topology will be loaded, and the Mininet network will start.
3.  **Data Collector Activation**: Two background threads will be initiated:
    - **Offline Collector**: `dumpcap` will start capturing all network traffic on the `any` interface, saving it to `traffic.pcap`.
    - **Online Collector**: A polling mechanism will begin querying the Ryu controller's REST API every 2 seconds for flow statistics.
4.  **Traffic Generation**: The script will proceed through two phases:
    - **Normal Traffic Period (60s)**: The simulation will run for 60 seconds with only benign background traffic.
    - **Attack Traffic Period (30s)**: `hping3` will be launched on host `h1` to execute a SYN flood attack against host `h2` for 30 seconds.
5.  **Shutdown and Cleanup**: Once traffic generation is complete, the script will:
    - Stop the data collection threads.
    - Terminate the Mininet network.
    - Stop the Ryu controller.
6.  **Offline Data Processing**: The script will invoke CICFlowMeter to process the `traffic.pcap` file and generate the final `offline_dataset.csv`.

## 5. Deliverables Verification

## 4. Adding New Attacks

To add a new attack type to the dataset generation process, follow these steps:

1.  **Create an Attack Script**: In the `attacks/` directory, create a new Python file (e.g., `gen_new_attack.py`). This script must contain a function named `run_attack` that accepts three arguments:
    -   `attacker_host`: The Mininet host object from which the attack will originate.
    -   `victim_ip`: The IP address of the target victim.
    -   `duration`: The duration (in seconds) for which the attack should run.

    Example structure for `gen_new_attack.py`:
    ```python
    from scapy.all import Ether, IP, TCP, sendp
    import time

    def run_attack(attacker_host, victim_ip, duration):
        print(f"Starting New Attack from {attacker_host.name} to {victim_ip} for {duration} seconds.")
        start_time = time.time()
        while time.time() - start_time < duration:
            # Your attack logic here, e.g., sendp(Ether()/IP(dst=victim_ip)/TCP(dport=80, flags='S'))
            pass
        print(f"New Attack from {attacker_host.name} to {victim_ip} finished.")
    ```

2.  **Update `config.json`**: Open `config.json` and add a new entry to the `traffic_types.attacks` array. This entry should specify the `type` of the attack, its `duration`, the `attacker` host, the `victim` host, and the `script_name` (the filename of your new attack script).

    Example addition to `config.json`:
    ```json
    {
        "type": "new_attack_type",
        "duration": 45,
        "attacker": "h1",
        "victim": "h3",
        "script_name": "gen_new_attack.py"
    }
    ```

By following these steps, `main.py` will automatically discover and execute your new attack script during the dataset generation process.

Upon successful completion, verify that the following files have been created in the `dataset_generation` directory:

- `offline_dataset.csv`: A CSV file containing flow features extracted by CICFlowMeter.
- `online_dataset.csv`: A CSV file containing flow statistics polled from the Ryu controller.
- `traffic.pcap`: The raw packet capture from the simulation.

If these files are present, the operation was a success.