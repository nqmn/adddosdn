# DDoS Attack Scenarios

This document details the various DDoS attack scenarios implemented in the system.

## ⏱️ Timing Configuration & Dataset Balance

### Default vs Recommended Configuration

| Traffic Type | Default Duration | Default Packets | Recommended Duration | Expected Packets | Improvement |
|--------------|------------------|-----------------|---------------------|------------------|-------------|
| **Normal Traffic** | 20 min | 7,713 | 60 min | ~230,000 | 30x increase ✅ |
| **SYN Flood** | 20 min | 411,413 | 5 min | ~100,000 | 4x reduction ⚖️ |
| **UDP Flood** | 20 min | 211,097 | 5 min | ~100,000 | 2x reduction ⚖️ |
| **ICMP Flood** | 20 min | 413,016 | 5 min | ~100,000 | 4x reduction ⚖️ |
| **Adversarial TCP** | 40 min | 221 | 120 min | ~80,000 | 360x increase ✅ |
| **Adversarial UDP** | 40 min | 253 | 80 min | ~60,000 | 240x increase ✅ |
| **Adversarial Slow** | 40 min | 2,479 | 60 min | ~50,000 | 20x increase ✅ |

### Performance Metrics
- **Current total runtime**: ~3 hours → **Recommended runtime**: ~6-6.5 hours
- **Current dataset size**: 185M → **Expected size**: ~400M  
- **Dataset balance**: Severely imbalanced → Well balanced for ML training

### Configuration File (`config.json`)
```json
{
    "scenario_durations": {
        "initialization": 5,
        "normal_traffic": 3600,    // 1 hour for proper baseline
        "syn_flood": 300,          // 5 min - sufficient for traditional attacks
        "udp_flood": 300,          // 5 min - efficient attack sampling  
        "icmp_flood": 300,         // 5 min - reduced storage requirements
        "ad_syn": 7200,            // 2 hours - adversarial needs more time
        "ad_udp": 4800,            // 80 min - complex evasion techniques
        "ad_slow": 3600,           // 1 hour - slow attack characteristics
        "cooldown": 5
    }
}
```

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

### 4.6. Advanced Evasion Techniques

**Description:**
To enhance stealth and bypass heuristic detection rules, the advanced adversarial attacks incorporate several evasion techniques:

- **Jittered Intervals and Randomization:** Packet and request sending intervals are randomized using `random.uniform()` to avoid predictable timing patterns that could indicate synthetic traffic. Source IP addresses, TCP sequence numbers, window sizes, and TTL values are also randomized.
- **TCP Flag Rotation:** TCP packets are crafted with a random selection of common TCP flags (SYN, SYN-ACK, ACK, PSH-ACK, FIN-ACK) to mimic varied legitimate TCP communication.
- **HTTP Header Rotation:** HTTP requests utilize a diverse set of User-Agent strings and randomly include Referer headers to simulate browsing behavior from different clients and sources.
- **Mimicking Benign Traffic:** The `SessionMaintainer` component actively creates and maintains persistent, legitimate-looking HTTP sessions, including navigating through various common web paths and handling cookies, to blend malicious traffic with normal user activity.
- **Payload and Timestamp Variability:** While explicit timestamp manipulation is handled by the OS/Scapy, the attacks introduce variability in payloads (e.g., varying query string lengths in HTTP requests) and manipulate TCP sequence numbers to ensure generated datasets do not appear overly synthetic.
- **Logging Emission Rates (Partial Implementation):** The `attack_logger` logs when packets/requests are sent, providing a basis for understanding traffic flow. However, explicit real-time calculation and logging of the precise emission rates (packets/sec or requests/sec) for verification of consistency and stealth are not fully implemented. This would require additional logic to track and report rates.

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