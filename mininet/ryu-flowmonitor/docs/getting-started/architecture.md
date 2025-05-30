# System Architecture Overview

This document provides a comprehensive overview of the Enhanced Ryu Flow Monitor system architecture, components, and data flow.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SDN DDoS Detection System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Ryu Server    │◄──►│ Mininet Server  │                    │
│  │  (Root Ctrl)    │    │ (Client Ctrl)   │                    │
│  │ 192.168.1.100   │    │ 192.168.1.101   │                    │
│  │                 │    │                 │                    │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                    │
│  │ │ ML Engine   │ │    │ │ Local ML    │ │                    │
│  │ │ Federated   │ │    │ │ Detection   │ │                    │
│  │ │ Learning    │ │    │ │ CICFlow     │ │                    │
│  │ └─────────────┘ │    │ └─────────────┘ │                    │
│  │                 │    │                 │                    │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │                    │
│  │ │ Web API     │ │    │ │ Web API     │ │                    │
│  │ │ Port 8080   │ │    │ │ Port 8081   │ │                    │
│  │ └─────────────┘ │    │ └─────────────┘ │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                            │
│           ▼                       ▼                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Web Interface  │    │   SDN Network   │                    │
│  │ - DDoS Monitor  │    │ - OpenFlow      │                    │
│  │ - ML Metrics    │    │ - Switches      │                    │
│  │ - Mitigation    │    │ - Traffic       │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. Flow Monitor Controller (`FlowMonitorController`)

**Purpose**: Main SDN controller with enhanced DDoS detection capabilities

**Key Features**:
- OpenFlow 1.3 support
- Real-time packet analysis
- ML-based anomaly detection
- Automated threat mitigation
- Multi-controller coordination

**Location**: `flow_monitor_controller.py`

### 2. DDoS Detection Engine (`DDoSDetector`)

**Purpose**: Machine learning-based DDoS attack detection

**Components**:
- **Isolation Forest**: Unsupervised anomaly detection
- **Random Forest**: Supervised classification backup
- **Feature Extractor**: Network traffic feature extraction
- **Model Manager**: Model training and persistence

**Detection Features**:
- Packet-level analysis
- Flow-level statistics
- Protocol-specific features
- Temporal pattern analysis

### 3. CICFlowMeter Integration (`CICFlowMeterIntegration`)

**Purpose**: Advanced network traffic analysis and feature extraction

**Capabilities**:
- Real-time packet capture
- Flow feature extraction
- Statistical analysis
- Integration with ML models

**Output**: CSV files with 80+ network flow features

### 4. Federated Learning Manager (`FederatedLearningManager`)

**Purpose**: Coordinate ML model training across multiple controllers

**Architecture**:
- **Root Controller**: Aggregates models from clients
- **Client Controllers**: Train local models, share updates
- **Model Synchronization**: Periodic model updates
- **Threat Intelligence**: Shared attack patterns

### 5. Web Interface and API (`FlowMonitorAPI`)

**Purpose**: Real-time monitoring and system management

**Endpoints**:
- Network statistics
- DDoS alerts and metrics
- Topology information
- Model management
- Configuration updates

## 🔄 Data Flow Architecture

### 1. Packet Processing Flow

```
Network Packet → OpenFlow Switch → Controller
                                      ↓
                              Packet Analysis
                                      ↓
                              Feature Extraction
                                      ↓
                              DDoS Detection
                                      ↓
                              Mitigation Decision
                                      ↓
                              Flow Rule Installation
```

### 2. ML Training Flow

```
Traffic Features → Local Model Training → Model Evaluation
                                              ↓
                                      Model Persistence
                                              ↓
                                   Federated Aggregation
                                              ↓
                                    Global Model Update
```

### 3. Detection and Response Flow

```
Real-time Traffic → Feature Extraction → ML Inference
                                              ↓
                                      Anomaly Score
                                              ↓
                                   Threshold Comparison
                                              ↓
                                      Alert Generation
                                              ↓
                                   Automated Mitigation
```

## 🏛️ Component Interactions

### Controller-to-Controller Communication

```python
# Root Controller (Federated Learning Server)
class FederatedLearningManager:
    def aggregate_models(self):
        # Collect models from client controllers
        # Perform federated averaging
        # Distribute updated global model
```

### Switch-to-Controller Communication

```python
# OpenFlow Message Handling
@conditional_set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
    # Extract packet information
    # Perform DDoS analysis
    # Install flow rules
    # Apply mitigation if needed
```

### Web Interface Integration

```python
# REST API Endpoints
class FlowMonitorAPI:
    def ddos_alerts(self):
        # Return real-time DDoS alerts
    
    def network_stats(self):
        # Return network statistics
    
    def mitigation_rules(self):
        # Return active mitigation rules
```

## 🔧 Configuration Architecture

### Controller Configuration

```python
CONTROLLER_CONFIG = {
    'controller_id': 'root_controller',
    'is_root': True,
    'detection_threshold': 0.7,
    'training_interval': 300,
    'federated_port': 9999
}
```

### ML Model Configuration

```python
ML_CONFIG = {
    'isolation_forest': {
        'contamination': 0.1,
        'random_state': 42
    },
    'random_forest': {
        'n_estimators': 100,
        'random_state': 42
    }
}
```

## 🚀 Deployment Architectures

### Single Server Deployment

```
┌─────────────────────────────────────┐
│           Single Server             │
│                                     │
│  ┌─────────────────────────────────┐│
│  │     Ryu Controller              ││
│  │   + DDoS Detection              ││
│  │   + Web Interface               ││
│  │   + ML Engine                   ││
│  └─────────────────────────────────┘│
│                 │                   │
│                 ▼                   │
│  ┌─────────────────────────────────┐│
│  │        Mininet Network          ││
│  │      (Local Simulation)         ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Multi-Server Deployment

```
┌─────────────────┐    ┌─────────────────┐
│   Ryu Server    │    │ Mininet Server  │
│                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │Root         │ │    │ │Client       │ │
│ │Controller   │◄┼────┼►│Controller   │ │
│ │             │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │
│                 │    │        │        │
│ ┌─────────────┐ │    │        ▼        │
│ │Global ML    │ │    │ ┌─────────────┐ │
│ │Model        │ │    │ │SDN Network  │ │
│ │             │ │    │ │Simulation   │ │
│ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘
```

## 📊 Performance Characteristics

### Scalability Metrics

- **Controllers**: Supports 2-10 federated controllers
- **Switches**: Handles 100+ OpenFlow switches
- **Flows**: Processes 10,000+ concurrent flows
- **Detection Latency**: < 100ms for packet-level detection
- **Model Training**: 5-minute intervals for adaptive learning

### Resource Requirements

- **CPU**: 2+ cores recommended
- **Memory**: 4GB+ RAM for ML models
- **Storage**: 10GB+ for traffic captures and logs
- **Network**: Gigabit connectivity for multi-server setup

## 🔒 Security Architecture

### Threat Detection Layers

1. **Packet-Level**: Real-time packet analysis
2. **Flow-Level**: Statistical flow analysis
3. **Network-Level**: Topology-aware detection
4. **Behavioral-Level**: ML-based anomaly detection

### Mitigation Strategies

1. **Immediate Blocking**: High-confidence threats
2. **Rate Limiting**: Suspicious traffic patterns
3. **Traffic Redirection**: Advanced mitigation
4. **Coordinated Response**: Multi-controller coordination

---

**Next**: [Installation Guide](installation.md)  
**Previous**: [Quick Start Guide](quick-start.md)
