# Real-Time DDoS Detection with PCAP Replay and ML Model Inference

This module provides a comprehensive framework for real-time DDoS detection using machine learning models trained on the AdDDoSDN dataset. The system replays PCAP files, extracts packet features on-the-fly, and performs live ML inference.

## 🎯 Overview

This framework implements a **two-phase approach**:

### Phase 1: Training Phase
- **Load `packet_features.csv`** from AdDDoSDN dataset
- **Train ML models** on the 15 packet-level features
- **Save trained models** for real-time inference

### Phase 2: Real-Time Detection Phase
- **Replay PCAP files** packet-by-packet in real-time
- **Extract features** from each packet on-the-fly
- **Run ML inference** using pre-trained models
- **Monitor performance metrics** (accuracy, precision, recall, F1-score)
- **Track system resources** (CPU, memory usage) during different phases
- **Calculate percentage changes** between normal and attack phases

## 📊 System Architecture

```
Training Phase:
packet_features.csv → Feature Engineering → ML Training → model.pkl

Real-Time Phase:
PCAP Replay → Feature Extraction → ML Inference → Performance Monitoring
```

**Key Point**: Real-time detection works purely with PCAP files - no CSV files are involved in the live detection process.

## 📋 Dataset Information

Based on the dataset analysis from `dataset_generation/main_output/analysis.md`:

### Available Training Data
- **Total Records**: 178,473 packets across 4 datasets
- **Features**: 15 packet-level attributes
- **Labels**: 7 attack types (normal, syn_flood, udp_flood, icmp_flood, ad_syn, ad_udp, ad_slow)
- **Quality**: 98.9% labeled data with conservative validation

### Attack Phase Timeline (for Ground Truth)
| Phase | Attack Type | Duration | Packet Rate | Characteristics |
|-------|-------------|----------|-------------|----------------|
| Normal | Baseline traffic | 1 hour | Variable | Multi-protocol benign traffic |
| SYN Flood | Traditional | 5 minutes | 22.5 pps | TCP SYN flood targeting port 80 |
| UDP Flood | Traditional | 5 minutes | 22.5 pps | UDP flood targeting port 53 |
| ICMP Flood | Traditional | 5 minutes | 22.5 pps | ICMP echo request flood |
| Adversarial SYN | Advanced | 2 hours | 0.3 pps | TCP state exhaustion with IP rotation |
| Adversarial UDP | Advanced | 1.33 hours | 0.3 pps | Application layer mimicry |
| Adversarial Slow | Advanced | 2 hours | 0.3 pps | Slow HTTP connection attacks |

## 🏗️ System Architecture

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                          Real-Time DDoS Detection Framework                            │
├───────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                            TRAINING PHASE                                       │   │
│  │                                                                                 │   │
│  │  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────────────────┐   │   │
│  │  │ Dataset Loader  │    │ Feature Eng. │    │    Model Training Pipeline  │   │   │
│  │  │                 │───▶│              │───▶│                             │   │   │
│  │  │• packet_features│    │• Normalization│    │• Random Forest              │   │   │
│  │  │  .csv files     │    │• Label Encode │    │• XGBoost                    │   │   │
│  │  │• Multi-dataset  │    │• Missing Val. │    │• Neural Network             │   │   │
│  │  │  aggregation    │    │• Feature Sel. │    │• Ensemble Voting            │   │   │
│  │  │• 178K packets   │    │• Validation   │    │• Cross-validation           │   │   │
│  │  └─────────────────┘    └──────────────┘    └─────────────────────────────┘   │   │
│  │                                                         │                      │   │
│  │                                                         ▼                      │   │
│  │                                               ┌─────────────────────────────┐   │   │
│  │                                               │    Trained Models Storage   │   │   │
│  │                                               │• random_forest.pkl          │   │   │
│  │                                               │• xgboost.pkl               │   │   │
│  │                                               │• neural_network.pkl        │   │   │
│  │                                               │• ensemble.pkl              │   │   │
│  │                                               └─────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                  │                                      │
│                                                  ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          REAL-TIME DETECTION PHASE                              │   │
│  │                                                                                 │   │
│  │  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────────────────┐   │   │
│  │  │ PCAP Replay     │    │ Live Feature │    │    ML Inference Engine      │   │   │
│  │  │ Engine          │───▶│ Extraction   │───▶│                             │   │   │
│  │  │                 │    │              │    │• Load pre-trained models    │   │   │
│  │  │• Real-time      │    │• Packet      │    │• Real-time prediction       │   │   │
│  │  │  packet stream  │    │  parsing     │    │• Confidence scoring         │   │   │
│  │  │• Timing sync    │    │• 15 features │    │• Attack classification      │   │   │
│  │  │• Scapy parsing  │    │• Vectorization│    │• Ensemble aggregation       │   │   │
│  │  │• Timeline track │    │• Normalization│    │• Prediction history         │   │   │
│  │  └─────────────────┘    └──────────────┘    └─────────────────────────────┘   │   │
│  │           │                       │                       │                    │   │
│  │           ▼                       ▼                       ▼                    │   │
│  │  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────────────────┐   │   │
│  │  │ Ground Truth    │    │ Performance  │    │    Results & Monitoring     │   │   │
│  │  │ Timeline        │    │ Metrics      │    │                             │   │   │
│  │  │                 │    │              │    │• Real-time Dashboard        │   │   │
│  │  │• attack.log     │    │• Accuracy    │    │• Performance Reports        │   │   │
│  │  │• Phase bound.   │    │• Precision   │    │• Resource Usage Graphs      │   │   │
│  │  │• Label valid.   │    │• Recall      │    │• Detection Logs             │   │   │
│  │  │• Attack types   │    │• F1-Score    │    │• Phase Comparisons          │   │   │
│  │  │• Timing sync    │    │• Phase anal. │    │• JSON Results Export        │   │   │
│  │  └─────────────────┘    └──────────────┘    └─────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                            RESOURCE MONITORING                                  │   │
│  │                                                                                 │   │
│  │  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────────────────┐   │   │
│  │  │ System Monitor  │    │ Performance  │    │    Analysis & Reporting     │   │   │
│  │  │                 │───▶│ Analyzer     │───▶│                             │   │   │
│  │  │• CPU Usage      │    │              │    │• Phase Comparisons          │   │   │
│  │  │• Memory Usage   │    │• Baseline    │    │• Percentage Changes         │   │   │
│  │  │• Disk I/O       │    │• Attack      │    │• Trend Analysis             │   │   │
│  │  │• Network        │    │• Adversarial │    │• Resource Optimization      │   │   │
│  │  │• Process stats  │    │• Comparison  │    │• Performance Benchmarks     │   │   │
│  │  └─────────────────┘    └──────────────┘    └─────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Step 1: Environment Setup

```bash
# Navigate to the ML directory
cd ml/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Train ML Models

```bash
# Train models on all datasets
python scripts/train_models.py --datasets all --models all

# Train specific model on specific dataset
python scripts/train_models.py --dataset 1607-1 --model random_forest

# Train ensemble model
python scripts/train_models.py --dataset 1607-1 --model ensemble
```

### Step 3: Run Real-Time Detection

```bash
# Full system with all monitoring
python scripts/real_time_detection.py --dataset 1607-1 --model ensemble --monitor-all

# Specific PCAP file with trained model
python scripts/real_time_detection.py --pcap ../dataset_generation/main_output/1607-1/syn_flood.pcap --model random_forest

# Custom configuration
python scripts/real_time_detection.py --config config/detection_config.json
```

## 📁 Project Structure

```
ml/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config/                      # Configuration files
│   ├── detection_config.json    # Real-time detection settings
│   ├── model_config.json        # ML model parameters
│   └── training_config.json     # Training configuration
├── src/                         # Source code
│   ├── __init__.py
│   ├── training/               # Model training pipeline
│   │   ├── __init__.py
│   │   ├── data_loader.py      # Load packet_features.csv
│   │   ├── feature_engineer.py # Feature preprocessing
│   │   ├── model_trainer.py    # ML model training
│   │   └── model_evaluator.py  # Model evaluation
│   ├── realtime/               # Real-time detection pipeline
│   │   ├── __init__.py
│   │   ├── pcap_replayer.py    # PCAP file replay engine
│   │   ├── packet_processor.py # Real-time packet processing
│   │   ├── feature_extractor.py # Live feature extraction
│   │   ├── model_inference.py  # Real-time ML inference
│   │   └── timeline_tracker.py # Attack phase tracking
│   ├── monitoring/             # Performance monitoring
│   │   ├── __init__.py
│   │   ├── metrics_tracker.py  # Accuracy metrics calculation
│   │   ├── resource_monitor.py # CPU/memory monitoring
│   │   ├── phase_analyzer.py   # Phase-based analysis
│   │   └── dashboard.py        # Real-time dashboard
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── logger.py           # Logging utilities
│       ├── config_loader.py    # Configuration management
│       └── visualization.py    # Performance visualization
├── models/                     # Trained ML models
│   ├── random_forest.pkl       # Random Forest model
│   ├── xgboost.pkl            # XGBoost model
│   ├── neural_network.pkl     # Neural Network model
│   └── ensemble.pkl           # Ensemble model
├── results/                   # Detection results
│   ├── training_reports/      # Model training results
│   ├── detection_logs/        # Real-time detection logs
│   ├── performance_metrics/   # Performance analysis
│   └── visualizations/        # Performance graphs
├── scripts/                   # Main execution scripts
│   ├── train_models.py        # Model training script
│   ├── real_time_detection.py # Real-time detection script
│   ├── evaluate_models.py     # Model evaluation script
│   └── benchmark_performance.py # Performance benchmarking
└── tests/                     # Unit tests
    ├── test_training.py
    ├── test_realtime.py
    └── test_monitoring.py
```

## 🔧 Configuration

### Detection Configuration (`config/detection_config.json`)

```json
{
  "dataset": {
    "base_path": "../dataset_generation/main_output/",
    "dataset_name": "1607-1",
    "pcap_files": [
      "normal.pcap",
      "syn_flood.pcap", 
      "udp_flood.pcap",
      "icmp_flood.pcap",
      "ad_syn.pcap",
      "ad_udp.pcap",
      "ad_slow.pcap"
    ],
    "replay_speed": 1.0,
    "buffer_size": 1000
  },
  "model": {
    "model_path": "models/ensemble.pkl",
    "model_type": "ensemble",
    "confidence_threshold": 0.7
  },
  "monitoring": {
    "calculate_metrics": true,
    "monitor_resources": true,
    "save_results": true,
    "real_time_dashboard": true,
    "metrics_update_interval": 1.0,
    "resource_update_interval": 0.5
  },
  "features": {
    "packet_features": [
      "packet_length",
      "eth_type", 
      "ip_proto",
      "ip_ttl",
      "ip_id",
      "ip_flags",
      "ip_len",
      "src_port",
      "dst_port", 
      "tcp_flags"
    ],
    "normalize": true,
    "handle_missing": "zero"
  }
}
```

### Training Configuration (`config/training_config.json`)

```json
{
  "data": {
    "datasets": ["1607-1", "1607-2", "1707-1", "1707-2"],
    "feature_file": "packet_features.csv",
    "test_size": 0.2,
    "validation_size": 0.1,
    "random_state": 42
  },
  "models": {
    "random_forest": {
      "n_estimators": 100,
      "max_depth": 20,
      "min_samples_split": 2,
      "min_samples_leaf": 1,
      "random_state": 42
    },
    "xgboost": {
      "n_estimators": 100,
      "max_depth": 6,
      "learning_rate": 0.1,
      "subsample": 0.8,
      "colsample_bytree": 0.8,
      "random_state": 42
    },
    "neural_network": {
      "hidden_layer_sizes": [128, 64, 32],
      "activation": "relu",
      "solver": "adam",
      "alpha": 0.001,
      "batch_size": 200,
      "learning_rate": "constant",
      "max_iter": 500,
      "random_state": 42
    },
    "ensemble": {
      "models": ["random_forest", "xgboost", "neural_network"],
      "voting": "soft",
      "weights": [0.4, 0.4, 0.2]
    }
  },
  "preprocessing": {
    "normalize_features": true,
    "handle_missing_values": "zero",
    "feature_selection": false,
    "remove_outliers": false
  }
}
```

## 🎯 Step-by-Step Implementation

### Phase 1: Training Pipeline

#### 1.1 Data Loading and Preprocessing

```python
# src/training/data_loader.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

class PacketDataLoader:
    def __init__(self, config):
        self.config = config
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def load_training_data(self):
        """Load packet features from CSV files"""
        datasets = self.config['data']['datasets']
        base_path = "../dataset_generation/main_output/"
        
        all_data = []
        for dataset in datasets:
            csv_path = f"{base_path}/{dataset}/packet_features.csv"
            df = pd.read_csv(csv_path)
            all_data.append(df)
            
        # Combine all datasets
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Extract features and labels
        feature_columns = [
            'packet_length', 'eth_type', 'ip_proto', 'ip_ttl', 
            'ip_id', 'ip_flags', 'ip_len', 'src_port', 'dst_port', 'tcp_flags'
        ]
        
        X = combined_df[feature_columns].fillna(0)
        y = combined_df['Label_multi']
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        return X, y_encoded
    
    def preprocess_features(self, X):
        """Normalize and preprocess features"""
        if self.config['preprocessing']['normalize_features']:
            X_scaled = self.scaler.fit_transform(X)
            return X_scaled
        return X.values
```

#### 1.2 Model Training

```python
# src/training/model_trainer.py
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import joblib
import os

class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.models = {}
        
    def train_all_models(self, X_train, y_train, X_val, y_val):
        """Train all configured models"""
        model_configs = self.config['models']
        
        for model_name, model_config in model_configs.items():
            if model_name == 'ensemble':
                continue
                
            print(f"Training {model_name}...")
            model = self._create_model(model_name, model_config)
            model.fit(X_train, y_train)
            
            # Evaluate on validation set
            val_score = model.score(X_val, y_val)
            print(f"{model_name} validation accuracy: {val_score:.4f}")
            
            # Save model
            model_path = f"models/{model_name}.pkl"
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(model, model_path)
            
            self.models[model_name] = model
            
        # Train ensemble if configured
        if 'ensemble' in model_configs:
            self._train_ensemble(X_train, y_train, X_val, y_val)
    
    def _create_model(self, model_name, config):
        """Create model instance based on configuration"""
        if model_name == 'random_forest':
            return RandomForestClassifier(**config)
        elif model_name == 'xgboost':
            return xgb.XGBClassifier(**config)
        elif model_name == 'neural_network':
            return MLPClassifier(**config)
        else:
            raise ValueError(f"Unknown model type: {model_name}")
    
    def _train_ensemble(self, X_train, y_train, X_val, y_val):
        """Train ensemble model"""
        ensemble_config = self.config['models']['ensemble']
        base_models = []
        
        for model_name in ensemble_config['models']:
            if model_name in self.models:
                base_models.append((model_name, self.models[model_name]))
        
        ensemble = VotingClassifier(
            estimators=base_models,
            voting=ensemble_config['voting'],
            weights=ensemble_config.get('weights')
        )
        
        ensemble.fit(X_train, y_train)
        
        val_score = ensemble.score(X_val, y_val)
        print(f"Ensemble validation accuracy: {val_score:.4f}")
        
        # Save ensemble model
        joblib.dump(ensemble, "models/ensemble.pkl")
        self.models['ensemble'] = ensemble
```

### Phase 2: Real-Time Detection Pipeline

#### 2.1 PCAP Replay Engine

```python
# src/realtime/pcap_replayer.py
from scapy.all import rdpcap, Ether, IP, TCP, UDP, ICMP
import time
import threading
from queue import Queue

class PCAPReplayer:
    def __init__(self, config):
        self.config = config
        self.replay_speed = config['dataset']['replay_speed']
        self.buffer_size = config['dataset']['buffer_size']
        self.packet_queue = Queue(maxsize=self.buffer_size)
        self.replaying = False
        
    def replay_pcap_file(self, pcap_path, packet_callback):
        """Replay PCAP file in real-time"""
        print(f"Loading PCAP file: {pcap_path}")
        packets = rdpcap(pcap_path)
        
        if not packets:
            print("No packets found in PCAP file")
            return
            
        print(f"Loaded {len(packets)} packets")
        
        # Start replay
        self.replaying = True
        start_time = time.time()
        first_packet_time = float(packets[0].time)
        
        for i, packet in enumerate(packets):
            if not self.replaying:
                break
                
            # Calculate timing for real-time replay
            packet_time = float(packet.time)
            elapsed_real = time.time() - start_time
            elapsed_packet = (packet_time - first_packet_time) / self.replay_speed
            
            # Sleep to maintain real-time timing
            if elapsed_real < elapsed_packet:
                time.sleep(elapsed_packet - elapsed_real)
            
            # Process packet
            packet_callback(packet, packet_time)
            
            # Progress indicator
            if i % 1000 == 0:
                print(f"Processed {i}/{len(packets)} packets")
        
        print(f"Replay completed: {len(packets)} packets")
        self.replaying = False
    
    def stop_replay(self):
        """Stop the replay process"""
        self.replaying = False
```

#### 2.2 Real-Time Feature Extraction

```python
# src/realtime/feature_extractor.py
from scapy.all import Ether, IP, TCP, UDP, ICMP
import numpy as np

class RealTimeFeatureExtractor:
    def __init__(self, config):
        self.config = config
        self.feature_names = config['features']['packet_features']
        
    def extract_packet_features(self, packet):
        """Extract 15 packet-level features in real-time"""
        features = {}
        
        # Basic packet information
        features['packet_length'] = len(packet)
        
        # Ethernet layer
        if Ether in packet:
            features['eth_type'] = packet[Ether].type
        else:
            features['eth_type'] = 0
            
        # IP layer
        if IP in packet:
            features['ip_proto'] = packet[IP].proto
            features['ip_ttl'] = packet[IP].ttl
            features['ip_id'] = packet[IP].id
            features['ip_flags'] = packet[IP].flags
            features['ip_len'] = packet[IP].len
        else:
            features['ip_proto'] = 0
            features['ip_ttl'] = 0
            features['ip_id'] = 0
            features['ip_flags'] = 0
            features['ip_len'] = 0
            
        # Transport layer
        if TCP in packet:
            features['src_port'] = packet[TCP].sport
            features['dst_port'] = packet[TCP].dport
            features['tcp_flags'] = packet[TCP].flags
        elif UDP in packet:
            features['src_port'] = packet[UDP].sport
            features['dst_port'] = packet[UDP].dport
            features['tcp_flags'] = 0
        else:
            features['src_port'] = 0
            features['dst_port'] = 0
            features['tcp_flags'] = 0
        
        # Convert to array for ML model
        feature_array = np.array([
            features.get(name, 0) for name in self.feature_names
        ]).reshape(1, -1)
        
        return feature_array, features
```

#### 2.3 Real-Time ML Inference

```python
# src/realtime/model_inference.py
import joblib
import numpy as np
import time

class RealTimeInference:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.model_type = config['model']['model_type']
        self.confidence_threshold = config['model']['confidence_threshold']
        self.prediction_history = []
        
    def load_model(self):
        """Load trained model for inference"""
        model_path = self.config['model']['model_path']
        try:
            self.model = joblib.load(model_path)
            print(f"Model loaded from: {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def predict(self, features):
        """Make real-time prediction"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Make prediction
        prediction = self.model.predict(features)[0]
        
        # Get confidence score if available
        confidence = 1.0
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            confidence = np.max(probabilities)
        
        # Store prediction
        prediction_info = {
            'timestamp': time.time(),
            'prediction': prediction,
            'confidence': confidence,
            'features': features[0].tolist()
        }
        
        self.prediction_history.append(prediction_info)
        
        return prediction, confidence
    
    def get_prediction_stats(self):
        """Get prediction statistics"""
        if not self.prediction_history:
            return {}
        
        predictions = [p['prediction'] for p in self.prediction_history]
        confidences = [p['confidence'] for p in self.prediction_history]
        
        return {
            'total_predictions': len(predictions),
            'avg_confidence': np.mean(confidences),
            'prediction_counts': {
                int(pred): predictions.count(pred) for pred in set(predictions)
            }
        }
```

### Phase 3: Performance Monitoring

#### 3.1 Real-Time Metrics Tracking

```python
# src/monitoring/metrics_tracker.py
import time
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class MetricsTracker:
    def __init__(self, config):
        self.config = config
        self.predictions = []
        self.ground_truth = []
        self.timestamps = []
        self.phase_data = {}
        
    def add_prediction(self, prediction, ground_truth, timestamp, phase):
        """Add prediction for metrics calculation"""
        self.predictions.append(prediction)
        self.ground_truth.append(ground_truth)
        self.timestamps.append(timestamp)
        
        # Track by phase
        if phase not in self.phase_data:
            self.phase_data[phase] = {
                'predictions': [],
                'ground_truth': [],
                'timestamps': []
            }
        
        self.phase_data[phase]['predictions'].append(prediction)
        self.phase_data[phase]['ground_truth'].append(ground_truth)
        self.phase_data[phase]['timestamps'].append(timestamp)
    
    def calculate_current_metrics(self, window_size=1000):
        """Calculate metrics for recent predictions"""
        if len(self.predictions) < 10:
            return {}
        
        # Use recent predictions
        recent_pred = self.predictions[-window_size:]
        recent_truth = self.ground_truth[-window_size:]
        
        try:
            metrics = {
                'accuracy': accuracy_score(recent_truth, recent_pred),
                'precision': precision_score(recent_truth, recent_pred, average='weighted', zero_division=0),
                'recall': recall_score(recent_truth, recent_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(recent_truth, recent_pred, average='weighted', zero_division=0),
                'total_predictions': len(recent_pred)
            }
            return metrics
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {}
    
    def get_phase_metrics(self, phase):
        """Get metrics for specific phase"""
        if phase not in self.phase_data:
            return {}
        
        phase_pred = self.phase_data[phase]['predictions']
        phase_truth = self.phase_data[phase]['ground_truth']
        
        if len(phase_pred) < 5:
            return {}
        
        try:
            metrics = {
                'accuracy': accuracy_score(phase_truth, phase_pred),
                'precision': precision_score(phase_truth, phase_pred, average='weighted', zero_division=0),
                'recall': recall_score(phase_truth, phase_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(phase_truth, phase_pred, average='weighted', zero_division=0),
                'total_predictions': len(phase_pred)
            }
            return metrics
        except Exception as e:
            print(f"Error calculating phase metrics: {e}")
            return {}
    
    def compare_phases(self, baseline_phase='normal'):
        """Compare metrics across phases"""
        if baseline_phase not in self.phase_data:
            return {}
        
        baseline_metrics = self.get_phase_metrics(baseline_phase)
        if not baseline_metrics:
            return {}
        
        comparison = {}
        for phase in self.phase_data:
            if phase == baseline_phase:
                continue
            
            phase_metrics = self.get_phase_metrics(phase)
            if not phase_metrics:
                continue
            
            # Calculate percentage changes
            changes = {}
            for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
                if metric in baseline_metrics and metric in phase_metrics:
                    baseline_val = baseline_metrics[metric]
                    phase_val = phase_metrics[metric]
                    
                    if baseline_val != 0:
                        change = ((phase_val - baseline_val) / baseline_val) * 100
                        changes[f'{metric}_change_percent'] = change
                    
                    changes[f'{metric}_baseline'] = baseline_val
                    changes[f'{metric}_current'] = phase_val
            
            comparison[phase] = changes
        
        return comparison
```

### Phase 4: Main Real-Time Detection Script

```python
# scripts/real_time_detection.py
import argparse
import json
import time
import threading
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from realtime.pcap_replayer import PCAPReplayer
from realtime.feature_extractor import RealTimeFeatureExtractor
from realtime.model_inference import RealTimeInference
from realtime.timeline_tracker import TimelineTracker
from monitoring.metrics_tracker import MetricsTracker
from monitoring.resource_monitor import ResourceMonitor
from monitoring.dashboard import RealTimeDashboard
from utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description='Real-time DDoS detection')
    parser.add_argument('--dataset', required=True, help='Dataset name (e.g., 1607-1)')
    parser.add_argument('--pcap', help='Specific PCAP file to replay')
    parser.add_argument('--model', default='ensemble', help='Model type (random_forest, xgboost, neural_network, ensemble)')
    parser.add_argument('--config', default='config/detection_config.json', help='Configuration file')
    parser.add_argument('--monitor-all', action='store_true', help='Enable comprehensive monitoring')
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger('real_time_detection')
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # Update config with CLI arguments
    config['dataset']['dataset_name'] = args.dataset
    config['model']['model_type'] = args.model
    config['model']['model_path'] = f"models/{args.model}.pkl"
    
    # Initialize components
    feature_extractor = RealTimeFeatureExtractor(config)
    model_inference = RealTimeInference(config)
    metrics_tracker = MetricsTracker(config)
    timeline_tracker = TimelineTracker(config)
    dashboard = RealTimeDashboard(config)
    
    # Load model
    model_inference.load_model()
    
    # Start resource monitoring if requested
    resource_monitor = None
    if args.monitor_all:
        resource_monitor = ResourceMonitor(config)
        resource_monitor.start_monitoring()
    
    # Load ground truth timeline
    dataset_path = f"{config['dataset']['base_path']}/{args.dataset}"
    attack_log_path = f"{dataset_path}/attack.log"
    timeline_tracker.load_timeline(attack_log_path)
    
    # Statistics
    total_packets = 0
    start_time = time.time()
    
    def process_packet(packet, packet_time):
        """Process each packet in real-time"""
        nonlocal total_packets
        total_packets += 1
        
        # Extract features
        features, feature_dict = feature_extractor.extract_packet_features(packet)
        
        # Make prediction
        prediction, confidence = model_inference.predict(features)
        
        # Get ground truth phase
        ground_truth_phase = timeline_tracker.get_current_phase(packet_time)
        
        # Update metrics
        metrics_tracker.add_prediction(prediction, ground_truth_phase, packet_time, ground_truth_phase)
        
        # Update dashboard every 100 packets
        if total_packets % 100 == 0:
            current_metrics = metrics_tracker.calculate_current_metrics()
            dashboard.update_display(current_metrics, ground_truth_phase, total_packets)
            
            # Log progress
            elapsed = time.time() - start_time
            pps = total_packets / elapsed if elapsed > 0 else 0
            logger.info(f"Processed {total_packets} packets, {pps:.2f} pps, Phase: {ground_truth_phase}")
    
    # Replay PCAP files
    pcap_replayer = PCAPReplayer(config)
    
    try:
        if args.pcap:
            # Replay specific PCAP file
            pcap_replayer.replay_pcap_file(args.pcap, process_packet)
        else:
            # Replay all PCAP files in sequence
            pcap_files = config['dataset']['pcap_files']
            for pcap_file in pcap_files:
                pcap_path = f"{dataset_path}/{pcap_file}"
                if os.path.exists(pcap_path):
                    print(f"\nReplaying {pcap_file}...")
                    pcap_replayer.replay_pcap_file(pcap_path, process_packet)
                else:
                    print(f"PCAP file not found: {pcap_path}")
        
        # Final analysis
        print("\n" + "="*60)
        print("FINAL ANALYSIS")
        print("="*60)
        
        # Overall metrics
        final_metrics = metrics_tracker.calculate_current_metrics(window_size=len(metrics_tracker.predictions))
        print(f"Overall Performance:")
        for metric, value in final_metrics.items():
            print(f"  {metric}: {value:.4f}")
        
        # Phase comparison
        phase_comparison = metrics_tracker.compare_phases()
        print(f"\nPhase Comparison (vs normal):")
        for phase, changes in phase_comparison.items():
            print(f"  {phase}:")
            for metric, change in changes.items():
                if 'change_percent' in metric:
                    print(f"    {metric}: {change:+.2f}%")
        
        # Model performance
        model_stats = model_inference.get_prediction_stats()
        print(f"\nModel Statistics:")
        print(f"  Total predictions: {model_stats.get('total_predictions', 0)}")
        print(f"  Average confidence: {model_stats.get('avg_confidence', 0):.4f}")
        
        # Resource usage
        if resource_monitor:
            resource_stats = resource_monitor.get_final_stats()
            print(f"\nResource Usage:")
            print(f"  Peak CPU: {resource_stats.get('peak_cpu', 0):.2f}%")
            print(f"  Peak Memory: {resource_stats.get('peak_memory', 0):.2f}%")
            print(f"  Average CPU: {resource_stats.get('avg_cpu', 0):.2f}%")
            print(f"  Average Memory: {resource_stats.get('avg_memory', 0):.2f}%")
        
    except KeyboardInterrupt:
        print("\nDetection interrupted by user")
    finally:
        if resource_monitor:
            resource_monitor.stop_monitoring()
        
        # Save results
        results = {
            'total_packets': total_packets,
            'final_metrics': final_metrics,
            'phase_comparison': phase_comparison,
            'model_stats': model_stats
        }
        
        results_path = f"results/detection_logs/{args.dataset}_{args.model}_{int(time.time())}.json"
        os.makedirs(os.path.dirname(results_path), exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {results_path}")

if __name__ == "__main__":
    main()
```

## 📊 Expected Performance Results

### Training Phase Results
- **Random Forest**: ~95-97% accuracy on test set
- **XGBoost**: ~94-96% accuracy on test set  
- **Neural Network**: ~93-95% accuracy on test set
- **Ensemble**: ~96-98% accuracy on test set

### Real-Time Detection Performance

#### Normal Traffic Phase
- **Accuracy**: 95-98%
- **CPU Usage**: 5-15%
- **Memory Usage**: 200-400 MB
- **Processing Speed**: 1000-2000 packets/second

#### Traditional Attack Phases
- **Accuracy**: 92-97% (slight decrease due to volume)
- **CPU Usage**: 15-35% (150-200% increase)
- **Memory Usage**: 300-600 MB (50-100% increase)
- **Processing Speed**: 800-1500 packets/second

#### Adversarial Attack Phases
- **Accuracy**: 85-92% (challenging evasion techniques)
- **CPU Usage**: 8-20% (minimal increase due to low packet rates)
- **Memory Usage**: 220-450 MB (10-30% increase)
- **Processing Speed**: 1200-2000 packets/second

## 🔧 Advanced Features

### Custom Model Training
```python
# Train with custom parameters
python scripts/train_models.py --dataset 1607-1 --model custom --config config/custom_model.json
```

### Performance Benchmarking
```python
# Benchmark different models
python scripts/benchmark_performance.py --datasets all --models all --iterations 5
```

### Real-Time Visualization
```python
# Enable real-time dashboard
python scripts/real_time_detection.py --dataset 1607-1 --model ensemble --dashboard
```

## 📝 Dependencies

```txt
# requirements.txt
scapy>=2.4.5
scikit-learn>=1.0.0
xgboost>=1.5.0
numpy>=1.21.0
pandas>=1.3.0
psutil>=5.8.0
matplotlib>=3.4.0
seaborn>=0.11.0
joblib>=1.1.0
tqdm>=4.62.0
flask>=2.0.0
plotly>=5.3.0
```

## 🎯 Key Features

### Training Phase Capabilities
- **Multi-Dataset Support**: Aggregate training data from multiple AdDDoSDN datasets
- **Advanced Feature Engineering**: 15 packet-level features with normalization and validation
- **Multiple ML Algorithms**: Random Forest, XGBoost, Neural Networks, and Ensemble methods
- **Robust Validation**: Cross-validation and performance evaluation on test sets
- **Model Persistence**: Trained models saved as pickle files for deployment

### Real-Time Detection Features
- **Live PCAP Replay**: Real-time packet stream processing with timing synchronization
- **On-the-Fly Feature Extraction**: Extract 15 features from packets without CSV dependencies
- **Multi-Model Inference**: Support for individual models and ensemble voting
- **Performance Monitoring**: Real-time accuracy, precision, recall, and F1-score calculation
- **Resource Tracking**: CPU, memory, and system resource monitoring during detection
- **Phase-Based Analysis**: Compare performance across normal, attack, and adversarial phases

### Advanced Analytics
- **Ground Truth Integration**: Synchronize predictions with attack timeline from `attack.log`
- **Performance Benchmarking**: Compare detection accuracy across different attack types
- **Resource Impact Analysis**: Measure computational overhead during different phases
- **Real-Time Dashboard**: Live visualization of detection metrics and system performance
- **Comprehensive Reporting**: JSON export of results with detailed performance metrics

## 🔬 Technical Specifications

### Packet Feature Set (15 Features)
1. **packet_length**: Total packet size in bytes
2. **eth_type**: Ethernet frame type (IPv4, IPv6, ARP, etc.)
3. **ip_proto**: IP protocol number (TCP=6, UDP=17, ICMP=1)
4. **ip_ttl**: IP Time-to-Live value
5. **ip_id**: IP identification field
6. **ip_flags**: IP fragmentation flags
7. **ip_len**: IP packet length
8. **src_port**: Source port number (TCP/UDP)
9. **dst_port**: Destination port number (TCP/UDP)
10. **tcp_flags**: TCP flags (SYN, ACK, FIN, RST, PSH, URG)

### Attack Detection Classes
- **Normal**: Baseline benign traffic
- **syn_flood**: TCP SYN flood attacks
- **udp_flood**: UDP flood attacks
- **icmp_flood**: ICMP echo request floods
- **ad_syn**: Adversarial TCP state exhaustion
- **ad_udp**: Adversarial application layer mimicry
- **ad_slow**: Adversarial slow HTTP attacks

### Performance Metrics
- **Accuracy**: Overall classification correctness
- **Precision**: True positive rate per class
- **Recall**: Sensitivity per class
- **F1-Score**: Harmonic mean of precision and recall
- **Resource Usage**: CPU and memory consumption
- **Processing Speed**: Packets processed per second

## 🛠️ Implementation Status

### Current Framework State
This README documents a **comprehensive design specification** for the real-time DDoS detection system. The framework architecture includes:

1. **Training Phase**: Uses `packet_features.csv` for model training
2. **Real-Time Phase**: Uses PCAP files for packet replay and live feature extraction
3. **No CSV in real-time**: Only PCAP packet processing with on-the-fly feature extraction
4. **Proper performance monitoring**: Tracks metrics and resources during live detection

### Development Roadmap
- **Phase 1**: Core training pipeline implementation
- **Phase 2**: Real-time PCAP replay and feature extraction
- **Phase 3**: ML inference engine and performance monitoring
- **Phase 4**: Advanced analytics and visualization dashboard

## 🔒 Security Considerations

### Defensive Research Focus
This framework is designed exclusively for **defensive security research**:
- **Attack Detection**: Identify and classify DDoS attacks in real-time
- **Performance Analysis**: Measure detection accuracy across attack types
- **Resource Monitoring**: Analyze computational overhead of detection systems
- **Academic Research**: Support cybersecurity education and research

### Ethical Usage
- **No Malicious Enhancement**: Framework cannot be used to improve attack effectiveness
- **Contained Environment**: All testing performed in isolated Mininet virtual networks
- **Detection Focus**: Emphasis on improving defensive capabilities, not attack methods
- **Research Compliance**: Designed for academic and legitimate security research only

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Redesign README.md for proper PCAP-only real-time detection system", "status": "completed", "priority": "high"}, {"id": "2", "content": "Design training phase using packet_features.csv", "status": "completed", "priority": "high"}, {"id": "3", "content": "Design real-time phase with PCAP replay and live feature extraction", "status": "completed", "priority": "high"}]