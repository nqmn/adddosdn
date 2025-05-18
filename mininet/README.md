# 3-Tier Topology SDN Controller Apps

This project provides a set of Ryu controller applications for a Software Defined Networking (SDN) environment. These apps work together to monitor, mitigate, and log packet-in events, providing a secure and observable network switch behavior.

## Overview

This suite consists of four Ryu apps that together enable:

* Basic L2 switching
* Monitoring and detection of packet-in floods
* Automated mitigation (blocking) of malicious sources
* Logging of packet-in events to a PCAP file

These are designed to be run simultaneously using the Ryu framework.

---

## Components

* **simple\_switch\_13.py**
  Basic OpenFlow 1.3 L2 learning switch implementation.
* **packet\_in\_monitor.py**
  Monitors for excessive packet-in events (potential flooding) and logs warnings.
* **mitigate.py**
  Automatically blocks MAC addresses that exceed a packet-in threshold for a set duration.
* **log\_w\.py**
  Dumps all packet-in events to a PCAP file for later analysis.

---

## Topology

- Remote controller at 192.168.159.132:6633
- 1 switch
  - Hardware interface (default `ens32`) attached
- Four hosts (h2–h5) with custom IPs (10.0.0.2–.5)

**Make sure your real interface (e.g., `ens32`) is UP and has no IP assigned:

## Requirements

* Python 3.x
* [Ryu SDN Framework](https://osrg.github.io/ryu/)
* [Scapy](https://scapy.net/) (for `log_w.py`)

Install requirements (example):

```bash
pip install ryu scapy
```

---

## Usage

Run the following command to start all apps together:

```bash
sudo python3 custom5.py # this is the latest version; add hardware interface to connect to other vm.
```

Or, directly with the Ryu manager:

```bash
ryu-manager simple_switch_13.py # packet_in_monitor.py mitigate.py log_w.py (this is advanced)
```

> **Note:**
> Root privileges (`sudo`) may be required for certain network operations.

---

## Files Description

* **custom5.py**
  *Entry-point script (if used, must import and start all apps above).*

* **simple\_switch\_13.py**
  Implements a simple learning switch using OpenFlow 1.3.

* **packet\_in\_monitor.py**
  Detects packet-in floods by monitoring packet-in rates per MAC address. Logs a warning if a MAC address exceeds 100 packet-ins in 5 seconds.

* **mitigate.py**
  Blocks sources that exceed a threshold by installing a drop flow rule for 60 seconds, preventing further traffic from the offending MAC address.

* **log\_w\.py**
  Writes all incoming packet-in packets to `packet_in.pcap` using Scapy for later inspection with Wireshark or similar tools.

---

## License

MIT License (or specify your own).

---

## Example Output

* **Logs:**
  Look for warnings and errors in the Ryu log output for detection/block events.
* **PCAP:**
  Open `packet_in.pcap` in Wireshark for captured packet-in data.

---

## Contact

For issues or questions, open an issue on your repository or contact the author.

---

Let me know if you want to add usage examples, troubleshooting, or a diagram!
