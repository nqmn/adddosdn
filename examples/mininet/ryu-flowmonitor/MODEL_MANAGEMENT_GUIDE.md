# ML Model Management Guide

This guide covers the ML model upload, download, and management functionality in the Enhanced Ryu Flow Monitor system.

## Overview

The Enhanced Ryu Flow Monitor supports uploading, downloading, and managing ML models in pickle (.pkl) format. This allows for:

- **Model Sharing**: Share trained models between controllers
- **Model Updates**: Update existing models with improved versions
- **Model Backup**: Download and backup current models
- **Model Testing**: Upload and test different model configurations
- **Federated Learning**: Share models across distributed controllers

## Supported Model Types

### 1. DDoS Detector Models
Complete DDoS detection models with the following structure:
```python
{
    'model': sklearn_model,           # Main ML model (IsolationForest, RandomForest, etc.)
    'scaler': StandardScaler(),       # Feature scaler
    'controller_id': 'controller_1',  # Source controller ID
    'timestamp': 1234567890.0,       # Creation timestamp
    'model_type': 'ddos_detector',    # Model type identifier
    'description': 'Model description'
}
```

### 2. Federated Learning Models
Global models for federated learning:
```python
{
    'version': 1,                     # Model version
    'model_weights': {...},           # Neural network weights
    'timestamp': 1234567890.0,        # Creation timestamp
    'model_type': 'federated_model',  # Model type identifier
    'aggregation_round': 1            # Federated learning round
}
```

### 3. Custom Models
Any scikit-learn compatible model:
```python
# Simple model object
model = RandomForestClassifier()

# Or structured model data
{
    'model': sklearn_model,
    'model_type': 'custom',
    'timestamp': 1234567890.0,
    'description': 'Custom classifier'
}
```

## Web Interface Usage

### Accessing Model Manager

1. Open the web interface: `http://controller-ip:port/flow_monitor.html`
2. Click the **"Model Manager"** button in the control panel
3. The Model Manager modal will open

### Uploading Models

1. **Select Model File**: Choose a `.pkl` file from your computer
2. **Choose Model Type**: Select the appropriate model type:
   - `DDoS Detector`: For DDoS detection models
   - `Federated Model`: For federated learning models
   - `Custom Model`: For other ML models
3. **Replace Option**: Check "Replace existing model" to overwrite models with the same name
4. **Upload**: Click "Upload Model" to upload the file

### Managing Models

The model list shows:
- **Model Name**: Unique identifier
- **Type**: Model category (uploaded, current, etc.)
- **Size**: File size in bytes
- **Modified Date**: Last modification timestamp
- **Status**: Active models are marked with "ACTIVE" badge

Available actions:
- **📥 Download**: Download the model file
- **🗑️ Delete**: Remove the model (not available for active models)

## API Usage

### Upload Model
```bash
curl -X POST \
  http://controller-ip:port/models/upload \
  -F "model_file=@path/to/model.pkl" \
  -F "model_type=ddos_detector" \
  -F "replace_existing=false"
```

### List Models
```bash
curl http://controller-ip:port/models/list
```

### Download Model
```bash
curl -O http://controller-ip:port/models/download/model_name
```

### Delete Model
```bash
curl -X DELETE http://controller-ip:port/models/delete/model_name
```

## Creating Sample Models

Use the provided script to create sample models for testing:

```bash
# Create all sample models
python3 create_sample_models.py --create-all

# List existing models
python3 create_sample_models.py --list-models

# Validate a model file
python3 create_sample_models.py --validate models/sample_ddos_detector.pkl
```

## Model Creation Examples

### Creating a DDoS Detection Model

```python
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
from datetime import datetime

# Create training data
X, y = make_classification(n_samples=1000, n_features=10, random_state=42)

# Train model and scaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_scaled)

# Create model data structure
model_data = {
    'model': model,
    'scaler': scaler,
    'controller_id': 'my_controller',
    'timestamp': datetime.now().timestamp(),
    'model_type': 'ddos_detector',
    'description': 'Custom DDoS detection model',
    'features': ['packet_count', 'byte_count', 'duration', ...],
    'performance_metrics': {
        'accuracy': 0.95,
        'precision': 0.93,
        'recall': 0.97
    }
}

# Save model
with open('my_ddos_model.pkl', 'wb') as f:
    pickle.dump(model_data, f)
```

### Creating a Simple Classifier

```python
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# Create and train model
X, y = make_classification(n_samples=500, n_features=5, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save simple model
with open('simple_classifier.pkl', 'wb') as f:
    pickle.dump(model, f)
```

## Best Practices

### Model Validation
- Always validate models before uploading
- Test models with sample data
- Check model compatibility with the system

### Model Naming
- Use descriptive names: `ddos_detector_v2_improved`
- Include version numbers: `model_v1.0`
- Add date stamps: `model_20241201`

### Model Security
- Only upload trusted models
- Validate model sources
- Backup important models

### Performance Considerations
- Keep model files under 100MB for faster uploads
- Use model compression when possible
- Monitor model performance after upload

## Troubleshooting

### Upload Errors

**"Only .pkl files are allowed"**
- Ensure file has `.pkl` extension
- File must be a valid pickle file

**"Invalid model structure"**
- Check model data structure matches expected format
- Validate required fields are present

**"Invalid pickle file"**
- File may be corrupted
- Try recreating the model file

### Download Issues

**"Model file not found"**
- Model may have been deleted
- Check model name spelling

**"Download failed"**
- Check network connectivity
- Verify controller is running

### Performance Issues

**Slow uploads**
- Large model files take longer
- Check network bandwidth
- Consider model compression

**Model loading errors**
- Check model compatibility
- Verify required libraries are installed

## Integration with Federated Learning

### Sharing Models Between Controllers

1. **Export Model**: Download model from source controller
2. **Transfer**: Copy model file to target controller
3. **Import**: Upload model to target controller
4. **Activate**: System automatically uses uploaded DDoS detector models

### Model Synchronization

The system supports automatic model synchronization:
- Root controller aggregates models from clients
- Global models are distributed to all clients
- Local models are updated with global improvements

## Advanced Usage

### Programmatic Model Management

```python
import requests

# Upload model programmatically
def upload_model(controller_url, model_path, model_type='ddos_detector'):
    with open(model_path, 'rb') as f:
        files = {'model_file': f}
        data = {'model_type': model_type}
        response = requests.post(f"{controller_url}/models/upload", 
                               files=files, data=data)
    return response.json()

# Download model programmatically
def download_model(controller_url, model_name, save_path):
    response = requests.get(f"{controller_url}/models/download/{model_name}")
    if response.ok:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    return False
```

### Batch Model Operations

```bash
# Upload multiple models
for model in models/*.pkl; do
    curl -X POST http://controller:8080/models/upload \
         -F "model_file=@$model" \
         -F "model_type=ddos_detector"
done

# Download all models
curl http://controller:8080/models/list | \
jq -r '.models[].name' | \
while read model; do
    curl -O http://controller:8080/models/download/$model
done
```

This model management system provides flexible and powerful capabilities for managing ML models in the Enhanced Ryu Flow Monitor, supporting both manual and automated workflows for model deployment and updates.
