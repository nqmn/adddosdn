#!/usr/bin/env python3
"""
Sample Model Creator for Enhanced Ryu Flow Monitor
This script creates sample ML models for testing the model upload functionality.
"""

import pickle
import numpy as np
import os
from datetime import datetime
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
import argparse

def create_ddos_detector_model(name="sample_ddos_detector"):
    """Create a sample DDoS detection model"""
    print(f"Creating DDoS detector model: {name}")
    
    # Create sample training data
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )
    
    # Create and train models
    isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
    scaler = StandardScaler()
    
    # Fit the models
    X_scaled = scaler.fit_transform(X)
    isolation_forest.fit(X_scaled)
    random_forest.fit(X_scaled, y)
    
    # Create model data structure
    model_data = {
        'model': isolation_forest,
        'backup_model': random_forest,
        'scaler': scaler,
        'controller_id': 'sample_controller',
        'timestamp': datetime.now().timestamp(),
        'creation_date': datetime.now().isoformat(),
        'model_type': 'ddos_detector',
        'version': '1.0',
        'description': 'Sample DDoS detection model for testing',
        'features': [
            'packet_count', 'byte_count', 'duration', 'packets_per_second',
            'bytes_per_packet', 'flow_priority', 'packet_size', 'protocol_type',
            'port_entropy', 'flow_rate'
        ],
        'performance_metrics': {
            'accuracy': 0.95,
            'precision': 0.93,
            'recall': 0.97,
            'f1_score': 0.95
        }
    }
    
    return model_data

def create_federated_model(name="sample_federated_model"):
    """Create a sample federated learning model"""
    print(f"Creating federated learning model: {name}")
    
    # Create sample model weights (simulated)
    model_weights = {
        'layer_1': np.random.randn(10, 20).tolist(),
        'layer_2': np.random.randn(20, 10).tolist(),
        'layer_3': np.random.randn(10, 2).tolist(),
        'bias_1': np.random.randn(20).tolist(),
        'bias_2': np.random.randn(10).tolist(),
        'bias_3': np.random.randn(2).tolist()
    }
    
    model_data = {
        'version': 1,
        'model_weights': model_weights,
        'timestamp': datetime.now().timestamp(),
        'creation_date': datetime.now().isoformat(),
        'model_type': 'federated_model',
        'aggregation_round': 1,
        'participating_controllers': ['controller_1', 'controller_2', 'controller_3'],
        'global_accuracy': 0.92,
        'description': 'Sample federated learning model for testing'
    }
    
    return model_data

def create_custom_classifier(name="sample_custom_classifier"):
    """Create a sample custom classifier"""
    print(f"Creating custom classifier: {name}")
    
    # Create sample data
    X, y = make_classification(
        n_samples=500,
        n_features=15,
        n_informative=10,
        n_redundant=5,
        n_classes=3,
        random_state=42
    )
    
    # Create and train classifier
    classifier = RandomForestClassifier(n_estimators=50, random_state=42)
    scaler = StandardScaler()
    
    X_scaled = scaler.fit_transform(X)
    classifier.fit(X_scaled, y)
    
    model_data = {
        'model': classifier,
        'scaler': scaler,
        'model_type': 'custom_classifier',
        'timestamp': datetime.now().timestamp(),
        'creation_date': datetime.now().isoformat(),
        'version': '1.0',
        'description': 'Sample custom classifier for testing',
        'classes': ['benign', 'suspicious', 'malicious'],
        'feature_count': 15,
        'accuracy': 0.88
    }
    
    return model_data

def save_model(model_data, filename):
    """Save model to pickle file"""
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    filepath = os.path.join('models', f"{filename}.pkl")
    
    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)
    
    # Get file size
    file_size = os.path.getsize(filepath)
    
    print(f"✅ Model saved: {filepath} ({file_size} bytes)")
    return filepath

def create_all_sample_models():
    """Create all sample models"""
    print("Creating sample ML models for testing...")
    print("=" * 50)
    
    models_created = []
    
    # Create DDoS detector model
    try:
        ddos_model = create_ddos_detector_model()
        filepath = save_model(ddos_model, "sample_ddos_detector")
        models_created.append(filepath)
    except Exception as e:
        print(f"❌ Failed to create DDoS detector model: {e}")
    
    # Create federated learning model
    try:
        federated_model = create_federated_model()
        filepath = save_model(federated_model, "sample_federated_model")
        models_created.append(filepath)
    except Exception as e:
        print(f"❌ Failed to create federated model: {e}")
    
    # Create custom classifier
    try:
        custom_model = create_custom_classifier()
        filepath = save_model(custom_model, "sample_custom_classifier")
        models_created.append(filepath)
    except Exception as e:
        print(f"❌ Failed to create custom classifier: {e}")
    
    # Create a simple model (just the classifier object)
    try:
        print("Creating simple classifier model: simple_model")
        X, y = make_classification(n_samples=200, n_features=5, random_state=42)
        simple_model = RandomForestClassifier(n_estimators=10, random_state=42)
        simple_model.fit(X, y)
        
        filepath = save_model(simple_model, "simple_model")
        models_created.append(filepath)
    except Exception as e:
        print(f"❌ Failed to create simple model: {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ Created {len(models_created)} sample models:")
    for filepath in models_created:
        print(f"   - {filepath}")
    
    print("\nThese models can now be uploaded through the web interface!")
    print("Access the Model Manager in the web interface to upload and manage models.")

def validate_model(filepath):
    """Validate a model file"""
    try:
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        print(f"✅ Model validation successful: {filepath}")
        
        if isinstance(model_data, dict):
            print(f"   Model type: {model_data.get('model_type', 'unknown')}")
            print(f"   Creation date: {model_data.get('creation_date', 'unknown')}")
            print(f"   Description: {model_data.get('description', 'No description')}")
        else:
            print(f"   Model object type: {type(model_data).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create sample ML models for testing')
    parser.add_argument('--create-all', action='store_true',
                       help='Create all sample models')
    parser.add_argument('--validate', type=str,
                       help='Validate a specific model file')
    parser.add_argument('--list-models', action='store_true',
                       help='List existing model files')
    
    args = parser.parse_args()
    
    if args.validate:
        validate_model(args.validate)
    elif args.list_models:
        models_dir = 'models'
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
            if model_files:
                print("Existing model files:")
                for model_file in model_files:
                    filepath = os.path.join(models_dir, model_file)
                    size = os.path.getsize(filepath)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    print(f"  - {model_file} ({size} bytes, modified: {mtime})")
            else:
                print("No model files found in models/ directory")
        else:
            print("Models directory does not exist")
    else:
        create_all_sample_models()

if __name__ == '__main__':
    main()
