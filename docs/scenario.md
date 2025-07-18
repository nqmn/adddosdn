# 🎭 Attack Scenarios and Network Architecture

This document provides a comprehensive overview of the network architecture, attack scenarios, and data generation process for the AdDDoSDN framework.

## 🏗️ Network Architecture

### SDN Network Topology

```mermaid
graph TD
    subgraph "SDN Controller Layer"
        ryu[Ryu Controller<br/>Port 6633<br/>REST API: 8080]
    end
    
    subgraph "SDN Data Plane"
        s1[OpenFlow Switch s1<br/>OpenFlow 1.3]
        
        s1 --- h1[🔴 Attacker 1<br/>h1: 10.0.0.1<br/>SYN Flood Source]
        s1 --- h2[🔴 Attacker 2<br/>h2: 10.0.0.2<br/>Multi-Attack Source]
        s1 --- h3[🟢 Normal Host<br/>h3: 10.0.0.3<br/>Benign Traffic]
        s1 --- h4[🔵 Victim 1<br/>h4: 10.0.0.4<br/>UDP/ICMP Target]
        s1 --- h5[🟢 Normal Host<br/>h5: 10.0.0.5<br/>Benign Traffic]
        s1 --- h6[🔵 Web Server<br/>h6: 10.0.0.6<br/>HTTP Target]
    end
    
    ryu -.->|OpenFlow Control| s1
    
    style h1 fill:#ffcccc,stroke:#ff0000,stroke-width:2px
    style h2 fill:#ffcccc,stroke:#ff0000,stroke-width:2px
    style h3 fill:#ccffcc,stroke:#00ff00,stroke-width:2px
    style h4 fill:#ccccff,stroke:#0000ff,stroke-width:2px
    style h5 fill:#ccffcc,stroke:#00ff00,stroke-width:2px
    style h6 fill:#ccccff,stroke:#0000ff,stroke-width:2px
    style ryu fill:#ffffcc,stroke:#ffaa00,stroke-width:2px
    style s1 fill:#f0f0f0,stroke:#333,stroke-width:2px
```

### Host Roles and Responsibilities

| Host | IP Address | Role | Primary Function | Attack Types |
|------|------------|------|------------------|--------------|
| **h1** | 10.0.0.1 | Primary Attacker | SYN Flood Generator | Traditional SYN Flood |
| **h2** | 10.0.0.2 | Multi-Attack Source | Advanced Attack Platform | UDP Flood, ICMP Flood, Adversarial Attacks |
| **h3** | 10.0.0.3 | Normal Traffic Generator | Benign Traffic Source | HTTP, DNS, SMTP, FTP |
| **h4** | 10.0.0.4 | Primary Victim | Attack Target | UDP/ICMP Flood Target |
| **h5** | 10.0.0.5 | Normal Traffic Generator | Benign Traffic Source | HTTP, DNS, SMTP, FTP |
| **h6** | 10.0.0.6 | Web Server Victim | HTTP Service Target | SYN Flood, Adversarial Attacks |

## 🎯 Attack Scenario Timeline

### 7-Phase Attack Sequence

```mermaid
gantt
    title Attack Scenario Timeline
    dateFormat X
    axisFormat %H:%M
    
    section Normal Traffic
    Baseline Traffic         :normal, 0, 3600
    
    section Traditional Attacks
    SYN Flood               :syn, 3600, 300
    UDP Flood               :udp, 3900, 300
    ICMP Flood              :icmp, 4200, 300
    
    section Adversarial Attacks
    Advanced SYN            :adsyn, 4500, 7200
    Advanced UDP            :adudp, 11700, 4800
    Advanced Slow           :adslow, 16500, 7200
    
    section Data Collection
    Continuous Monitoring   :monitor, 0, 23700
```

### Phase-by-Phase Breakdown

```mermaid
flowchart TD
    A[Phase 1: Network Initialization<br/>5 seconds] --> B[Phase 2: Normal Traffic<br/>1 hour<br/>h3 ↔ h5]
    B --> C[Phase 3: SYN Flood<br/>5 minutes<br/>h1 → h6:80]
    C --> D[Phase 4: UDP Flood<br/>5 minutes<br/>h2 → h4:53]
    D --> E[Phase 5: ICMP Flood<br/>5 minutes<br/>h2 → h4]
    E --> F[Phase 6: Advanced SYN<br/>2 hours<br/>h2 → h6:80]
    F --> G[Phase 7: Advanced UDP<br/>1.33 hours<br/>h2 → h6:80]
    G --> H[Phase 8: Advanced Slow<br/>2 hours<br/>h2 → h6:80]
    H --> I[Phase 9: Cooldown<br/>10 seconds]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#ffebee
    style D fill:#ffebee
    style E fill:#ffebee
    style F fill:#fff3e0
    style G fill:#fff3e0
    style H fill:#fff3e0
    style I fill:#e8f5e8
```

## 🔴 Attack Details

### Traditional DDoS Attacks

#### 1. SYN Flood Attack
```mermaid
sequenceDiagram
    participant h1 as h1 (Attacker)
    participant s1 as Switch s1
    participant h6 as h6 (Web Server)
    
    Note over h1,h6: SYN Flood Attack (5 minutes)
    
    loop Every 0.01 seconds
        h1->>s1: TCP SYN to 10.0.0.6:80
        s1->>h6: Forward SYN packet
        h6->>s1: TCP SYN+ACK response
        s1->>h1: Forward SYN+ACK
        Note over h1: Never sends ACK<br/>(Half-open connection)
    end
    
    Note over h6: Connection table exhausted<br/>Service degradation
```

#### 2. UDP Flood Attack
```mermaid
sequenceDiagram
    participant h2 as h2 (Attacker)
    participant s1 as Switch s1
    participant h4 as h4 (Victim)
    
    Note over h2,h4: UDP Flood Attack (5 minutes)
    
    loop Every 0.01 seconds
        h2->>s1: UDP packet to 10.0.0.4:53
        s1->>h4: Forward UDP packet
        h4->>s1: ICMP Port Unreachable
        s1->>h2: Forward ICMP response
    end
    
    Note over h4: Bandwidth exhausted<br/>Service disruption
```

#### 3. ICMP Flood Attack
```mermaid
sequenceDiagram
    participant h2 as h2 (Attacker)
    participant s1 as Switch s1
    participant h4 as h4 (Victim)
    
    Note over h2,h4: ICMP Flood Attack (5 minutes)
    
    loop Every 0.01 seconds
        h2->>s1: ICMP Echo Request
        s1->>h4: Forward ICMP packet
        h4->>s1: ICMP Echo Reply
        s1->>h2: Forward ICMP reply
    end
    
    Note over h4: Network layer saturated<br/>Bandwidth consumed
```

### Advanced Adversarial Attacks

#### 1. Advanced SYN Attack (TCP State Exhaustion)
```mermaid
flowchart TD
    A[Start Advanced SYN Attack] --> B[IP Rotation Pool<br/>Multiple Source IPs]
    B --> C[Burst Pattern Generation<br/>Variable rate + jitter]
    C --> D[TCP SYN to h6:80<br/>Realistic headers]
    D --> E[Adaptive Rate Control<br/>Evade detection]
    E --> F[Connection Tracking<br/>Maintain state]
    F --> G{Duration Complete?}
    G -->|No| C
    G -->|Yes| H[Attack Complete]
    
    style A fill:#fff3e0
    style H fill:#e8f5e8
```

#### 2. Advanced UDP Attack (Application Layer Mimicry)
```mermaid
flowchart TD
    A[Start Application Mimicry] --> B[Realistic HTTP Requests<br/>Varied User Agents]
    B --> C[Legitimate-looking Payloads<br/>Valid HTTP headers]
    C --> D[UDP to h6:80<br/>Mimicking HTTP]
    D --> E[IP Rotation<br/>Evade source tracking]
    E --> F[Timing Patterns<br/>Human-like intervals]
    F --> G{Duration Complete?}
    G -->|No| C
    G -->|Yes| H[Attack Complete]
    
    style A fill:#fff3e0
    style H fill:#e8f5e8
```

#### 3. Slow Read Attack
```mermaid
sequenceDiagram
    participant h2 as h2 (Attacker)
    participant s1 as Switch s1
    participant h6 as h6 (Web Server)
    
    Note over h2,h6: Slow Read Attack (2 hours)
    
    h2->>s1: HTTP GET request
    s1->>h6: Forward HTTP request
    h6->>s1: HTTP response headers
    s1->>h2: Forward response headers
    
    Note over h2: Slowly consume response<br/>Keep connection alive
    
    loop Every 10 seconds
        h2->>s1: Read small chunks
        s1->>h6: Forward read request
        h6->>s1: Send data chunk
        s1->>h2: Forward data chunk
    end
    
    Note over h6: Connection resources exhausted<br/>100 concurrent connections
```

## 🟢 Normal Traffic Patterns

### Multi-Protocol Benign Traffic

```mermaid
flowchart LR
    subgraph "Normal Traffic Types"
        A[HTTP/HTTPS<br/>Web Browsing] --> B[DNS Queries<br/>Name Resolution]
        B --> C[SMTP Traffic<br/>Email Simulation]
        C --> D[FTP Traffic<br/>File Transfer]
        D --> E[SSH/Telnet<br/>Remote Access]
        E --> F[ICMP Ping<br/>Connectivity Tests]
    end
    
    subgraph "Traffic Sources"
        h3[h3: 10.0.0.3] -.-> A
        h5[h5: 10.0.0.5] -.-> A
    end
    
    style A fill:#e8f5e8
    style B fill:#e8f5e8
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
    style F fill:#e8f5e8
```

## 📊 Data Collection Architecture

### Three-Layer Data Collection

```mermaid
flowchart TB
    subgraph "Data Collection Layer"
        A[Packet Capture<br/>tcpdump/tshark] --> D[Packet-Level Data<br/>15 features]
        B[SDN Controller<br/>Flow Statistics] --> E[SDN Flow Data<br/>18 features]
        C[CICFlowMeter<br/>Flow Aggregation] --> F[CICFlow Data<br/>78 features]
    end
    
    subgraph "Network Layer"
        G[PCAP Files<br/>Raw Packets] --> A
        G --> C
        H[OpenFlow Stats<br/>Switch Flows] --> B
    end
    
    subgraph "Output Layer"
        D --> I[packet_features.csv<br/>Individual packets]
        E --> J[flow_features.csv<br/>Switch statistics]
        F --> K[cicflow_features_all.csv<br/>Bidirectional flows]
    end
    
    style D fill:#e3f2fd
    style E fill:#f3e5f5
    style F fill:#fff3e0
    style I fill:#e3f2fd
    style J fill:#f3e5f5
    style K fill:#fff3e0
```

### Data Synchronization Process

```mermaid
sequenceDiagram
    participant AL as attack.log
    participant PC as Packet Capture
    participant FC as Flow Collector
    participant CF as CICFlow
    participant TI as Timeline Integrity
    
    Note over AL,TI: Data Generation Process
    
    AL->>PC: Attack phase boundaries
    AL->>FC: Attack phase boundaries
    AL->>CF: Attack phase boundaries
    
    PC->>TI: Raw packet data
    FC->>TI: Flow statistics
    CF->>TI: Aggregated flows
    
    TI->>TI: Validate timeline consistency
    TI->>TI: Apply conservative labeling
    TI->>TI: Preserve data integrity
    
    Note over TI: 98.9% labeling accuracy<br/>2,072 legitimate unknowns preserved
```

## 🔍 Attack Detection Characteristics

### Traditional vs Adversarial Attack Patterns

```mermaid
flowchart LR
    subgraph "Traditional Attacks"
        A[High Packet Rate<br/>~100 pps] --> B[Obvious Patterns<br/>Predictable timing]
        B --> C[Easy Detection<br/>Rate-based rules]
        C --> D[Short Duration<br/>5 minutes each]
    end
    
    subgraph "Adversarial Attacks"
        E[Low Packet Rate<br/>~0.3 pps] --> F[Evasive Patterns<br/>Burst + jitter]
        F --> G[ML Evasion<br/>Mimicry techniques]
        G --> H[Long Duration<br/>1-2 hours each]
    end
    
    style A fill:#ffebee
    style B fill:#ffebee
    style C fill:#ffebee
    style D fill:#ffebee
    style E fill:#fff3e0
    style F fill:#fff3e0
    style G fill:#fff3e0
    style H fill:#fff3e0
```

## 📈 Dataset Statistics

### Record Distribution Across Formats

```mermaid
pie title Dataset Record Distribution
    "SDN Flow Data" : 2700131
    "Packet-Level Data" : 178473
    "CICFlow Data" : 34246
```

### Attack Type Distribution

```mermaid
xychart-beta
    title "Attack Type Distribution (Packet-Level)"
    x-axis ["normal", "syn_flood", "udp_flood", "icmp_flood", "ad_syn", "ad_udp", "ad_slow", "unknown"]
    y-axis "Records" 0 --> 100000
    bar [96533, 22201, 13692, 22346, 4696, 7330, 9755, 2072]
```

## 🎯 Timeline Integrity Validation

### Conservative Data Preservation

```mermaid
flowchart TD
    A[Raw Dataset] --> B{Existing Labels}
    B -->|Correct| C[Preserve All Existing Labels]
    B -->|Unknown| D[Validate Against Timeline]
    
    D --> E{Within Attack Window?}
    E -->|Yes| F[Validate Packet Characteristics]
    E -->|No| G[Keep as Unknown<br/>Timeline Gap]
    
    F --> H{Matches Attack Pattern?}
    H -->|Yes| I[Reclassify to Attack Type]
    H -->|No| J[Keep as Unknown<br/>Response Packet]
    
    C --> K[Final Dataset<br/>98.9% Labeled]
    I --> K
    G --> K
    J --> K
    
    style C fill:#e8f5e8
    style I fill:#e8f5e8
    style G fill:#fff3e0
    style J fill:#fff3e0
    style K fill:#e3f2fd
```

This comprehensive scenario documentation provides visual diagrams for:
- Network topology and architecture
- Attack timeline and sequence
- Individual attack patterns
- Data collection processes
- Timeline integrity validation
- Dataset statistics and distributions

The diagrams use Mermaid syntax which renders properly in markdown viewers and provides clear visual understanding of the complex attack scenarios and data generation process.