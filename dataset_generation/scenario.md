# DDoS Attack Scenarios

This document details the various DDoS attack scenarios implemented in the system.

## 1. ICMP Flood Attack

**Description:**
The ICMP Flood attack is a denial-of-service attack in which an attacker overwhelms a target system with a large volume of ICMP (Internet Control Message Protocol) echo request packets, also known as "ping" requests. The goal is to consume the target's network bandwidth and processing resources, making it unresponsive to legitimate traffic.

**How it happens in the scenario:**
- **Source:** `gen_icmp_flood.py`
- An `attacker_host` continuously sends ICMP echo request packets to a `victim_ip`.
- The `scapy` library is used to craft and send these packets.
- Each packet consists of an Ethernet frame, an IP header (with the victim's IP as destination), and an ICMP echo request.
- The packets are sent in a loop with a small inter-packet delay (0.01 seconds) to maximize the flood.
- The attack runs for a specified `duration`, after which the process is gracefully stopped.

## 2. SYN Flood Attack

**Description:**
The SYN Flood attack exploits the TCP three-way handshake mechanism. An attacker sends a large number of TCP SYN (synchronize) requests to a target server but never completes the handshake by sending the final ACK (acknowledgment) packet. This leaves the server with many half-open connections, exhausting its connection table and preventing it from accepting new legitimate connections.

**How it happens in the scenario:**
- **Source:** `gen_syn_flood.py`
- An `attacker_host` sends a continuous stream of TCP SYN packets to a `victim_ip` on port 80 (HTTP).
- The `scapy` library is used to craft these packets.
- Each packet includes an Ethernet frame, an IP header, and a TCP header with the SYN flag set.
- Similar to the ICMP flood, packets are sent in a loop with a small inter-packet delay (0.01 seconds).
- The attack runs for a specified `duration`, after which the process is gracefully stopped.

## 3. UDP Flood Attack

**Description:**
The UDP Flood attack is a denial-of-service attack where the attacker overwhelms a target system with a large volume of UDP (User Datagram Protocol) packets. The attacker often spoofs the source IP address to make it harder to trace the origin. When these packets arrive at the victim, the victim's system attempts to process them, often by sending an ICMP "Destination Unreachable" packet back to the spoofed source, consuming resources and bandwidth.

**How it happens in the scenario:**
- **Source:** `gen_udp_flood.py`
- An `attacker_host` sends a flood of UDP packets to a `victim_ip`, typically targeting a common UDP port like 53 (DNS).
- The `scapy` library is used to craft the packets.
- Each packet contains an Ethernet frame, an IP header, and a UDP header.
- The packets are sent in a continuous loop with a small inter-packet delay (0.01 seconds).
- The attack runs for a specified `duration`, after which the process is gracefully stopped.

## 4. Advanced Adversarial DDoS Attacks

**Description:**
This category encompasses more sophisticated DDoS attacks designed to evade detection and mimic legitimate traffic patterns. They often involve IP address rotation, advanced packet crafting, and multi-vector approaches.

**Source:** `gen_advanced_adversarial_ddos_attacks.py`

This module implements several advanced techniques:

### 4.1. TCP State Exhaustion (ad_syn variant)

**Description:**
This attack aims to exhaust the target's TCP connection state table by initiating many TCP handshakes but not completing them, similar to a SYN flood, but with more sophisticated manipulation of sequence numbers and window sizes to appear more legitimate and keep connections "half-open" for longer.

**How it happens in the scenario:**
- Uses an `IPRotator` to generate random source IP addresses, making it harder to block based on IP.
- Crafts TCP SYN packets with randomized sequence numbers, window sizes, and TTL (Time To Live) values.
- Sends SYN packets and attempts to receive SYN-ACK replies. If a SYN-ACK is received, an ACK packet is sent to establish a "half-open" connection, but no further data is exchanged, consuming server resources.
- Includes jitter in packet sending to avoid detection based on timing patterns.

### 4.2. Distributed Application Layer Attack (ad_udp variant)

**Description:**
This attack targets the application layer (e.g., HTTP) by sending legitimate-looking requests to resource-intensive endpoints on the victim server. The goal is to consume server processing power, database resources, or application-specific bandwidth rather than just network bandwidth.

**How it happens in the scenario:**
- Uses an `IPRotator` for source IP randomization.
- Employs a `PacketCrafter` to generate HTTP requests with varied methods (GET, POST, HEAD, OPTIONS), paths (including resource-heavy ones like search queries, API calls, large file downloads), and realistic User-Agent strings.
- Randomly adds common HTTP headers and sometimes cookies to appear more legitimate.
- Sends these crafted HTTP requests to the target, mimicking distributed legitimate user traffic.
- Variable timing between requests helps evade detection.

### 4.3. Multi-Vector Attack

**Description:**
A multi-vector attack combines several different attack types simultaneously. This approach makes it more challenging for defense systems to mitigate, as they need to address multiple attack vectors at once.

**How it happens in the scenario:**
- Launches threads for different attack vectors concurrently, such as:
    - TCP State Exhaustion
    - Distributed Application Layer Attack
    - Slow Read Attack
- The `AdvancedDDoSCoordinator` manages the execution of these combined attacks.

### 4.4. Slow Read Attack (ad_slow variant)

**Description:**
A Slow Read attack is a type of low-bandwidth, application-layer DDoS attack that aims to exhaust the server's connection pool by reading responses very slowly. The attacker opens a connection and then reads the response data byte by byte, or in very small chunks, over a long period. This keeps the server's resources tied up, waiting for the client to finish reading, eventually leading to a denial of service for new connections.

**How it happens in the scenario:**
- **Tool Used:** `slowhttptest`
- The `attacker_host` executes the `slowhttptest` command in "Slow Read" mode (`-t SR`).
- It establishes a specified number of connections (`-c 100`) to the victim's HTTP server.
- The tool is configured to read data very slowly (`-i 10` for interval, `-r 20` for connections per second).
- The attack runs for a defined `duration` (`-l`).
- This ties up server resources as the server waits for the slow client to receive the full response, eventually exhausting the server's connection capacity.

### 4.5. Adaptive Attack Coordination

**Description:**
The `AdvancedDDoSCoordinator` and `AdaptiveController` components work together to make the advanced attacks more dynamic and evasive. They monitor the target's response and adapt the attack strategy accordingly.

**How it happens in the scenario:**
- **Monitoring:** The `AdaptiveController` continuously probes the target to measure response times and detect potential countermeasures (e.g., rate limiting, WAF blocking, Cloudflare, CAPTCHA, timeouts).
- **Adaptation:** Based on the monitoring results, the `AdaptiveController` recommends optimal attack parameters (e.g., packet rate, connection count, preferred technique, IP rotation speed).
- **Execution:** The `AdvancedDDoSCoordinator` uses these recommendations to dynamically switch between or adjust the parameters of the TCP State Exhaustion, Distributed Application Layer, or Multi-Vector attacks, making the overall attack more resilient and harder to defend against.
- **Session Maintenance:** The `SessionMaintainer` creates and maintains legitimate-looking HTTP sessions to further blend the attack traffic with normal user activity.

## 5. Benign Traffic Generation

**Description:**
Benign traffic simulates normal network activity to provide a realistic background for the DDoS attack scenarios. This helps in evaluating the effectiveness of detection mechanisms in a mixed traffic environment.

**How it happens in the scenario:**
- **Source:** `src/gen_benign_traffic.py`
- Various types of benign traffic are generated between `h3` and `h5` in the Mininet network.
- **Protocols Covered:**
    - **ICMP:** Standard ping requests and replies.
    - **TCP:** Full TCP handshake (SYN, SYN-ACK, ACK) followed by data transfer and a final ACK. This includes random payload lengths.
    - **UDP:** Datagrams with random payload lengths.
    - **Telnet (Port 23):** TCP handshake followed by simulated Telnet command data.
    - **SSH (Port 22):** TCP handshake followed by simulated encrypted SSH data.
    - **FTP (Port 21):** TCP handshake followed by simulated FTP file transfer data.
    - **HTTP (Port 80):** TCP handshake followed by simulated HTTP GET requests with headers and random payload.
    - **HTTPS (Port 443):** TCP handshake followed by simulated encrypted HTTPS application data.
    - **DNS (Port 53):** UDP-based DNS queries.
- **Traffic Generation:**
    - ICMP traffic uses Mininet's `ping` command.
    - All other traffic types are crafted and sent using the `scapy` library within the Mininet host's namespace.
    - Random source ports and random payload lengths are used to simulate varied legitimate traffic.
- The benign traffic runs for a specified `duration`, continuously generating sessions across different protocols.