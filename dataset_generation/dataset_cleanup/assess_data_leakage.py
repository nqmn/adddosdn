#!/usr/bin/env python3
"""
Data Leakage Assessment Script for SDN Attack Datasets
Analyzes feature sets in v3 combined datasets for potential data leakage issues
that could affect machine learning model performance and reliability.

Data leakage occurs when information from the future or target variable
inadvertently influences features, leading to unrealistic model performance.

This script analyzes flow_dataset.csv, packet_dataset.csv, and cicflow_dataset.csv
in the specified directory for comprehensive leakage detection.

Usage:
    python3 assess_data_leakage.py [--path PATH]
    
Arguments:
    --path PATH    Path to the dataset directory (default: ../main_output/v3)
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import argparse
import logging
import warnings
from collections import defaultdict
import re
warnings.filterwarnings('ignore')

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def setup_logging(log_path=None):
    """Set up logging configuration."""
    log_file = log_path if log_path else 'assess_data_leakage.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode='w')
        ]
    )
    return logging.getLogger(__name__)

class DataLeakageAssessment:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.results = {}
        self.summary_stats = {}
        self.logger = logging.getLogger(__name__)
        
        # Define potential leakage categories
        self.leakage_patterns = {
            'target_leakage': {
                'description': 'Features directly derived from target variable',
                'patterns': ['label', 'class', 'attack', 'malicious', 'benign', 'normal'],
                'risk_level': 'CRITICAL'
            },
            'statistical_leakage': {
                'description': 'Pre-computed statistical features that may contain future info',
                'patterns': ['avg_', 'mean_', 'std_', 'var_', 'min_', 'max_', 'sum_', 'count_', 'rate'],
                'risk_level': 'HIGH'
            },
            'protocol_specific_leakage': {
                'description': 'Protocol-specific features that may reveal attack signatures',
                'patterns': ['tcp_flags', 'icmp_type', 'tcp_seq', 'tcp_ack', 'urgent', 'rst', 'syn', 'fin'],
                'risk_level': 'MEDIUM'
            },
            'size_duration_leakage': {
                'description': 'Packet/flow size and duration metrics that may reveal attack patterns',
                'patterns': ['duration', 'length', 'size', 'bytes', 'packet_count', 'byte_count'],
                'risk_level': 'LOW'
            },
            'infrastructure_leakage': {
                'description': 'Network infrastructure details (typically dropped in ML)',
                'patterns': ['switch_id', 'port', 'mac', 'eth_', 'vlan', 'table_id', 'cookie', 'timestamp', 'time', 'seq', 'sequence', 'order', 'index', 'id'],
                'risk_level': 'LOW'
            }
        }
        
    def detect_leakage_in_features(self, features, dataset_name):
        """Detect potential data leakage in feature set"""
        leakage_analysis = {
            'dataset_name': dataset_name,
            'total_features': len(features),
            'feature_list': list(features),
            'leakage_detected': {},
            'risk_summary': defaultdict(list),
            'overall_risk': 'LOW'
        }
        
        for category, info in self.leakage_patterns.items():
            matching_features = []
            
            for feature in features:
                feature_lower = feature.lower()
                for pattern in info['patterns']:
                    if pattern.lower() in feature_lower:
                        matching_features.append(feature)
                        break
            
            if matching_features:
                leakage_analysis['leakage_detected'][category] = {
                    'description': info['description'],
                    'risk_level': info['risk_level'],
                    'matching_features': matching_features,
                    'feature_count': len(matching_features),
                    'percentage': round((len(matching_features) / len(features)) * 100, 2)
                }
                leakage_analysis['risk_summary'][info['risk_level']].extend(matching_features)
        
        # Determine overall risk level
        if leakage_analysis['risk_summary']['CRITICAL']:
            leakage_analysis['overall_risk'] = 'CRITICAL'
        elif leakage_analysis['risk_summary']['HIGH']:
            leakage_analysis['overall_risk'] = 'HIGH'
        elif leakage_analysis['risk_summary']['MEDIUM']:
            leakage_analysis['overall_risk'] = 'MEDIUM'
        else:
            leakage_analysis['overall_risk'] = 'LOW'
        
        return leakage_analysis
    
    def analyze_feature_uniqueness(self, df, dataset_name):
        """Analyze unique values for all features to identify potential leakage indicators"""
        uniqueness_analysis = {
            'dataset_name': dataset_name,
            'total_rows': len(df),
            'feature_uniqueness': {},
            'high_cardinality_features': [],
            'low_cardinality_features': [],
            'constant_features': [],
            'near_constant_features': []
        }
        
        for column in df.columns:
            try:
                unique_count = df[column].nunique()
                unique_ratio = unique_count / len(df)
                
                # Get sample unique values (limit to prevent memory issues)
                unique_values = df[column].unique()
                if len(unique_values) > 20:
                    sample_values = list(unique_values[:10]) + ['...'] + list(unique_values[-10:])
                else:
                    sample_values = list(unique_values)
                
                # Convert numpy types to native Python types for JSON serialization
                sample_values_clean = []
                for val in sample_values:
                    if val == '...':
                        sample_values_clean.append('...')
                    elif pd.isna(val):
                        sample_values_clean.append('NaN')
                    elif isinstance(val, (np.integer, np.floating)):
                        sample_values_clean.append(float(val))
                    else:
                        sample_values_clean.append(str(val))
                
                feature_info = {
                    'unique_count': int(unique_count),
                    'unique_ratio': round(unique_ratio, 4),
                    'data_type': str(df[column].dtype),
                    'sample_unique_values': sample_values_clean,
                    'is_constant': unique_count == 1,
                    'is_near_constant': unique_count <= max(1, len(df) * 0.01),  # Less than 1% unique
                    'is_high_cardinality': unique_ratio > 0.9,  # More than 90% unique
                    'missing_count': int(df[column].isnull().sum()),
                    'missing_ratio': round(df[column].isnull().sum() / len(df), 4)
                }
                
                # Add value distribution for low cardinality categorical features
                if unique_count <= 50 and df[column].dtype == 'object':
                    value_counts = df[column].value_counts()
                    feature_info['value_distribution'] = {
                        str(k): int(v) for k, v in value_counts.head(20).items()
                    }
                
                # Add statistics for numeric features
                if pd.api.types.is_numeric_dtype(df[column]):
                    finite_values = df[column][np.isfinite(df[column])]
                    if not finite_values.empty:
                        feature_info['numeric_stats'] = {
                            'min': float(finite_values.min()),
                            'max': float(finite_values.max()),
                            'mean': float(finite_values.mean()),
                            'median': float(finite_values.median()),
                            'std': float(finite_values.std()),
                            'zeros_count': int((df[column] == 0).sum()),
                            'infinity_count': int(np.isinf(df[column]).sum())
                        }
                
                uniqueness_analysis['feature_uniqueness'][column] = feature_info
                
                # Categorize features
                if unique_count == 1:
                    uniqueness_analysis['constant_features'].append(column)
                elif feature_info['is_near_constant']:
                    uniqueness_analysis['near_constant_features'].append(column)
                elif feature_info['is_high_cardinality']:
                    uniqueness_analysis['high_cardinality_features'].append(column)
                elif unique_count <= 10:
                    uniqueness_analysis['low_cardinality_features'].append(column)
                    
            except Exception as e:
                self.logger.warning(f"Error analyzing uniqueness for column {column}: {str(e)}")
                uniqueness_analysis['feature_uniqueness'][column] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        return uniqueness_analysis
    
    def analyze_temporal_patterns(self, df, dataset_name):
        """Analyze temporal patterns that could indicate leakage"""
        temporal_analysis = {
            'dataset_name': dataset_name,
            'has_timestamp': 'timestamp' in df.columns,
            'temporal_issues': [],
            'recommendations': []
        }
        
        if 'timestamp' in df.columns:
            timestamps = pd.to_numeric(df['timestamp'], errors='coerce')
            
            # Check for sorted timestamps (potential leakage)
            if timestamps.is_monotonic_increasing:
                temporal_analysis['temporal_issues'].append({
                    'issue': 'Perfectly sorted timestamps',
                    'description': 'Data is sorted by timestamp, which may cause temporal leakage',
                    'severity': 'HIGH'
                })
                temporal_analysis['recommendations'].append('Shuffle data before train/test split to prevent temporal leakage')
            
            # Check for timestamp gaps
            time_diffs = timestamps.diff().dropna()
            if len(time_diffs) > 0:
                large_gaps = (time_diffs > time_diffs.median() * 10).sum()
                if large_gaps > 0:
                    temporal_analysis['temporal_issues'].append({
                        'issue': f'{large_gaps} large timestamp gaps detected',
                        'description': 'Irregular timestamp gaps may indicate data collection issues',
                        'severity': 'MEDIUM'
                    })
            
            # Check for duplicate timestamps
            duplicate_timestamps = timestamps.duplicated().sum()
            if duplicate_timestamps > len(df) * 0.01:  # More than 1%
                temporal_analysis['temporal_issues'].append({
                    'issue': f'{duplicate_timestamps} duplicate timestamps',
                    'description': 'High number of duplicate timestamps may indicate processing errors',
                    'severity': 'MEDIUM'
                })
        
        return temporal_analysis
    
    def analyze_label_correlation(self, df, dataset_name):
        """Analyze correlation between features and labels"""
        label_analysis = {
            'dataset_name': dataset_name,
            'label_columns': [],
            'high_correlation_features': [],
            'suspicious_patterns': []
        }
        
        # Find label columns
        possible_labels = ['Label_multi', 'Label_binary', 'label', 'attack_type']
        label_cols = [col for col in possible_labels if col in df.columns]
        label_analysis['label_columns'] = label_cols
        
        if not label_cols:
            return label_analysis
        
        # Analyze correlation with numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        non_label_numeric = [col for col in numeric_cols if col not in label_cols]
        
        for label_col in label_cols:
            if label_col in df.columns:
                # Convert labels to numeric for correlation analysis
                if df[label_col].dtype == 'object':
                    label_encoded = pd.factorize(df[label_col])[0]
                else:
                    label_encoded = df[label_col]
                
                correlations = []
                for feature in non_label_numeric:
                    if feature in df.columns:
                        corr = np.corrcoef(df[feature].fillna(0), label_encoded)[0, 1]
                        if not np.isnan(corr) and abs(corr) > 0.8:  # High correlation threshold
                            correlations.append({
                                'feature': feature,
                                'correlation': round(corr, 4),
                                'label': label_col
                            })
                
                if correlations:
                    label_analysis['high_correlation_features'].extend(correlations)
        
        # Check for suspicious patterns in feature names
        for feature in df.columns:
            if any(pattern in feature.lower() for pattern in ['attack', 'malicious', 'intrusion', 'anomaly']):
                label_analysis['suspicious_patterns'].append({
                    'feature': feature,
                    'issue': 'Feature name suggests target variable derivation',
                    'severity': 'CRITICAL'
                })
        
        return label_analysis
    
    def assess_dataset_folder(self, folder_path):
        """Assess all CSV files in a dataset folder for data leakage"""
        folder_name = folder_path.name
        folder_analysis = {
            'folder_name': folder_name,
            'csv_files': [],
            'leakage_assessments': {},
            'uniqueness_analyses': {},
            'temporal_analyses': {},
            'label_correlations': {},
            'overall_folder_risk': 'LOW'
        }
        
        # Find all CSV files
        csv_files = list(folder_path.glob('*.csv'))
        folder_analysis['csv_files'] = [f.name for f in csv_files]
        
        if not csv_files:
            self.logger.warning(f"No CSV files found in {folder_path}")
            return folder_analysis
        
        max_risk_level = 0
        risk_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        
        for csv_file in csv_files:
            try:
                self.logger.info(f"Analyzing {csv_file.name}...")
                df = pd.read_csv(csv_file)
                dataset_name = csv_file.stem
                
                # Feature leakage detection
                leakage_assessment = self.detect_leakage_in_features(df.columns, dataset_name)
                folder_analysis['leakage_assessments'][dataset_name] = leakage_assessment
                
                # Feature uniqueness analysis
                uniqueness_analysis = self.analyze_feature_uniqueness(df, dataset_name)
                folder_analysis['uniqueness_analyses'][dataset_name] = uniqueness_analysis
                
                # Temporal analysis
                temporal_analysis = self.analyze_temporal_patterns(df, dataset_name)
                folder_analysis['temporal_analyses'][dataset_name] = temporal_analysis
                
                # Label correlation analysis
                label_correlation = self.analyze_label_correlation(df, dataset_name)
                folder_analysis['label_correlations'][dataset_name] = label_correlation
                
                # Update overall risk
                current_risk = risk_levels.get(leakage_assessment['overall_risk'], 1)
                max_risk_level = max(max_risk_level, current_risk)
                
            except Exception as e:
                self.logger.error(f"Error analyzing {csv_file.name}: {str(e)}")
                folder_analysis['leakage_assessments'][csv_file.stem] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Set overall folder risk
        for level, value in risk_levels.items():
            if value == max_risk_level:
                folder_analysis['overall_folder_risk'] = level
                break
        
        return folder_analysis
    
    def assess_combined_datasets(self):
        """Assess combined datasets at specific file paths"""
        dataset_files = {
            'flow_dataset': self.base_path / 'flow_dataset.csv',
            'packet_dataset': self.base_path / 'packet_dataset.csv', 
            'cicflow_dataset': self.base_path / 'cicflow_dataset.csv'
        }
        
        self.logger.info(f"Analyzing combined datasets in {self.base_path}")
        
        combined_analysis = {
            'folder_name': 'v3_combined_datasets',
            'csv_files': [],
            'leakage_assessments': {},
            'uniqueness_analyses': {},
            'temporal_analyses': {},
            'label_correlations': {},
            'overall_folder_risk': 'LOW'
        }
        
        max_risk_level = 0
        risk_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        
        for dataset_name, dataset_path in dataset_files.items():
            if not dataset_path.exists():
                self.logger.warning(f"Dataset file not found: {dataset_path}")
                continue
                
            combined_analysis['csv_files'].append(dataset_path.name)
            
            try:
                self.logger.info(f"Analyzing {dataset_name}...")
                df = pd.read_csv(dataset_path)
                
                # Feature leakage detection
                leakage_assessment = self.detect_leakage_in_features(df.columns, dataset_name)
                combined_analysis['leakage_assessments'][dataset_name] = leakage_assessment
                
                # Feature uniqueness analysis
                uniqueness_analysis = self.analyze_feature_uniqueness(df, dataset_name)
                combined_analysis['uniqueness_analyses'][dataset_name] = uniqueness_analysis
                
                # Temporal analysis
                temporal_analysis = self.analyze_temporal_patterns(df, dataset_name)
                combined_analysis['temporal_analyses'][dataset_name] = temporal_analysis
                
                # Label correlation analysis
                label_correlation = self.analyze_label_correlation(df, dataset_name)
                combined_analysis['label_correlations'][dataset_name] = label_correlation
                
                # Update overall risk
                current_risk = risk_levels.get(leakage_assessment['overall_risk'], 1)
                max_risk_level = max(max_risk_level, current_risk)
                
            except Exception as e:
                self.logger.error(f"Error analyzing {dataset_name}: {str(e)}")
                combined_analysis['leakage_assessments'][dataset_name] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        # Set overall folder risk
        for level, value in risk_levels.items():
            if value == max_risk_level:
                combined_analysis['overall_folder_risk'] = level
                break
        
        self.results['v3_combined_datasets'] = combined_analysis

    def assess_all_folders(self):
        """Assess all dataset folders in the base path"""
        if not self.base_path.exists():
            self.logger.error(f"Base path does not exist: {self.base_path}")
            return
        
        # Check if this is the v3 directory with combined datasets
        expected_files = ['flow_dataset.csv', 'packet_dataset.csv', 'cicflow_dataset.csv']
        if all((self.base_path / f).exists() for f in expected_files):
            self.logger.info("Detected v3 combined datasets directory, analyzing combined datasets")
            self.assess_combined_datasets()
            return
        
        # Find all subdirectories
        subfolders = [p for p in self.base_path.iterdir() if p.is_dir()]
        
        if not subfolders:
            self.logger.warning(f"No subdirectories found in {self.base_path}")
            return
        
        self.logger.info(f"Found {len(subfolders)} dataset folders to analyze")
        
        for folder in sorted(subfolders):
            self.logger.info(f"Processing folder: {folder.name}")
            folder_analysis = self.assess_dataset_folder(folder)
            self.results[folder.name] = folder_analysis
    
    def generate_summary_statistics(self):
        """Generate overall summary statistics"""
        total_folders = len(self.results)
        successful_folders = sum(1 for r in self.results.values() if 'error' not in str(r))
        
        risk_distribution = defaultdict(int)
        total_features = 0
        leaky_features = 0
        
        for folder_name, analysis in self.results.items():
            if isinstance(analysis, dict) and 'overall_folder_risk' in analysis:
                risk_distribution[analysis['overall_folder_risk']] += 1
                
                for dataset_name, leakage_data in analysis.get('leakage_assessments', {}).items():
                    if isinstance(leakage_data, dict) and 'total_features' in leakage_data:
                        total_features += leakage_data['total_features']
                        leaky_features += sum(
                            len(cat_data.get('matching_features', []))
                            for cat_data in leakage_data.get('leakage_detected', {}).values()
                        )
        
        self.summary_stats = {
            'total_folders_analyzed': total_folders,
            'successful_analyses': successful_folders,
            'analysis_timestamp': datetime.now().isoformat(),
            'risk_distribution': dict(risk_distribution),
            'total_features_analyzed': total_features,
            'potentially_leaky_features': leaky_features,
            'leakage_percentage': round((leaky_features / max(1, total_features)) * 100, 2),
            'overall_assessment': self.calculate_overall_assessment()
        }
    
    def calculate_overall_assessment(self):
        """Calculate overall data leakage risk assessment"""
        if not self.results:
            return 'NO_DATA'
        
        risk_counts = defaultdict(int)
        for analysis in self.results.values():
            if isinstance(analysis, dict):
                risk = analysis.get('overall_folder_risk', 'LOW')
                risk_counts[risk] += 1
        
        total = sum(risk_counts.values())
        if risk_counts['CRITICAL'] > 0:
            return 'CRITICAL'
        elif risk_counts['HIGH'] / total > 0.5:
            return 'HIGH'
        elif risk_counts['MEDIUM'] / total > 0.3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_report(self):
        """Generate comprehensive data leakage assessment report"""
        report = []
        report.append("# Data Leakage Assessment Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Dataset Path: {self.base_path}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        overall_risk = self.summary_stats.get('overall_assessment', 'UNKNOWN')
        
        if overall_risk == 'CRITICAL':
            status = "⚠️ CRITICAL DATA LEAKAGE DETECTED"
            recommendation = "Immediate attention required before ML training"
        elif overall_risk == 'HIGH':
            status = "⚠️ HIGH RISK OF DATA LEAKAGE"
            recommendation = "Significant modifications needed before ML training"
        elif overall_risk == 'MEDIUM':
            status = "⚠️ MODERATE LEAKAGE RISK"
            recommendation = "Some features should be reviewed and potentially removed"
        else:
            status = "✅ LOW LEAKAGE RISK"
            recommendation = "Dataset appears suitable for ML training with standard precautions"
        
        report.append(f"**Overall Assessment**: {status}")
        report.append(f"**Recommendation**: {recommendation}")
        report.append(f"**Folders Analyzed**: {self.summary_stats['successful_analyses']}/{self.summary_stats['total_folders_analyzed']}")
        report.append(f"**Features Analyzed**: {self.summary_stats['total_features_analyzed']:,}")
        report.append(f"**Potentially Leaky Features**: {self.summary_stats['potentially_leaky_features']:,} ({self.summary_stats['leakage_percentage']:.1f}%)")
        report.append("")
        
        # Risk Distribution
        report.append("## Risk Distribution Across Folders")
        risk_dist = self.summary_stats['risk_distribution']
        for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = risk_dist.get(risk_level, 0)
            if count > 0:
                report.append(f"- {risk_level}: {count} folders")
        report.append("")
        
        # Detailed Analysis by Folder
        report.append("## Detailed Analysis by Folder")
        
        for folder_name, analysis in sorted(self.results.items()):
            if isinstance(analysis, dict) and 'leakage_assessments' in analysis:
                report.append(f"### Folder: {folder_name}")
                report.append(f"**Overall Risk**: {analysis['overall_folder_risk']}")
                report.append(f"**CSV Files**: {', '.join(analysis['csv_files'])}")
                report.append("")
                
                # Feature leakage analysis
                for dataset_name, leakage_data in analysis['leakage_assessments'].items():
                    if isinstance(leakage_data, dict) and 'leakage_detected' in leakage_data:
                        report.append(f"#### Dataset: {dataset_name}")
                        report.append(f"**Total Features**: {leakage_data['total_features']}")
                        report.append(f"**Overall Risk**: {leakage_data['overall_risk']}")
                        
                        # Leakage categories
                        if leakage_data['leakage_detected']:
                            report.append("**Detected Leakage Categories**:")
                            for category, cat_data in leakage_data['leakage_detected'].items():
                                report.append(f"- **{category.replace('_', ' ').title()}** ({cat_data['risk_level']}): {cat_data['feature_count']} features ({cat_data['percentage']:.1f}%)")
                                report.append(f"  - Description: {cat_data['description']}")
                                report.append(f"  - Features: {', '.join(cat_data['matching_features'][:10])}")  # Limit display
                                if len(cat_data['matching_features']) > 10:
                                    report.append(f"  - ... and {len(cat_data['matching_features']) - 10} more")
                        else:
                            report.append("**No leakage patterns detected** ✅")
                        report.append("")
                
                # Feature uniqueness analysis
                uniqueness_data = analysis.get('uniqueness_analyses', {}).get(dataset_name, {})
                if uniqueness_data and 'feature_uniqueness' in uniqueness_data:
                    report.append(f"#### 🔍 Detailed Feature Uniqueness Analysis for {dataset_name}")
                    
                    # Summary statistics
                    constant_features = uniqueness_data.get('constant_features', [])
                    near_constant_features = uniqueness_data.get('near_constant_features', [])
                    high_cardinality_features = uniqueness_data.get('high_cardinality_features', [])
                    low_cardinality_features = uniqueness_data.get('low_cardinality_features', [])
                    
                    report.append(f"**Summary**: {uniqueness_data['total_rows']:,} total records")
                    
                    if constant_features:
                        report.append(f"- **Constant features**: {len(constant_features)} features (may be removable)")
                    if near_constant_features:
                        report.append(f"- **Near-constant features**: {len(near_constant_features)} features (<1% unique)")
                    if high_cardinality_features:
                        report.append(f"- **High cardinality features**: {len(high_cardinality_features)} features (>90% unique)")
                    if low_cardinality_features:
                        report.append(f"- **Low cardinality features**: {len(low_cardinality_features)} features (≤10 unique values)")
                    
                    report.append("")
                    
                    # Detailed feature analysis for risky features
                    feature_uniqueness = uniqueness_data['feature_uniqueness']
                    
                    # Get all features flagged as risky in leakage analysis
                    risky_features = set()
                    for cat_data in leakage_data.get('leakage_detected', {}).values():
                        risky_features.update(cat_data.get('matching_features', []))
                    
                    if risky_features:
                        report.append("**🚨 Detailed Analysis of Risky Features:**")
                        report.append("")
                        report.append("| Feature | Risk Type | Unique Count | Unique Ratio | Data Type | Sample Values | Notes |")
                        report.append("|---------|-----------|--------------|--------------|-----------|---------------|-------|")
                        
                        for feature in sorted(risky_features):
                            if feature in feature_uniqueness:
                                feat_info = feature_uniqueness[feature]
                                
                                # Determine risk type
                                risk_types = []
                                for category, cat_data in leakage_data.get('leakage_detected', {}).items():
                                    if feature in cat_data.get('matching_features', []):
                                        risk_types.append(f"{category.replace('_', ' ').title()}")
                                
                                risk_type_str = ", ".join(risk_types)
                                
                                # Format sample values
                                sample_values = feat_info.get('sample_unique_values', [])
                                if len(sample_values) > 5:
                                    sample_str = f"{', '.join(map(str, sample_values[:3]))}, ..."
                                else:
                                    sample_str = ', '.join(map(str, sample_values))
                                
                                # Generate notes
                                notes = []
                                if feat_info.get('is_constant'):
                                    notes.append("Constant")
                                elif feat_info.get('is_near_constant'):
                                    notes.append("Near-constant")
                                elif feat_info.get('is_high_cardinality'):
                                    notes.append("High cardinality")
                                
                                if feat_info.get('missing_count', 0) > 0:
                                    notes.append(f"{feat_info['missing_ratio']:.1%} missing")
                                
                                notes_str = "; ".join(notes) if notes else "Normal"
                                
                                report.append(f"| {feature} | {risk_type_str} | {feat_info.get('unique_count', 'N/A'):,} | {feat_info.get('unique_ratio', 0):.3f} | {feat_info.get('data_type', 'unknown')} | {sample_str} | {notes_str} |")
                    
                    report.append("")
                    
                    # Additional analysis for constant/near-constant features
                    if constant_features or near_constant_features:
                        report.append("**🔧 Constant/Near-Constant Feature Analysis:**")
                        
                        for feature in constant_features + near_constant_features:
                            if feature in feature_uniqueness:
                                feat_info = feature_uniqueness[feature]
                                sample_values = feat_info.get('sample_unique_values', [])
                                
                                if feat_info.get('is_constant'):
                                    report.append(f"- **{feature}** (CONSTANT): Always = `{sample_values[0] if sample_values else 'N/A'}` → **REMOVE**")
                                else:
                                    report.append(f"- **{feature}** (NEAR-CONSTANT): {feat_info.get('unique_count', 0)} unique values → Consider removal")
                                    if feat_info.get('value_distribution'):
                                        top_value = max(feat_info['value_distribution'].items(), key=lambda x: x[1])
                                        total_records = uniqueness_data['total_rows']
                                        pct = (top_value[1] / total_records) * 100
                                        report.append(f"  - Most common: `{top_value[0]}` ({top_value[1]:,} records, {pct:.1f}%)")
                    
                    report.append("")
                
                # Temporal analysis
                temporal_data = analysis.get('temporal_analyses', {})
                if temporal_data:
                    report.append("#### Temporal Analysis")
                    for dataset_name, temp_analysis in temporal_data.items():
                        if temp_analysis.get('temporal_issues'):
                            report.append(f"**{dataset_name}** temporal issues:")
                            for issue in temp_analysis['temporal_issues']:
                                report.append(f"- {issue['severity']}: {issue['issue']} - {issue['description']}")
                    report.append("")
                
                # Label correlation analysis
                label_data = analysis.get('label_correlations', {})
                if label_data:
                    report.append("#### Label Correlation Analysis")
                    for dataset_name, label_analysis in label_data.items():
                        high_corr = label_analysis.get('high_correlation_features', [])
                        suspicious = label_analysis.get('suspicious_patterns', [])
                        
                        if high_corr or suspicious:
                            report.append(f"**{dataset_name}** label issues:")
                            for corr in high_corr[:5]:  # Top 5 correlations
                                report.append(f"- HIGH CORRELATION: {corr['feature']} → {corr['label']} (r={corr['correlation']:.3f})")
                            for susp in suspicious:
                                report.append(f"- {susp['severity']}: {susp['feature']} - {susp['issue']}")
                    report.append("")
                
                report.append("")
        
        # Recommendations
        report.append("## 🛠️ Data Leakage Mitigation Recommendations")
        
        report.append("### Critical Actions Required")
        critical_actions = []
        
        # Check for critical issues across all datasets
        has_target_leakage = any(
            'target_leakage' in analysis.get('leakage_assessments', {}).get(dataset, {}).get('leakage_detected', {})
            for analysis in self.results.values()
            for dataset in analysis.get('leakage_assessments', {})
            if isinstance(analysis, dict)
        )
        
        if has_target_leakage:
            critical_actions.append("**Remove target-derived features**: Features directly derived from target variables must be removed")
        
        if overall_risk in ['CRITICAL', 'HIGH']:
            critical_actions.append("**Feature audit**: Manually review all flagged features before training")
            critical_actions.append("**Temporal validation**: Ensure proper temporal train/test splits")
        
        if critical_actions:
            for action in critical_actions:
                report.append(f"1. {action}")
        else:
            report.append("No critical actions required ✅")
        
        report.append("")
        
        # Feature-specific recommendations
        report.append("### Feature-Specific Recommendations")
        
        # Collect all leaky features by category
        feature_recommendations = defaultdict(set)
        for analysis in self.results.values():
            if isinstance(analysis, dict):
                for leakage_data in analysis.get('leakage_assessments', {}).values():
                    if isinstance(leakage_data, dict):
                        for category, cat_data in leakage_data.get('leakage_detected', {}).items():
                            for feature in cat_data.get('matching_features', []):
                                feature_recommendations[category].add(feature)
        
        for category, features in feature_recommendations.items():
            if features:
                category_name = category.replace('_', ' ').title()
                risk_level = self.leakage_patterns[category]['risk_level']
                
                report.append(f"#### {category_name} ({risk_level} Risk)")
                report.append(f"**Affected features**: {', '.join(sorted(list(features)))}")
                
                if category == 'target_leakage':
                    report.append("**Action**: Remove these features immediately")
                elif category == 'temporal_leakage':
                    report.append("**Action**: Remove temporal ordering features; keep timestamp for proper splitting only")
                elif category == 'statistical_leakage':
                    report.append("**Action**: Review if statistics are computed over future data; recompute if necessary")
                elif category == 'infrastructure_leakage':
                    report.append("**Action**: Consider removing if they don't generalize to other network environments")
                else:
                    report.append("**Action**: Review for necessity and potential impact on generalization")
                
                report.append("")
        
        # ML Pipeline recommendations
        report.append("### ML Pipeline Recommendations")
        report.append("1. **Temporal Splits**: Use timestamp-based train/test splits, not random splits")
        report.append("2. **Cross-validation**: Use time-series cross-validation for temporal data")
        report.append("3. **Feature Engineering**: Create features from raw data within each fold separately")
        report.append("4. **Validation Strategy**: Implement separate validation on hold-out temporal data")
        report.append("5. **Model Monitoring**: Track feature importance to detect potential leakage indicators")
        report.append("")
        
        # Python code examples
        report.append("### 🐍 Python Code for Leakage Prevention")
        
        report.append("#### Temporal Train/Test Split")
        report.append("```python")
        report.append("import pandas as pd")
        report.append("from sklearn.model_selection import TimeSeriesSplit")
        report.append("")
        report.append("# Load data and sort by timestamp")
        report.append("df = pd.read_csv('dataset.csv')")
        report.append("df = df.sort_values('timestamp')")
        report.append("")
        report.append("# Time-based split (80% train, 20% test)")
        report.append("split_time = df['timestamp'].quantile(0.8)")
        report.append("train_data = df[df['timestamp'] <= split_time]")
        report.append("test_data = df[df['timestamp'] > split_time]")
        report.append("")
        report.append("# Remove timestamp from features")
        report.append("feature_cols = [col for col in df.columns if col not in ['timestamp', 'Label_multi', 'Label_binary']]")
        report.append("X_train, y_train = train_data[feature_cols], train_data['Label_binary']")
        report.append("X_test, y_test = test_data[feature_cols], test_data['Label_binary']")
        report.append("```")
        report.append("")
        
        report.append("#### Feature Leakage Detection")
        report.append("```python")
        report.append("def detect_leakage_features(df, target_col):")
        report.append("    leaky_features = []")
        report.append("    ")
        report.append("    for col in df.columns:")
        report.append("        if col == target_col:")
        report.append("            continue")
        report.append("        ")
        report.append("        # Check correlation with target")
        report.append("        if df[col].dtype in ['int64', 'float64']:")
        report.append("            corr = df[col].corr(df[target_col])")
        report.append("            if abs(corr) > 0.9:  # Very high correlation")
        report.append("                leaky_features.append((col, corr))")
        report.append("        ")
        report.append("        # Check for suspicious names")
        report.append("        suspicious_patterns = ['label', 'target', 'class', 'attack', 'malicious']")
        report.append("        if any(pattern in col.lower() for pattern in suspicious_patterns):")
        report.append("            leaky_features.append((col, 'suspicious_name'))")
        report.append("    ")
        report.append("    return leaky_features")
        report.append("```")
        report.append("")
        
        return "\n".join(report)
    
    def save_results(self, output_dir):
        """Save results to files"""
        output_path = Path(output_dir) if output_dir else self.base_path
        output_path.mkdir(exist_ok=True)
        
        # Save detailed JSON results
        results_file = output_path / 'data_leakage_assessment.json'
        with open(results_file, 'w') as f:
            json.dump({
                'summary': self.summary_stats,
                'detailed_results': self.results,
                'analysis_timestamp': datetime.now().isoformat()
            }, f, indent=2, cls=NumpyEncoder)
        
        # Save report
        report = self.generate_report()
        report_file = output_path / 'data_leakage_assessment_report.md'
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Results saved to {output_path}")
        return report

def main():
    parser = argparse.ArgumentParser(description='Assess data leakage in SDN attack datasets')
    parser.add_argument('--path', default='../main_output/v3', 
                       help='Path to dataset directory (default: ../main_output/v3)')
    parser.add_argument('--output', default=None,
                       help='Output directory for results (default: same as input path)')
    args = parser.parse_args()
    
    base_path = Path(args.path)
    if not base_path.exists():
        print(f"❌ Error: Dataset path not found: {base_path}")
        return 1
    
    # Set up logging
    log_path = base_path / "assess_data_leakage.log"
    logger = setup_logging(log_path)
    
    assessor = DataLeakageAssessment(base_path)
    
    logger.info("Starting data leakage assessment...")
    assessor.assess_all_folders()
    
    logger.info("Generating summary statistics...")
    assessor.generate_summary_statistics()
    
    logger.info("Generating comprehensive report...")
    report = assessor.save_results(args.output)
    
    logger.info("\n" + "="*60)
    logger.info("DATA LEAKAGE ASSESSMENT COMPLETE")
    logger.info("="*60)
    
    # Print quick summary
    overall_risk = assessor.summary_stats.get('overall_assessment', 'UNKNOWN')
    print(f"\n🔍 DATA LEAKAGE ASSESSMENT SUMMARY")
    print(f"Overall Risk Level: {overall_risk}")
    print(f"Features Analyzed: {assessor.summary_stats['total_features_analyzed']:,}")
    print(f"Potentially Leaky Features: {assessor.summary_stats['potentially_leaky_features']:,} ({assessor.summary_stats['leakage_percentage']:.1f}%)")
    print(f"Report saved to: {base_path / 'data_leakage_assessment_report.md'}")
    
    return 0

if __name__ == "__main__":
    exit(main())