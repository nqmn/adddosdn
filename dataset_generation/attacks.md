# SDN Attack Analysis - AdDDoSDN Dataset Framework

## **Attack Configuration Overview**

All attacks originate from **h1 (192.168.10.10)** as the single attack source host.

| Attack Type | Primary Target Plane | Source Host | Victim Host | Source IP | Victim IP | Attack Path |
|-------------|---------------------|-------------|-------------|-----------|-----------|-------------|
| **Traditional Network-Level Attacks** |
| `syn_flood` | **Data Plane** | **h1** | **h6** | 192.168.10.10 | 192.168.30.10 | Cross-subnet → Web server |
| `udp_flood` | **Data Plane** | **h1** | **h6** | 192.168.10.10 | 192.168.30.10 | Cross-subnet → Web server |
| `icmp_flood` | **Control Plane** | **h1** | **h4** | 192.168.10.10 | 192.168.20.12 | Cross-subnet → Regular host |
| **Advanced/Adversarial Attacks** |
| `ad_syn` (TCP State Exhaustion) | **Data Plane** | **h1** | **h6** | 192.168.10.10 | 192.168.30.10 | Cross-subnet → Web server |
| `ad_udp` (Application Layer) | **Application Plane** | **h1** | **h6** | 192.168.10.10 | 192.168.30.10 | Cross-subnet → Web server |
| `ad_slow` (Slow HTTP) | **Application Plane** | **h1** | **h6** | 192.168.10.10 | 192.168.30.10 | Cross-subnet → Web server |

## **Network Topology**

**Subnet Distribution:**
- **Subnet 1 (192.168.10.0/24)**: h1 (attacker host)
- **Subnet 2 (192.168.20.0/24)**: h2, h3, h4, h5 (h4 = ICMP target)
- **Subnet 3 (192.168.30.0/24)**: h6 (web server target)

**Attack Distribution:**
- **→ h6 (Web Server)**: syn_flood, udp_flood, ad_syn, ad_udp, ad_slow (5 attacks)
- **→ h4 (Regular Host)**: icmp_flood (1 attack)

## **Complete Attack Phase Analysis**

### **Traditional Attacks Phase Structure**

#### **SYN Flood (2 Phases)**
| Phase | Duration | Pattern | Characteristics |
|-------|----------|---------|----------------|
| **Phase 1: Stress Burst** | **30%** of total | High-intensity flooding | • No think time<br>• Maximum rate SYN packets<br>• Random source ports<br>• Basic TCP options |
| **Phase 2: Advanced Attack** | **70%** of total | Human-like evasion | • Human timing (0.08-0.15s)<br>• RFC-compliant TCP options<br>• Session patterns<br>• Think time every 50 packets |

#### **UDP Flood (2 Phases)**
| Phase | Duration | Pattern | Characteristics |
|-------|----------|---------|----------------|
| **Phase 1: Stress Burst** | **30%** of total | High-intensity flooding | • No think time<br>• Maximum rate UDP packets<br>• Random DNS queries<br>• Random source ports |
| **Phase 2: Advanced Attack** | **70%** of total | Human-like evasion | • Human timing patterns<br>• Realistic DNS payloads<br>• Service-aware UDP traffic<br>• Session-based patterns |

## **ICMP Flood - Detailed 3 Phase Attack Analysis**

| Phase | Duration | Target | Attack Pattern | Traffic Characteristics | Plane Impact | Purpose |
|-------|----------|--------|----------------|------------------------|--------------|---------|
| **Phase 1: Host Stress Burst** | **15%** of total | **h4 (192.168.20.12)** | High-intensity direct flooding | • No think time<br>• Continuous ICMP Echo<br>• Maximum rate flooding<br>• Single target focus | **Data Plane** | Direct victim resource exhaustion testing |
| **Phase 2: Gateway Stress Burst** | **15%** of total | **All Gateways:<br>• 192.168.10.1<br>• 192.168.20.1<br>• 192.168.30.1** | Round-robin gateway flooding | • Rotates through all 3 gateways<br>• High-intensity ICMP<br>• No timing delays<br>• Forces controller processing | **Control Plane** | Controller stress via gateway echo handling |
| **Phase 3: Human-Like Advanced** | **70%** of total | **h4 (192.168.20.12)**<br>with **IP rotation** | Sophisticated evasion attack | • **RFC 1918 IP rotation** (50 IPs)<br>• **Human-like timing** (0.08-0.15s)<br>• **Circadian rhythms** (time-aware)<br>• **Session patterns** with breaks<br>• **Think time** every 50 packets<br>• **Random payloads** (0-1400 bytes)<br>• **Network delay simulation** | **Data + Control Plane** | ML evasion through realistic human behavior simulation |

## **Detailed Phase Characteristics**

### **Phase 1: Host Stress (Data Plane Impact)**
```python
# Maximum rate flooding - no delays
while time.time() < end_ts:
    pkt = Ether()/IP(dst=target_ip)/ICMP()
    sendp(pkt, iface=iface, verbose=0)
```
- **Impact**: Overwhelms victim host processing capacity
- **Detection**: Easy - obvious flooding pattern

### **Phase 2: Gateway Stress (Control Plane Impact)**  
```python
# Round-robin through all gateways
dst = gateways[i % len(gateways)]
pkt = Ether()/IP(dst=dst)/ICMP()
sendp(pkt, iface=iface, verbose=0)
```
- **Impact**: Forces controller to process each gateway ICMP packet
- **Detection**: Easy - targeting infrastructure IPs

### **Phase 3: Human-Like Advanced (Hybrid Impact)**
```python
# IP rotation every 10-20 packets
if packet_count % random.randint(10, 20) == 0:
    if random.random() < 0.7:  # 70% pool, 30% fresh
        current_src_ip = ip_pool[current_ip_index]
    else:
        current_src_ip = generate_fresh_rfc1918_ip()

# Human timing with think time
if packet_count % 50 == 0:
    think_time = random.uniform(0.5, 2.0)
else:
    interval = random.choice(typing_intervals) * random.uniform(0.8, 1.2)
```
- **Impact**: Sophisticated evasion targeting both planes
- **Detection**: Hard - mimics legitimate user behavior patterns

## **SDN Plane Definitions**

- **Data Plane**: Packet forwarding by switches using flow tables
- **Control Plane**: Controller flow table management and routing decisions  
- **Application Plane**: Services and applications running on network hosts
- **Management Plane**: Network configuration and monitoring (not targeted)

## **Attack Timeline Structure**

### **ICMP Flood Attack Timeline**
```
Total Duration = 100%
├── Stress Phase (30%)
│   ├── Host Stress (15%) → h4 direct flooding
│   └── Gateway Stress (15%) → Gateway flooding
└── Advanced Phase (70%) → Human-like attack with IP rotation
```

## **Key Attack Features**

### **Traditional Attacks Enhancement**
- **SYN Flood**: RFC-compliant TCP options with human-like timing (~25 pps)
- **UDP Flood**: Realistic DNS payloads with ephemeral ports
- **ICMP Flood**: 3-phase attack with gateway stress + human-like patterns

### **Adversarial Attacks**
- **TCP State Exhaustion (ad_syn)**: Traffic mimicry with burst patterns and jitter
- **Application Layer (ad_udp)**: HTTP requests with legitimate session mimicry
- **Slow HTTP (ad_slow)**: Adaptive behavior with stealth techniques

### **Adversarial Attacks Phase Structure**

#### **ad_syn: TCP State Exhaustion (4 Phases)**
| Phase | Duration | Attack Ratio | Intensity | Characteristics |
|-------|----------|--------------|-----------|----------------|
| **Phase 1: Recon** | **25%** of total | 0% attack | 10% intensity | • Pure reconnaissance<br>• Legitimate traffic only<br>• Target assessment |
| **Phase 2: Infiltration** | **25%** of total | 10% attack | 20% intensity | • Mixed legitimate/attack<br>• Slow attack introduction<br>• Evasion testing |
| **Phase 3: Escalation** | **30%** of total | 40% attack | 60% intensity | • Significant attack traffic<br>• TCP state exhaustion<br>• Connection flooding |
| **Phase 4: Peak** | **20%** of total | 70% attack | 100% intensity | • Maximum attack intensity<br>• Full state exhaustion<br>• Resource depletion |

#### **ad_udp: Application Layer Attack (4 Phases)**  
| Phase | Duration | Attack Ratio | Requests/Sec | Characteristics |
|-------|----------|--------------|--------------|----------------|
| **Phase 1: Browsing** | **30%** of total | 0% attack | 0.5 rps | • Normal web browsing<br>• Legitimate HTTP requests<br>• Session establishment |
| **Phase 2: Interaction** | **20%** of total | 10% attack | 1.0 rps | • Light attack mixing<br>• Form submissions<br>• API interactions |
| **Phase 3: Exploitation** | **30%** of total | 40% attack | 2.0 rps | • Resource exhaustion<br>• Large payloads<br>• Range requests |
| **Phase 4: Peak Attack** | **20%** of total | 70% attack | 4.0 rps | • Maximum HTTP load<br>• Application overload<br>• Service disruption |

#### **ad_slow: Slow HTTP Attack (4 Phases)**
| Phase | Duration | Attack Ratio | Connections/Sec | Characteristics |
|-------|----------|--------------|-----------------|----------------|
| **Phase 1: Normal Browsing** | **25%** of total | 0% attack | 0.3 cps | • Standard HTTP connections<br>• Normal response times<br>• Legitimate behavior |
| **Phase 2: Mixed Behavior** | **25%** of total | 20% attack | 0.5 cps | • Slow connections introduced<br>• Mixed timing patterns<br>• Behavioral variation |
| **Phase 3: Slow Escalation** | **30%** of total | 50% attack | 0.8 cps | • Significant slow connections<br>• Resource holding<br>• Connection persistence |
| **Phase 4: Stealth Peak** | **20%** of total | 70% attack | 1.0 cps | • Maximum slow attack<br>• Connection exhaustion<br>• Stealthy resource depletion |

## **Attack Complexity Comparison**

| Attack Type | Phases | Primary Strategy | Sophistication Level |
|-------------|--------|------------------|---------------------|
| **SYN Flood** | 2 | Stress → Human-like | Enhanced Traditional |
| **UDP Flood** | 2 | Stress → Human-like | Enhanced Traditional |
| **ICMP Flood** | 3 | Host Stress → Gateway Stress → Human-like | Multi-target Traditional |
| **ad_syn** | 4 | Recon → Infiltration → Escalation → Peak | Advanced Adversarial |
| **ad_udp** | 4 | Browsing → Interaction → Exploitation → Peak | Application-layer Adversarial |
| **ad_slow** | 4 | Normal → Mixed → Escalation → Stealth | Stealth Adversarial |

This multi-phase approach provides comprehensive attack surface coverage across different sophistication levels: traditional stress testing, infrastructure targeting, and advanced multi-stage adversarial techniques.

## **Updated Host Usage with Protocol Separation**

### **Normal Traffic Protocol Separation**
- **h2 ↔ h5**: ICMP ping traffic only
- **h3 ↔ h5**: TCP and UDP traffic (Telnet, SSH, FTP, HTTP, HTTPS, DNS)

### **Complete Host Roles**

| Host | Normal Traffic Role | Attack Role | IP Address | Subnet |
|------|--------------------|--------------|-----------|---------| 
| **h1** | ❌ Not involved | ✅ **Attacker source** (all attacks) | 192.168.10.10 | Subnet 1 |
| **h2** | ✅ **ICMP traffic source** | ❌ Not involved | 192.168.20.10 | Subnet 2 |
| **h3** | ✅ **TCP/UDP traffic source** | ❌ Not involved | 192.168.20.11 | Subnet 2 |
| **h4** | ❌ Not involved | ✅ **ICMP flood victim** | 192.168.20.12 | Subnet 2 |
| **h5** | ✅ **Normal traffic destination** | ❌ Not involved | 192.168.20.13 | Subnet 2 |
| **h6** | ❌ Not involved | ✅ **Web server victim** (5 attacks) | 192.168.30.10 | Subnet 3 |

### **Protocol Distribution Benefits**
- **Clean Separation**: Normal traffic protocols isolated from attack traffic
- **Full Utilization**: All 6 hosts now have dedicated roles
- **Protocol Diversity**: ICMP, TCP, and UDP properly distributed
- **Analysis Benefits**: Easy to identify protocol-specific patterns and anomalies