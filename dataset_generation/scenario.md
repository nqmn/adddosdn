# Mininet Host Scenario

This document details the Mininet host scenario for the DDoS dataset generation, outlining the roles of each host and the types of traffic generated.

## Topology Overview

The Mininet topology consists of a single OpenFlow switch (`s1`) connected to six hosts (`h1` through `h6`). Each host is assigned a unique IP address from `10.0.0.1` to `10.0.0.6`.

## Host Roles and Traffic Types

### Attackers

*   **h1 (Attacker 1):** Launches a **TCP-based DDoS attack (SYN Flood)** against the web server (`h6`).
*   **h2 (Attacker 2):** Launches multiple attacks:
    *   A **TCP-based DDoS attack (SYN Flood)** against the web server (`h6`).
    *   A **UDP Flood attack** against the victim host (`h4`).
    *   An **ICMP Flood attack** against the victim host (`h4`).

### Victims

*   **h6 (Web Server Victim):** The target for TCP-based DDoS attacks (SYN Flood) from both `h1` and `h2`.
*   **h4 (General Victim):** The target for UDP Flood and ICMP Flood attacks from `h2`.

### Normal Traffic Generators

The remaining hosts are responsible for generating benign, normal network traffic to simulate a realistic network environment. This traffic helps in creating a balanced dataset with both normal and attack patterns.

*   **h3:** Generates normal traffic, including TCP packets to `h5`.
*   **h5:** Generates normal traffic, including UDP packets to `h3`.

## Traffic Generation Phases

The dataset generation process proceeds through distinct traffic generation phases:

1.  **Normal Traffic Period:** All hosts not designated as attackers or victims for a specific attack type will generate normal background traffic for a configured duration.
2.  **Attack Traffic Period:** During this phase, the configured attackers (`h1`, `h2`) will launch their respective DDoS attacks against their designated victims (`h4`, `h6`). These attacks run concurrently with any ongoing normal traffic.

This structured approach ensures that the generated dataset accurately reflects a mix of normal network operations and various types of DDoS attacks.