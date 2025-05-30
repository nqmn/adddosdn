# API Reference

Complete REST API reference for the Enhanced Ryu Flow Monitor system.

## 🌐 Base URL and Authentication

### Base URL
- **Primary Controller**: `http://localhost:8080`
- **Client Controller**: `http://localhost:8081`
- **Production**: `https://your-domain.com:8080`

### Authentication
Currently, the API uses basic authentication (optional):
```bash
# With authentication (if enabled)
curl -u username:password http://localhost:8080/api/endpoint

# Without authentication (default)
curl http://localhost:8080/api/endpoint
```

### Response Format
All API responses are in JSON format with CORS headers enabled.

## 📊 Network Monitoring Endpoints

### GET /stats
Get overall network statistics.

**Response**:
```json
{
  "switch_count": 3,
  "flow_count": 15,
  "packet_count": 1250,
  "byte_count": 125000,
  "link_count": 2,
  "uptime": 3600
}
```

**Example**:
```bash
curl http://localhost:8080/stats
```

### GET /switches
Get information about all connected switches.

**Response**:
```json
[
  {
    "id": "0x1",
    "status": "Active",
    "flows": 5,
    "ports": 4,
    "uptime": 1800
  }
]
```

**Example**:
```bash
curl http://localhost:8080/switches
```

### GET /flows
Get flow statistics from all switches.

**Response**:
```json
[
  {
    "switch_id": "0x1",
    "priority": 1,
    "match": "in_port=1,eth_dst=00:00:00:00:00:02",
    "actions": "output:2",
    "packet_count": 100,
    "byte_count": 10000,
    "duration_sec": 300
  }
]
```

**Example**:
```bash
curl http://localhost:8080/flows
```

### GET /topology
Get network topology information.

**Response**:
```json
{
  "switches": [1, 2, 3],
  "links": [
    {
      "src": 1,
      "dst": 2,
      "src_port": 1,
      "dst_port": 2
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:8080/topology
```

### GET /logs
Get recent activity logs.

**Parameters**:
- `limit` (optional): Number of log entries to return (default: 100)

**Response**:
```json
[
  {
    "timestamp": "2024-12-07T10:30:00Z",
    "level": "info",
    "message": "Switch 0x1 connected",
    "component": "controller"
  }
]
```

**Example**:
```bash
curl http://localhost:8080/logs?limit=50
```

### GET /port_stats/{dpid}
Get port statistics for a specific switch.

**Parameters**:
- `dpid`: Switch datapath ID (hex format, e.g., "0x1")

**Response**:
```json
[
  {
    "port_no": 1,
    "rx_packets": 1000,
    "tx_packets": 950,
    "rx_bytes": 100000,
    "tx_bytes": 95000,
    "rx_errors": 0,
    "tx_errors": 0
  }
]
```

**Example**:
```bash
curl http://localhost:8080/port_stats/0x1
```

## 🛡️ DDoS Detection Endpoints

### GET /ddos/alerts
Get DDoS detection alerts.

**Parameters**:
- `limit` (optional): Number of alerts to return (default: 100)
- `since` (optional): Unix timestamp to get alerts since

**Response**:
```json
[
  {
    "timestamp": "2024-12-07T10:35:00Z",
    "type": "ddos_detected",
    "source_ip": "10.0.0.1",
    "target_ip": "10.0.0.3",
    "confidence": 0.85,
    "attack_type": "tcp_syn_flood",
    "mitigation_applied": true
  }
]
```

**Example**:
```bash
curl http://localhost:8080/ddos/alerts
curl http://localhost:8080/ddos/alerts?limit=10&since=1701936000
```

### GET /ddos/stats
Get DDoS detection statistics.

**Response**:
```json
{
  "total_detections": 25,
  "true_positives": 20,
  "false_positives": 5,
  "mitigations_applied": 18,
  "active_mitigations": 3,
  "blocked_flows": 12,
  "controller_id": "root_controller",
  "is_root": true,
  "threat_intel_count": 150
}
```

**Example**:
```bash
curl http://localhost:8080/ddos/stats
```

### GET /ddos/mitigation
Get active mitigation rules.

**Response**:
```json
{
  "10.0.0.1": {
    "rule_id": "block_10.0.0.1",
    "action": "drop",
    "timeout": 60,
    "created": "2024-12-07T10:35:00Z",
    "switch_id": "0x1"
  }
}
```

**Example**:
```bash
curl http://localhost:8080/ddos/mitigation
```

### GET /ddos/threats
Get threat intelligence data.

**Response**:
```json
{
  "known_attackers": [
    {
      "ip": "192.168.1.100",
      "last_seen": "2024-12-07T10:30:00Z",
      "attack_count": 5,
      "severity": "high"
    }
  ],
  "attack_patterns": [
    {
      "pattern": "tcp_syn_flood",
      "frequency": 15,
      "last_detected": "2024-12-07T10:35:00Z"
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:8080/ddos/threats
```

## 🔬 CICFlowMeter Endpoints

### GET /cicflow/features
Get CICFlowMeter extracted features.

**Parameters**:
- `count` (optional): Number of feature sets to return (default: 100)

**Response**:
```json
[
  {
    "flow_duration": 1.5,
    "total_fwd_packets": 10,
    "total_bwd_packets": 8,
    "flow_bytes_per_sec": 6666.67,
    "flow_packets_per_sec": 12.0,
    "flow_iat_mean": 0.15,
    "fwd_packet_length_mean": 64.0,
    "bwd_packet_length_mean": 60.0,
    "label": "BENIGN"
  }
]
```

**Example**:
```bash
curl http://localhost:8080/cicflow/features?count=50
```

## 🤝 Federated Learning Endpoints

### GET /federated/status
Get federated learning status.

**Response**:
```json
{
  "is_root": true,
  "controller_id": "root_controller",
  "root_address": "localhost:9999",
  "client_models": 2,
  "global_model_version": 5,
  "last_sync": 1701936000
}
```

**Example**:
```bash
curl http://localhost:8080/federated/status
```

## 🧠 Machine Learning Endpoints

### POST /ml/upload
Upload a custom ML model.

**Parameters**:
- `model_file`: ML model file (.pkl format)
- `model_type` (optional): Type of model (default: "ddos_detector")
- `replace_existing` (optional): Replace existing model (default: false)

**Request**:
```bash
curl -X POST http://localhost:8080/ml/upload \
  -F "model_file=@custom_model.pkl" \
  -F "model_type=ddos_detector" \
  -F "replace_existing=true"
```

**Response**:
```json
{
  "status": "success",
  "message": "Model uploaded successfully",
  "model_id": "custom_model_20241207",
  "model_type": "ddos_detector"
}
```

### GET /ml/models
Get information about available ML models.

**Response**:
```json
[
  {
    "model_id": "default_isolation_forest",
    "model_type": "ddos_detector",
    "created": "2024-12-07T10:00:00Z",
    "accuracy": 0.92,
    "status": "active"
  }
]
```

**Example**:
```bash
curl http://localhost:8080/ml/models
```

### POST /ml/train
Trigger manual model training.

**Request**:
```bash
curl -X POST http://localhost:8080/ml/train \
  -H "Content-Type: application/json" \
  -d '{"force_retrain": true}'
```

**Response**:
```json
{
  "status": "success",
  "message": "Model training initiated",
  "training_id": "train_20241207_103000"
}
```

## ⚙️ Configuration Endpoints

### GET /config
Get current system configuration.

**Response**:
```json
{
  "controller_id": "root_controller",
  "is_root": true,
  "detection_threshold": 0.7,
  "training_interval": 300,
  "wsapi_port": 8080,
  "ofp_port": 6633
}
```

**Example**:
```bash
curl http://localhost:8080/config
```

### POST /config/detection
Update detection configuration.

**Request**:
```bash
curl -X POST http://localhost:8080/config/detection \
  -H "Content-Type: application/json" \
  -d '{
    "threshold": 0.8,
    "training_interval": 600
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "Detection configuration updated",
  "new_config": {
    "threshold": 0.8,
    "training_interval": 600
  }
}
```

## 📊 Metrics and Health Endpoints

### GET /health
Get system health status.

**Response**:
```json
{
  "status": "healthy",
  "uptime": 3600,
  "memory_usage": "45%",
  "cpu_usage": "12%",
  "disk_usage": "23%",
  "active_connections": 3
}
```

**Example**:
```bash
curl http://localhost:8080/health
```

### GET /metrics
Get detailed system metrics.

**Response**:
```json
{
  "controller": {
    "packets_processed": 10000,
    "flows_installed": 150,
    "processing_latency_ms": 2.5
  },
  "detection": {
    "detections_per_minute": 0.5,
    "false_positive_rate": 0.05,
    "model_accuracy": 0.92
  },
  "system": {
    "memory_mb": 1024,
    "cpu_percent": 15.2,
    "disk_io_mb": 50.3
  }
}
```

**Example**:
```bash
curl http://localhost:8080/metrics
```

## 🚨 Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "error": {
    "code": 400,
    "message": "Invalid parameter: threshold must be between 0 and 1",
    "details": {
      "parameter": "threshold",
      "provided_value": 1.5,
      "valid_range": "0.0 - 1.0"
    }
  }
}
```

## 📝 Rate Limiting

### Default Limits
- **General Endpoints**: 100 requests/minute
- **Upload Endpoints**: 10 requests/minute
- **Training Endpoints**: 5 requests/minute

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701936060
```

---

**Next**: [Configuration Guide](configuration.md)  
**Previous**: [Basic Usage Guide](basic-usage.md)
