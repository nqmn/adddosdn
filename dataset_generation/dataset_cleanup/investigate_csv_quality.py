#!/usr/bin/env python3
"""
CSV Data Quality Investigation Script
Analyzes combined CSV datasets for preprocessing issues, missing values, 
infinity values, data types, cross-dataset consistency, and other quality metrics.

Updated to focus on combined datasets: packet_dataset.csv, flow_dataset.csv, cicflow_dataset.csv

Usage:
    python3 investigate_csv_quality.py [--path PATH]
    
Arguments:
    --path PATH    Path to the dataset directory (default: ../main_output/v2_main)
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
    log_file = log_path if log_path else 'investigate_csv_quality.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode='w')
        ]
    )
    return logging.getLogger(__name__)

class CombinedDatasetInvestigator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.results = {}
        self.summary_stats = {}
        self.combined_files = [
            'packet_dataset.csv',
            'flow_dataset.csv', 
            'cicflow_dataset.csv'
        ]
        self.logger = logging.getLogger(__name__)
        
    def analyze_combined_dataset(self, file_path, dataset_type):
        """Analyze a combined CSV dataset for quality issues and cross-dataset integrity"""
        try:
            self.logger.info(f"Analyzing {dataset_type}...")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            analysis = {
                'file_path': str(file_path),
                'dataset_type': dataset_type,
                'file_size_mb': round(file_path.stat().st_size / 1024 / 1024, 2),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
            # Dataset ID analysis (cross-dataset consistency)
            if 'dataset_id' in df.columns:
                dataset_distribution = df['dataset_id'].value_counts().sort_index()
                analysis['dataset_distribution'] = {
                    'unique_datasets': list(dataset_distribution.index),
                    'record_counts': dataset_distribution.to_dict(),
                    'total_datasets': len(dataset_distribution),
                    'min_records': int(dataset_distribution.min()),
                    'max_records': int(dataset_distribution.max()),
                    'mean_records': round(dataset_distribution.mean(), 2),
                    'std_records': round(dataset_distribution.std(), 2)
                }
                
                # Check for balanced distribution
                analysis['dataset_balance'] = {
                    'is_balanced': (dataset_distribution.max() - dataset_distribution.min()) < (dataset_distribution.mean() * 0.1),
                    'imbalance_ratio': round(dataset_distribution.max() / dataset_distribution.min(), 2) if dataset_distribution.min() > 0 else float('inf')
                }
            
            # Data type analysis
            analysis['data_types'] = {}
            type_summary = {}
            for col in df.columns:
                dtype_str = str(df[col].dtype)
                analysis['data_types'][col] = dtype_str
                type_summary[dtype_str] = type_summary.get(dtype_str, 0) + 1
            
            analysis['type_summary'] = type_summary
            
            # Missing values analysis
            missing_counts = df.isnull().sum()
            analysis['missing_values'] = {
                'total_missing': int(missing_counts.sum()),
                'missing_percentage': round((missing_counts.sum() / (len(df) * len(df.columns))) * 100, 4),
                'columns_with_missing': {},
                'missing_per_dataset': {}
            }
            
            # Missing values per column (detailed analysis)
            for col in df.columns:
                missing_count = missing_counts[col]
                if missing_count > 0:
                    analysis['missing_values']['columns_with_missing'][col] = {
                        'count': int(missing_count),
                        'percentage': round((missing_count / len(df)) * 100, 4),
                        'data_type': str(df[col].dtype),
                        'non_missing_count': int(len(df) - missing_count),
                        'missing_pattern': 'scattered' if missing_count < len(df) * 0.9 else 'mostly_missing'
                    }
            
            # Missing values per dataset_id (if available)
            if 'dataset_id' in df.columns:
                for dataset_id in df['dataset_id'].unique():
                    subset = df[df['dataset_id'] == dataset_id]
                    subset_missing = subset.isnull().sum().sum()
                    analysis['missing_values']['missing_per_dataset'][dataset_id] = {
                        'count': int(subset_missing),
                        'percentage': round((subset_missing / (len(subset) * len(subset.columns))) * 100, 4)
                    }
            
            # Infinity values analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            analysis['infinity_values'] = {
                'total_infinity': 0,
                'columns_with_infinity': {},
                'infinity_per_dataset': {}
            }
            
            total_inf = 0
            for col in numeric_cols:
                inf_count = np.isinf(df[col]).sum()
                pos_inf_count = np.isposinf(df[col]).sum()
                neg_inf_count = np.isneginf(df[col]).sum()
                
                if inf_count > 0:
                    total_inf += inf_count
                    analysis['infinity_values']['columns_with_infinity'][col] = {
                        'total_count': int(inf_count),
                        'positive_infinity': int(pos_inf_count),
                        'negative_infinity': int(neg_inf_count),
                        'percentage': round((inf_count / len(df)) * 100, 4),
                        'data_type': str(df[col].dtype),
                        'finite_count': int(np.isfinite(df[col]).sum()),
                        'finite_min': float(df[col][np.isfinite(df[col])].min()) if np.isfinite(df[col]).any() else None,
                        'finite_max': float(df[col][np.isfinite(df[col])].max()) if np.isfinite(df[col]).any() else None
                    }
            
            analysis['infinity_values']['total_infinity'] = int(total_inf)
            
            # Infinity values per dataset_id
            if 'dataset_id' in df.columns:
                for dataset_id in df['dataset_id'].unique():
                    subset = df[df['dataset_id'] == dataset_id]
                    subset_inf = 0
                    for col in numeric_cols:
                        if col in subset.columns:
                            subset_inf += np.isinf(subset[col]).sum()
                    analysis['infinity_values']['infinity_per_dataset'][dataset_id] = int(subset_inf)
            
            # Duplicate rows analysis
            duplicates = df.duplicated().sum()
            analysis['duplicate_rows'] = {
                'count': int(duplicates),
                'percentage': round((duplicates / len(df)) * 100, 4)
            }
            
            # Cross-dataset duplicate analysis
            if 'dataset_id' in df.columns:
                # Check for identical records across different datasets
                df_no_id = df.drop('dataset_id', axis=1)
                cross_duplicates = df_no_id.duplicated().sum()
                analysis['cross_dataset_duplicates'] = {
                    'count': int(cross_duplicates),
                    'percentage': round((cross_duplicates / len(df)) * 100, 4)
                }
            
            # Detailed numeric columns statistics
            analysis['numeric_stats'] = {}
            for col in numeric_cols:
                if col in df.columns and col != 'dataset_id':  # Skip dataset_id for numeric stats
                    finite_values = df[col][np.isfinite(df[col])]
                    
                    col_stats = {
                        'data_type': str(df[col].dtype),
                        'total_count': int(len(df[col])),
                        'finite_count': int(len(finite_values)),
                        'missing_count': int(df[col].isnull().sum()),
                        'infinity_count': int(np.isinf(df[col]).sum()),
                        'positive_infinity': int(np.isposinf(df[col]).sum()),
                        'negative_infinity': int(np.isneginf(df[col]).sum()),
                        'min': float(finite_values.min()) if not finite_values.empty else None,
                        'max': float(finite_values.max()) if not finite_values.empty else None,
                        'mean': float(finite_values.mean()) if not finite_values.empty else None,
                        'median': float(finite_values.median()) if not finite_values.empty else None,
                        'std': float(finite_values.std()) if not finite_values.empty else None,
                        'zeros': int((df[col] == 0).sum()),
                        'negatives': int((finite_values < 0).sum()),
                        'positives': int((finite_values > 0).sum()),
                        'unique_values': int(df[col].nunique()),
                        'finite_unique_values': int(finite_values.nunique()),
                        'outliers_iqr': 0,  # Will calculate below
                        'extreme_outliers_iqr': 0,  # 3*IQR outliers
                        'percentiles': {}
                    }
                    
                    # Calculate percentiles for finite values
                    if not finite_values.empty:
                        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
                        for p in percentiles:
                            col_stats['percentiles'][f'p{p}'] = float(finite_values.quantile(p/100))
                    
                    # Calculate IQR outliers (both standard and extreme)
                    if not finite_values.empty and len(finite_values) > 4:
                        Q1 = finite_values.quantile(0.25)
                        Q3 = finite_values.quantile(0.75)
                        IQR = Q3 - Q1
                        if IQR > 0:
                            # Standard outliers (1.5 * IQR)
                            outliers = ((finite_values < (Q1 - 1.5 * IQR)) | (finite_values > (Q3 + 1.5 * IQR))).sum()
                            col_stats['outliers_iqr'] = int(outliers)
                            
                            # Extreme outliers (3 * IQR)
                            extreme_outliers = ((finite_values < (Q1 - 3 * IQR)) | (finite_values > (Q3 + 3 * IQR))).sum()
                            col_stats['extreme_outliers_iqr'] = int(extreme_outliers)
                            
                            col_stats['iqr'] = float(IQR)
                            col_stats['lower_fence'] = float(Q1 - 1.5 * IQR)
                            col_stats['upper_fence'] = float(Q3 + 1.5 * IQR)
                    
                    # Value range analysis
                    if not finite_values.empty:
                        col_stats['range'] = float(finite_values.max() - finite_values.min())
                        col_stats['coefficient_of_variation'] = float(finite_values.std() / finite_values.mean()) if finite_values.mean() != 0 else float('inf')
                    
                    analysis['numeric_stats'][col] = col_stats
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            analysis['categorical_stats'] = {}
            for col in categorical_cols:
                if col in df.columns:
                    value_counts = df[col].value_counts()
                    analysis['categorical_stats'][col] = {
                        'unique_values': int(df[col].nunique()),
                        'most_common': value_counts.head(10).to_dict(),
                        'empty_strings': int((df[col] == '').sum()),
                        'whitespace_only': int(df[col].str.strip().eq('').sum()) if df[col].dtype == 'object' else 0,
                        'null_as_string': int((df[col] == 'null').sum() + (df[col] == 'NULL').sum() + (df[col] == 'None').sum())
                    }
            
            # Label analysis (multiple possible label columns)
            label_columns = ['Label_multi', 'Label_binary', 'label', 'attack_type']
            analysis['label_analysis'] = {}
            
            for label_col in label_columns:
                if label_col in df.columns:
                    label_dist = df[label_col].value_counts().to_dict()
                    analysis['label_analysis'][label_col] = {
                        'distribution': label_dist,
                        'unique_labels': len(label_dist),
                        'most_common_label': max(label_dist, key=label_dist.get),
                        'label_balance': min(label_dist.values()) / max(label_dist.values()) if label_dist else 0
                    }
                    
                    # Label distribution per dataset
                    if 'dataset_id' in df.columns:
                        label_per_dataset = {}
                        for dataset_id in df['dataset_id'].unique():
                            subset_labels = df[df['dataset_id'] == dataset_id][label_col].value_counts().to_dict()
                            label_per_dataset[dataset_id] = subset_labels
                        analysis['label_analysis'][label_col]['per_dataset'] = label_per_dataset
            
            # Timestamp analysis
            timestamp_columns = ['timestamp']
            analysis['timestamp_analysis'] = {}
            
            for ts_col in timestamp_columns:
                if ts_col in df.columns:
                    analysis['timestamp_analysis'][ts_col] = {
                        'min_timestamp': str(df[ts_col].min()),
                        'max_timestamp': str(df[ts_col].max()),
                        'timestamp_format': 'numeric' if pd.api.types.is_numeric_dtype(df[ts_col]) else 'string',
                        'timestamp_range_hours': 0,
                        'gaps_detected': False
                    }
                    
                    # Calculate time range
                    if pd.api.types.is_numeric_dtype(df[ts_col]):
                        time_range = df[ts_col].max() - df[ts_col].min()
                        analysis['timestamp_analysis'][ts_col]['timestamp_range_hours'] = round(time_range / 3600, 2)
                        
                        # Check for gaps (simplified)
                        time_diffs = df[ts_col].diff().dropna()
                        median_diff = time_diffs.median()
                        large_gaps = (time_diffs > median_diff * 10).sum()
                        analysis['timestamp_analysis'][ts_col]['gaps_detected'] = large_gaps > 0
                        analysis['timestamp_analysis'][ts_col]['large_gaps_count'] = int(large_gaps)
            
            # Memory and performance analysis
            analysis['performance_metrics'] = {
                'load_time_estimate': 'fast' if analysis['file_size_mb'] < 100 else 'medium' if analysis['file_size_mb'] < 500 else 'slow',
                'memory_efficiency': round((analysis['memory_usage_mb'] / analysis['file_size_mb']), 2) if analysis['file_size_mb'] > 0 else 0,
                'recommended_chunk_size': max(1000, min(100000, int(analysis['rows'] / 100))) if analysis['rows'] > 0 else 1000
            }
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'dataset_type': dataset_type,
                'error': str(e),
                'status': 'failed'
            }
    
    def investigate_combined_datasets(self):
        """Investigate all combined CSV datasets"""
        for csv_file in self.combined_files:
            csv_path = self.base_path / csv_file
            dataset_type = csv_file.replace('_dataset.csv', '').replace('.csv', '')
            
            if csv_path.exists():
                self.logger.info(f"Found {csv_file}")
                analysis = self.analyze_combined_dataset(csv_path, dataset_type)
                self.results[dataset_type] = analysis
            else:
                self.logger.warning(f"Missing {csv_file}")
                self.results[dataset_type] = {
                    'file_path': str(csv_path),
                    'dataset_type': dataset_type,
                    'status': 'missing'
                }
    
    def generate_summary_statistics(self):
        """Generate overall summary statistics for combined datasets"""
        total_files = len(self.combined_files)
        successful_files = 0
        total_rows = 0
        total_size_mb = 0
        total_missing = 0
        total_infinity = 0
        total_duplicates = 0
        
        dataset_consistency = {
            'dataset_ids_consistent': True,
            'common_datasets': set(),
            'inconsistent_datasets': []
        }
        
        all_dataset_ids = []
        
        for dataset_type, analysis in self.results.items():
            if 'error' not in analysis and 'status' not in analysis:
                successful_files += 1
                total_rows += analysis.get('rows', 0)
                total_size_mb += analysis.get('file_size_mb', 0)
                total_missing += analysis.get('missing_values', {}).get('total_missing', 0)
                total_infinity += analysis.get('infinity_values', {}).get('total_infinity', 0)
                total_duplicates += analysis.get('duplicate_rows', {}).get('count', 0)
                
                # Collect dataset IDs for consistency check
                if 'dataset_distribution' in analysis:
                    dataset_ids = set(analysis['dataset_distribution']['unique_datasets'])
                    all_dataset_ids.append((dataset_type, dataset_ids))
                    if not dataset_consistency['common_datasets']:
                        dataset_consistency['common_datasets'] = dataset_ids
                    else:
                        if dataset_ids != dataset_consistency['common_datasets']:
                            dataset_consistency['dataset_ids_consistent'] = False
                            dataset_consistency['inconsistent_datasets'].append(dataset_type)
        
        # Convert set to list for JSON serialization
        dataset_consistency['common_datasets'] = list(dataset_consistency['common_datasets'])
        
        self.summary_stats = {
            'total_files': total_files,
            'successful_files': successful_files,
            'missing_files': total_files - successful_files,
            'success_rate': round((successful_files / total_files * 100), 2) if total_files > 0 else 0,
            'total_rows': total_rows,
            'total_size_mb': round(total_size_mb, 2),
            'total_missing_values': total_missing,
            'total_infinity_values': total_infinity,
            'total_duplicate_rows': total_duplicates,
            'dataset_consistency': dataset_consistency,
            'data_integrity_score': self.calculate_integrity_score()
        }
    
    def calculate_integrity_score(self):
        """Calculate overall data integrity score (0-100)"""
        score = 100
        
        # Penalize missing files
        if self.summary_stats.get('missing_files', 0) > 0:
            score -= (self.summary_stats['missing_files'] / len(self.combined_files)) * 30
        
        # Penalize missing values
        total_cells = sum(r.get('rows', 0) * r.get('columns', 0) for r in self.results.values() if 'rows' in r)
        if total_cells > 0:
            missing_rate = self.summary_stats.get('total_missing_values', 0) / total_cells
            score -= missing_rate * 25
        
        # Penalize infinity values
        if self.summary_stats.get('total_infinity_values', 0) > 0:
            score -= min(15, (self.summary_stats['total_infinity_values'] / 1000))
        
        # Penalize dataset inconsistency
        if not self.summary_stats.get('dataset_consistency', {}).get('dataset_ids_consistent', True):
            score -= 20
        
        # Penalize excessive duplicates
        duplicate_rate = self.summary_stats.get('total_duplicate_rows', 0) / max(1, self.summary_stats.get('total_rows', 1))
        if duplicate_rate > 0.01:  # More than 1% duplicates
            score -= duplicate_rate * 10
        
        return max(0, round(score, 2))
    
    def generate_report(self):
        """Generate comprehensive data quality report for combined datasets"""
        report = []
        report.append("# Combined Datasets Quality Investigation Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        integrity_score = self.summary_stats.get('data_integrity_score', 0)
        if integrity_score >= 90:
            status = "EXCELLENT ✅"
        elif integrity_score >= 75:
            status = "GOOD ✅"
        elif integrity_score >= 60:
            status = "ACCEPTABLE ⚠️"
        else:
            status = "POOR ❌"
        
        report.append(f"- **Data Integrity Score**: {integrity_score}/100 ({status})")
        report.append(f"- **Files Processed**: {self.summary_stats['successful_files']}/{self.summary_stats['total_files']} ({self.summary_stats['success_rate']}%)")
        report.append(f"- **Total Records**: {self.summary_stats['total_rows']:,}")
        report.append(f"- **Total Size**: {self.summary_stats['total_size_mb']:.1f} MB")
        report.append(f"- **Dataset ID Consistency**: {'✅ Consistent' if self.summary_stats['dataset_consistency']['dataset_ids_consistent'] else '❌ Inconsistent'}")
        report.append("")
        
        # Quick Quality Check
        report.append("## Quick Quality Check")
        issues = []
        if self.summary_stats['total_missing_values'] > 0:
            issues.append(f"Missing values: {self.summary_stats['total_missing_values']:,}")
        if self.summary_stats['total_infinity_values'] > 0:
            issues.append(f"Infinity values: {self.summary_stats['total_infinity_values']:,}")
        if self.summary_stats['total_duplicate_rows'] > 1000:
            issues.append(f"Duplicate rows: {self.summary_stats['total_duplicate_rows']:,}")
        
        if issues:
            report.append("### Issues Detected:")
            for issue in issues:
                report.append(f"- ⚠️ {issue}")
        else:
            report.append("### ✅ No Major Issues Detected")
        report.append("")
        
        # Dataset-specific analysis
        report.append("## Dataset-Specific Analysis")
        
        for dataset_type, analysis in self.results.items():
            report.append(f"### {dataset_type.upper()} Dataset")
            
            if 'error' in analysis:
                report.append(f"❌ **ERROR**: {analysis['error']}")
            elif 'status' in analysis and analysis['status'] == 'missing':
                report.append("❌ **FILE MISSING**")
            else:
                # Basic metrics
                report.append(f"- **File**: {analysis['file_path']}")
                report.append(f"- **Size**: {analysis['file_size_mb']:.1f} MB")
                report.append(f"- **Records**: {analysis['rows']:,}")
                report.append(f"- **Features**: {analysis['columns']} columns")
                report.append(f"- **Memory Usage**: {analysis['memory_usage_mb']:.1f} MB")
                
                # Dataset distribution
                if 'dataset_distribution' in analysis:
                    dist = analysis['dataset_distribution']
                    report.append(f"- **Source Datasets**: {dist['total_datasets']} datasets")
                    report.append(f"- **Records per Dataset**: {dist['min_records']:,} - {dist['max_records']:,} (avg: {dist['mean_records']:,.0f})")
                    
                    balance = analysis.get('dataset_balance', {})
                    if balance.get('is_balanced', False):
                        report.append("- **Distribution**: ✅ Well balanced")
                    else:
                        report.append(f"- **Distribution**: ⚠️ Imbalanced (ratio: {balance.get('imbalance_ratio', 'N/A')})")
                
                # Data quality metrics
                quality_items = []
                
                missing = analysis.get('missing_values', {})
                if missing.get('total_missing', 0) > 0:
                    quality_items.append(f"Missing: {missing['total_missing']:,} ({missing['missing_percentage']:.2f}%)")
                
                infinity = analysis.get('infinity_values', {})
                if infinity.get('total_infinity', 0) > 0:
                    quality_items.append(f"Infinity: {infinity['total_infinity']:,}")
                
                duplicates = analysis.get('duplicate_rows', {})
                if duplicates.get('count', 0) > 0:
                    quality_items.append(f"Duplicates: {duplicates['count']:,} ({duplicates['percentage']:.2f}%)")
                
                if quality_items:
                    report.append(f"- **Quality Issues**: {', '.join(quality_items)}")
                else:
                    report.append("- **Quality Issues**: None detected ✅")
                
                # Detailed Missing Values Analysis
                missing_cols = missing.get('columns_with_missing', {})
                if missing_cols:
                    report.append("#### 🔍 Detailed Missing Values Analysis")
                    report.append("| Column | Missing Count | % Missing | Data Type | Pattern |")
                    report.append("|--------|---------------|-----------|-----------|---------|")
                    
                    sorted_missing = sorted(missing_cols.items(), key=lambda x: x[1]['percentage'], reverse=True)
                    for col, info in sorted_missing:
                        report.append(f"| {col} | {info['count']:,} | {info['percentage']:.2f}% | {info['data_type']} | {info['missing_pattern']} |")
                
                # Detailed Infinity Values Analysis
                inf_cols = infinity.get('columns_with_infinity', {})
                if inf_cols:
                    report.append("#### ♾️ Detailed Infinity Values Analysis")
                    report.append("| Column | Total Inf | +Inf | -Inf | % Inf | Data Type | Finite Range |")
                    report.append("|--------|-----------|------|------|-------|-----------|-------------|")
                    
                    for col, info in inf_cols.items():
                        finite_range = f"{info['finite_min']:.2e} to {info['finite_max']:.2e}" if info['finite_min'] is not None else "N/A"
                        report.append(f"| {col} | {info['total_count']:,} | {info['positive_infinity']:,} | {info['negative_infinity']:,} | {info['percentage']:.2f}% | {info['data_type']} | {finite_range} |")
                
                # Detailed Numeric Statistics for problematic columns
                numeric_stats = analysis.get('numeric_stats', {})
                if numeric_stats:
                    problematic_cols = []
                    for col, stats in numeric_stats.items():
                        if (stats.get('missing_count', 0) > 0 or 
                            stats.get('infinity_count', 0) > 0 or 
                            stats.get('outliers_iqr', 0) > analysis.get('rows', 0) * 0.05):  # More than 5% outliers
                            problematic_cols.append((col, stats))
                    
                    if problematic_cols:
                        report.append("#### 📊 Detailed Statistics for Problematic Columns")
                        
                        for col, stats in problematic_cols[:10]:  # Limit to top 10 most problematic
                            report.append(f"**{col}** ({stats['data_type']}):")
                            report.append(f"- Total: {stats['total_count']:,}, Finite: {stats['finite_count']:,}, Missing: {stats['missing_count']:,}, Infinity: {stats['infinity_count']:,}")
                            
                            if stats['finite_count'] > 0:
                                report.append(f"- Range: {stats['min']:.2e} to {stats['max']:.2e}")
                                report.append(f"- Mean: {stats['mean']:.2e}, Median: {stats['median']:.2e}, Std: {stats['std']:.2e}")
                                report.append(f"- Zeros: {stats['zeros']:,}, Negatives: {stats['negatives']:,}")
                                
                                if stats.get('outliers_iqr', 0) > 0:
                                    outlier_pct = (stats['outliers_iqr'] / stats['total_count']) * 100
                                    report.append(f"- Outliers (IQR): {stats['outliers_iqr']:,} ({outlier_pct:.1f}%)")
                                    
                                    if 'lower_fence' in stats and 'upper_fence' in stats:
                                        report.append(f"- Outlier fences: {stats['lower_fence']:.2e} to {stats['upper_fence']:.2e}")
                                
                                # Show key percentiles
                                if 'percentiles' in stats and stats['percentiles']:
                                    p1, p5, p95, p99 = stats['percentiles'].get('p1', 0), stats['percentiles'].get('p5', 0), stats['percentiles'].get('p95', 0), stats['percentiles'].get('p99', 0)
                                    report.append(f"- Percentiles: P1={p1:.2e}, P5={p5:.2e}, P95={p95:.2e}, P99={p99:.2e}")
                            
                            report.append("")
                
                # Label analysis
                label_analysis = analysis.get('label_analysis', {})
                if label_analysis:
                    report.append("#### 🏷️ Label Distribution Analysis")
                    for label_col, info in label_analysis.items():
                        total_labels = sum(info['distribution'].values())
                        report.append(f"**{label_col}**: {info['unique_labels']} classes, {total_labels:,} records")
                        
                        # Show all labels with counts and percentages
                        sorted_labels = sorted(info['distribution'].items(), key=lambda x: x[1], reverse=True)
                        for label, count in sorted_labels:
                            pct = (count / total_labels) * 100
                            report.append(f"- {label}: {count:,} ({pct:.1f}%)")
                        report.append("")
                
                # Performance metrics
                perf = analysis.get('performance_metrics', {})
                if perf:
                    report.append(f"- **Performance**: {perf['load_time_estimate'].title()} loading, Memory efficiency: {perf['memory_efficiency']:.1f}")
            
            report.append("")
        
        # Cross-dataset consistency analysis
        report.append("## Cross-Dataset Consistency")
        consistency = self.summary_stats['dataset_consistency']
        
        if consistency['dataset_ids_consistent']:
            report.append("✅ **All datasets contain the same source dataset IDs**")
            report.append(f"- Common dataset IDs: {', '.join(sorted(consistency['common_datasets']))}")
        else:
            report.append("❌ **Dataset ID inconsistency detected**")
            report.append(f"- Expected dataset IDs: {', '.join(sorted(consistency['common_datasets']))}")
            report.append(f"- Inconsistent files: {', '.join(consistency['inconsistent_datasets'])}")
        
        report.append("")
        
        # Data Cleaning Recommendations
        report.append("## 🧹 Detailed Data Cleaning Recommendations")
        
        # Missing values strategy
        if self.summary_stats['total_missing_values'] > 0:
            report.append("### Missing Values Treatment")
            
            for dataset_type, analysis in self.results.items():
                missing_cols = analysis.get('missing_values', {}).get('columns_with_missing', {})
                if missing_cols:
                    report.append(f"#### {dataset_type.upper()} Dataset:")
                    
                    for col, info in sorted(missing_cols.items(), key=lambda x: x[1]['percentage'], reverse=True):
                        missing_pct = info['percentage']
                        data_type = info['data_type']
                        
                        if missing_pct > 90:
                            report.append(f"- **{col}** ({missing_pct:.1f}% missing): **DROP COLUMN** - Too sparse for reliable imputation")
                        elif missing_pct > 50:
                            report.append(f"- **{col}** ({missing_pct:.1f}% missing): Consider dropping or use advanced imputation (e.g., iterative)")
                        elif missing_pct > 20:
                            if 'float' in data_type.lower() or 'int' in data_type.lower():
                                report.append(f"- **{col}** ({missing_pct:.1f}% missing): Use median/mean imputation or advanced techniques")
                            else:
                                report.append(f"- **{col}** ({missing_pct:.1f}% missing): Use mode imputation or 'unknown' category")
                        elif missing_pct > 5:
                            if 'float' in data_type.lower() or 'int' in data_type.lower():
                                report.append(f"- **{col}** ({missing_pct:.1f}% missing): Safe for median/mean imputation")
                            else:
                                report.append(f"- **{col}** ({missing_pct:.1f}% missing): Use forward-fill or mode imputation")
                        else:
                            report.append(f"- **{col}** ({missing_pct:.1f}% missing): Simple interpolation or deletion of missing rows")
            report.append("")
        
        # Infinity values strategy
        if self.summary_stats['total_infinity_values'] > 0:
            report.append("### Infinity Values Treatment")
            
            for dataset_type, analysis in self.results.items():
                inf_cols = analysis.get('infinity_values', {}).get('columns_with_infinity', {})
                if inf_cols:
                    report.append(f"#### {dataset_type.upper()} Dataset:")
                    
                    for col, info in inf_cols.items():
                        total_inf = info['total_count']
                        pos_inf = info['positive_infinity']
                        neg_inf = info['negative_infinity']
                        finite_min = info.get('finite_min')
                        finite_max = info.get('finite_max')
                        
                        report.append(f"- **{col}** ({total_inf:,} infinity values):")
                        
                        if pos_inf > 0:
                            if finite_max is not None:
                                report.append(f"  - Replace +Inf ({pos_inf:,} values) with {finite_max:.2e} (finite max) or clip to 99th percentile")
                            else:
                                report.append(f"  - Replace +Inf ({pos_inf:,} values) with large finite value (e.g., 1e10)")
                        
                        if neg_inf > 0:
                            if finite_min is not None:
                                report.append(f"  - Replace -Inf ({neg_inf:,} values) with {finite_min:.2e} (finite min) or clip to 1st percentile")
                            else:
                                report.append(f"  - Replace -Inf ({neg_inf:,} values) with large negative value (e.g., -1e10)")
                        
                        report.append(f"  - **Alternative**: Convert to NaN and apply missing value strategy")
            report.append("")
        
        # Outliers strategy
        report.append("### Outlier Treatment")
        for dataset_type, analysis in self.results.items():
            numeric_stats = analysis.get('numeric_stats', {})
            outlier_cols = []
            
            for col, stats in numeric_stats.items():
                outliers = stats.get('outliers_iqr', 0)
                extreme_outliers = stats.get('extreme_outliers_iqr', 0)
                total_count = stats.get('total_count', 1)
                
                if outliers > total_count * 0.05:  # More than 5% outliers
                    outlier_cols.append((col, stats))
            
            if outlier_cols:
                report.append(f"#### {dataset_type.upper()} Dataset:")
                
                for col, stats in outlier_cols[:5]:  # Top 5 most problematic
                    outlier_pct = (stats['outliers_iqr'] / stats['total_count']) * 100
                    extreme_pct = (stats['extreme_outliers_iqr'] / stats['total_count']) * 100
                    
                    report.append(f"- **{col}** ({outlier_pct:.1f}% outliers, {extreme_pct:.1f}% extreme):")
                    
                    if extreme_pct > 1:
                        report.append(f"  - **Action**: Cap extreme outliers at 3×IQR boundaries")
                    if outlier_pct > 10:
                        report.append(f"  - **Action**: Apply log transformation or robust scaling")
                    elif outlier_pct > 5:
                        report.append(f"  - **Action**: Use robust statistics (median, IQR) for normalization")
                    else:
                        report.append(f"  - **Action**: Standard z-score normalization acceptable")
                    
                    if 'lower_fence' in stats and 'upper_fence' in stats:
                        report.append(f"  - **Clipping bounds**: [{stats['lower_fence']:.2e}, {stats['upper_fence']:.2e}]")
        report.append("")
        
        # Specific cleaning strategies per dataset
        report.append("### Dataset-Specific Cleaning Strategies")
        
        for dataset_type, analysis in self.results.items():
            report.append(f"#### {dataset_type.upper()} Dataset Cleaning Plan:")
            
            missing_count = analysis.get('missing_values', {}).get('total_missing', 0)
            inf_count = analysis.get('infinity_values', {}).get('total_infinity', 0)
            duplicate_count = analysis.get('duplicate_rows', {}).get('count', 0)
            
            cleaning_steps = []
            
            if duplicate_count > 0:
                cleaning_steps.append(f"1. **Remove duplicates**: Drop {duplicate_count:,} duplicate rows")
            
            if inf_count > 0:
                cleaning_steps.append(f"2. **Handle infinity**: Replace {inf_count:,} infinity values using strategies above")
            
            if missing_count > 0:
                cleaning_steps.append(f"3. **Impute missing**: Apply appropriate imputation for {missing_count:,} missing values")
            
            # Add dataset-specific recommendations
            if dataset_type == 'flow':
                cleaning_steps.append("4. **Flow-specific**: Consider time-based interpolation for flow statistics")
                cleaning_steps.append("5. **Feature engineering**: Create flow duration and rate features from existing data")
            elif dataset_type == 'packet':
                cleaning_steps.append("4. **Packet-specific**: Validate timestamp sequences and packet ordering")
                cleaning_steps.append("5. **Network validation**: Check for impossible protocol combinations")
            elif dataset_type == 'cicflow':
                cleaning_steps.append("4. **CICFlow-specific**: Many features are derived - verify calculation consistency")
                cleaning_steps.append("5. **Feature selection**: Consider removing highly correlated CICFlow features")
            
            cleaning_steps.append("6. **Normalization**: Apply appropriate scaling based on outlier analysis")
            cleaning_steps.append("7. **Validation**: Cross-check cleaned data maintains attack patterns")
            
            for step in cleaning_steps:
                report.append(f"   {step}")
            
            report.append("")
        
        # Python code templates
        report.append("### 🐍 Python Code Templates for Data Cleaning")
        
        report.append("#### Missing Values Imputation")
        report.append("```python")
        report.append("import pandas as pd")
        report.append("from sklearn.impute import SimpleImputer, IterativeImputer")
        report.append("")
        report.append("# For columns with <20% missing - simple imputation")
        report.append("numeric_imputer = SimpleImputer(strategy='median')")
        report.append("categorical_imputer = SimpleImputer(strategy='most_frequent')")
        report.append("")
        report.append("# For columns with 20-50% missing - advanced imputation")
        report.append("advanced_imputer = IterativeImputer(random_state=42)")
        report.append("")
        report.append("# For columns with >50% missing - consider dropping")
        report.append("high_missing_cols = df.isnull().sum()[df.isnull().sum() > len(df) * 0.5].index")
        report.append("df_cleaned = df.drop(columns=high_missing_cols)")
        report.append("```")
        report.append("")
        
        report.append("#### Infinity Values Replacement")
        report.append("```python")
        report.append("import numpy as np")
        report.append("")
        report.append("def replace_infinity(df, strategy='percentile'):")
        report.append("    df_clean = df.copy()")
        report.append("    for col in df.select_dtypes(include=[np.number]).columns:")
        report.append("        if np.isinf(df[col]).any():")
        report.append("            if strategy == 'percentile':")
        report.append("                finite_vals = df[col][np.isfinite(df[col])]")
        report.append("                p99 = finite_vals.quantile(0.99)")
        report.append("                p1 = finite_vals.quantile(0.01)")
        report.append("                df_clean[col] = df[col].replace([np.inf, -np.inf], [p99, p1])")
        report.append("            elif strategy == 'nan':")
        report.append("                df_clean[col] = df[col].replace([np.inf, -np.inf], np.nan)")
        report.append("    return df_clean")
        report.append("```")
        report.append("")
        
        report.append("#### Outlier Treatment")
        report.append("```python")
        report.append("def cap_outliers_iqr(df, multiplier=1.5):")
        report.append("    df_clean = df.copy()")
        report.append("    for col in df.select_dtypes(include=[np.number]).columns:")
        report.append("        Q1 = df[col].quantile(0.25)")
        report.append("        Q3 = df[col].quantile(0.75)")
        report.append("        IQR = Q3 - Q1")
        report.append("        lower_bound = Q1 - multiplier * IQR")
        report.append("        upper_bound = Q3 + multiplier * IQR")
        report.append("        df_clean[col] = df[col].clip(lower=lower_bound, upper=upper_bound)")
        report.append("    return df_clean")
        report.append("```")
        report.append("")
        
        # General recommendations
        report.append("## General ML Preparation Recommendations")
        
        if integrity_score >= 90:
            report.append("### ✅ Excellent Data Quality")
            report.append("- Data is ready for ML training with minimal preprocessing")
            report.append("- Focus on feature engineering and normalization")
            report.append("- Implement automated quality monitoring")
        elif integrity_score >= 75:
            report.append("### ✅ Good Data Quality")
            report.append("- Apply cleaning strategies above before ML training")
            report.append("- Validate cleaning preserves attack patterns")
            report.append("- Consider feature selection to reduce dimensionality")
        else:
            report.append("### ⚠️ Data Quality Issues Require Attention")
            report.append("- **Mandatory**: Apply all cleaning strategies above")
            report.append("- **Validation**: Extensive testing after cleaning")
            report.append("- **Monitoring**: Implement data quality checks in pipeline")
        
        report.append("")
        report.append("### ML Pipeline Steps:")
        report.append("1. **Data Cleaning**: Apply strategies above based on column-specific analysis")
        report.append("2. **Feature Engineering**: Create temporal and behavioral features from network data")
        report.append("3. **Data Splitting**: Use dataset_id for temporal/cross-dataset validation")
        report.append("4. **Preprocessing**: Apply scaling after cleaning to avoid leakage")
        report.append("5. **Validation**: Ensure attack patterns remain detectable after preprocessing")
        report.append("6. **Monitoring**: Implement drift detection for production deployment")
        
        return "\n".join(report)
    
    def save_results(self, output_dir):
        """Save results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save detailed JSON results
        with open(output_path / 'combined_datasets_quality_analysis.json', 'w') as f:
            json.dump({
                'summary': self.summary_stats,
                'detailed_results': self.results,
                'analysis_timestamp': datetime.now().isoformat()
            }, f, indent=2, cls=NumpyEncoder)
        
        # Save report
        report = self.generate_report()
        with open(output_path / 'combined_datasets_quality_report.md', 'w') as f:
            f.write(report)
        
        self.logger.info(f"Results saved to {output_path}")
        return report

def main():
    parser = argparse.ArgumentParser(description='Investigate quality of combined CSV datasets')
    parser.add_argument('--path', default='../main_output/v2_main', 
                       help='Path to dataset directory (default: ../main_output/v2_main)')
    args = parser.parse_args()
    
    base_path = Path(args.path)
    if not base_path.exists():
        print(f"❌ Error: Dataset path not found: {base_path}")
        return 1
    
    # Set up logging with path to dataset directory
    log_path = base_path / "investigate_csv_quality.log"
    logger = setup_logging(log_path)
    
    investigator = CombinedDatasetInvestigator(base_path)
    
    logger.info("Starting combined datasets quality investigation...")
    investigator.investigate_combined_datasets()
    
    logger.info("Generating summary statistics...")
    investigator.generate_summary_statistics()
    
    logger.info("Generating comprehensive report...")
    report = investigator.save_results(base_path)
    
    logger.info("\n" + "="*60)
    logger.info("COMBINED DATASETS INVESTIGATION COMPLETE")
    logger.info("="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())