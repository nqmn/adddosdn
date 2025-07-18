#!/usr/bin/env python3
"""
CSV Data Quality Investigation Script
Analyzes CSV files in dataset folders for preprocessing issues, missing values, 
infinity values, data types, and other quality metrics.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CSVQualityInvestigator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.results = {}
        self.summary_stats = {}
        
    def analyze_csv_file(self, file_path, dataset_name, csv_type):
        """Analyze a single CSV file for quality issues"""
        try:
            print(f"Analyzing {dataset_name}/{csv_type}...")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            analysis = {
                'file_path': str(file_path),
                'dataset': dataset_name,
                'csv_type': csv_type,
                'file_size_mb': round(file_path.stat().st_size / 1024 / 1024, 2),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
            # Data type analysis
            analysis['data_types'] = {}
            for col in df.columns:
                analysis['data_types'][col] = str(df[col].dtype)
            
            # Missing values analysis
            missing_counts = df.isnull().sum()
            analysis['missing_values'] = {
                'total_missing': int(missing_counts.sum()),
                'missing_percentage': round((missing_counts.sum() / (len(df) * len(df.columns))) * 100, 2),
                'columns_with_missing': {}
            }
            
            for col in df.columns:
                missing_count = missing_counts[col]
                if missing_count > 0:
                    analysis['missing_values']['columns_with_missing'][col] = {
                        'count': int(missing_count),
                        'percentage': round((missing_count / len(df)) * 100, 2)
                    }
            
            # Infinity values analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            analysis['infinity_values'] = {
                'total_infinity': 0,
                'columns_with_infinity': {}
            }
            
            for col in numeric_cols:
                inf_count = np.isinf(df[col]).sum()
                if inf_count > 0:
                    analysis['infinity_values']['total_infinity'] += inf_count
                    analysis['infinity_values']['columns_with_infinity'][col] = {
                        'count': int(inf_count),
                        'percentage': round((inf_count / len(df)) * 100, 2)
                    }
            
            # Duplicate rows analysis
            duplicates = df.duplicated().sum()
            analysis['duplicate_rows'] = {
                'count': int(duplicates),
                'percentage': round((duplicates / len(df)) * 100, 2)
            }
            
            # Numeric columns statistics
            analysis['numeric_stats'] = {}
            for col in numeric_cols:
                if col in df.columns:
                    col_stats = {
                        'min': float(df[col].min()) if not df[col].empty else None,
                        'max': float(df[col].max()) if not df[col].empty else None,
                        'mean': float(df[col].mean()) if not df[col].empty else None,
                        'std': float(df[col].std()) if not df[col].empty else None,
                        'zeros': int((df[col] == 0).sum()),
                        'negatives': int((df[col] < 0).sum()),
                        'unique_values': int(df[col].nunique())
                    }
                    analysis['numeric_stats'][col] = col_stats
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            analysis['categorical_stats'] = {}
            for col in categorical_cols:
                if col in df.columns:
                    value_counts = df[col].value_counts()
                    analysis['categorical_stats'][col] = {
                        'unique_values': int(df[col].nunique()),
                        'most_common': value_counts.head(5).to_dict(),
                        'empty_strings': int((df[col] == '').sum()),
                        'whitespace_only': int(df[col].str.strip().eq('').sum()) if df[col].dtype == 'object' else 0
                    }
            
            # Special checks for known columns
            if 'label' in df.columns:
                analysis['label_distribution'] = df['label'].value_counts().to_dict()
            
            if 'timestamp' in df.columns:
                analysis['timestamp_analysis'] = {
                    'min_timestamp': str(df['timestamp'].min()),
                    'max_timestamp': str(df['timestamp'].max()),
                    'timestamp_format': 'detected' if pd.api.types.is_datetime64_any_dtype(df['timestamp']) else 'string'
                }
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'dataset': dataset_name,
                'csv_type': csv_type,
                'error': str(e),
                'status': 'failed'
            }
    
    def investigate_all_datasets(self):
        """Investigate all CSV files in dataset folders"""
        dataset_folders = [d for d in self.base_path.iterdir() if d.is_dir() and d.name.startswith(('1607', '1707'))]
        
        csv_types = ['packet_features.csv', 'flow_features.csv', 'cicflow_features_all.csv']
        
        for folder in sorted(dataset_folders):
            dataset_name = folder.name
            self.results[dataset_name] = {}
            
            for csv_type in csv_types:
                csv_file = folder / csv_type
                if csv_file.exists():
                    analysis = self.analyze_csv_file(csv_file, dataset_name, csv_type)
                    self.results[dataset_name][csv_type] = analysis
                else:
                    self.results[dataset_name][csv_type] = {
                        'file_path': str(csv_file),
                        'dataset': dataset_name,
                        'csv_type': csv_type,
                        'status': 'missing'
                    }
    
    def generate_summary_statistics(self):
        """Generate overall summary statistics"""
        total_files = 0
        successful_files = 0
        total_rows = 0
        total_size_mb = 0
        total_missing = 0
        total_infinity = 0
        total_duplicates = 0
        
        csv_type_stats = {}
        
        for dataset_name, dataset_results in self.results.items():
            for csv_type, analysis in dataset_results.items():
                total_files += 1
                
                if 'error' not in analysis and 'status' not in analysis:
                    successful_files += 1
                    total_rows += analysis.get('rows', 0)
                    total_size_mb += analysis.get('file_size_mb', 0)
                    total_missing += analysis.get('missing_values', {}).get('total_missing', 0)
                    total_infinity += analysis.get('infinity_values', {}).get('total_infinity', 0)
                    total_duplicates += analysis.get('duplicate_rows', {}).get('count', 0)
                    
                    # CSV type statistics
                    if csv_type not in csv_type_stats:
                        csv_type_stats[csv_type] = {
                            'count': 0,
                            'total_rows': 0,
                            'total_size_mb': 0,
                            'avg_columns': 0
                        }
                    
                    csv_type_stats[csv_type]['count'] += 1
                    csv_type_stats[csv_type]['total_rows'] += analysis.get('rows', 0)
                    csv_type_stats[csv_type]['total_size_mb'] += analysis.get('file_size_mb', 0)
                    csv_type_stats[csv_type]['avg_columns'] += analysis.get('columns', 0)
        
        # Calculate averages
        for csv_type in csv_type_stats:
            if csv_type_stats[csv_type]['count'] > 0:
                csv_type_stats[csv_type]['avg_columns'] /= csv_type_stats[csv_type]['count']
        
        self.summary_stats = {
            'total_files': total_files,
            'successful_files': successful_files,
            'success_rate': round((successful_files / total_files * 100), 2) if total_files > 0 else 0,
            'total_rows': total_rows,
            'total_size_mb': round(total_size_mb, 2),
            'total_missing_values': total_missing,
            'total_infinity_values': total_infinity,
            'total_duplicate_rows': total_duplicates,
            'csv_type_statistics': csv_type_stats
        }
    
    def generate_report(self):
        """Generate comprehensive data quality report"""
        report = []
        report.append("# CSV Data Quality Investigation Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        report.append("## Summary Statistics")
        report.append(f"- **Total CSV files analyzed**: {self.summary_stats['total_files']}")
        report.append(f"- **Successfully processed**: {self.summary_stats['successful_files']} ({self.summary_stats['success_rate']}%)")
        report.append(f"- **Total data rows**: {self.summary_stats['total_rows']:,}")
        report.append(f"- **Total file size**: {self.summary_stats['total_size_mb']} MB")
        report.append(f"- **Total missing values**: {self.summary_stats['total_missing_values']:,}")
        report.append(f"- **Total infinity values**: {self.summary_stats['total_infinity_values']:,}")
        report.append(f"- **Total duplicate rows**: {self.summary_stats['total_duplicate_rows']:,}")
        report.append("")
        
        # CSV type breakdown
        report.append("## CSV Type Breakdown")
        for csv_type, stats in self.summary_stats['csv_type_statistics'].items():
            report.append(f"### {csv_type}")
            report.append(f"- Files: {stats['count']}")
            report.append(f"- Total rows: {stats['total_rows']:,}")
            report.append(f"- Total size: {stats['total_size_mb']:.2f} MB")
            report.append(f"- Average columns: {stats['avg_columns']:.1f}")
            report.append("")
        
        # Dataset-specific analysis
        report.append("## Dataset-Specific Analysis")
        for dataset_name, dataset_results in self.results.items():
            report.append(f"### Dataset: {dataset_name}")
            
            for csv_type, analysis in dataset_results.items():
                report.append(f"#### {csv_type}")
                
                if 'error' in analysis:
                    report.append(f"❌ **ERROR**: {analysis['error']}")
                elif 'status' in analysis and analysis['status'] == 'missing':
                    report.append("❌ **MISSING FILE**")
                else:
                    # Basic info
                    report.append(f"- **Rows**: {analysis['rows']:,}")
                    report.append(f"- **Columns**: {analysis['columns']}")
                    report.append(f"- **File size**: {analysis['file_size_mb']} MB")
                    report.append(f"- **Memory usage**: {analysis['memory_usage_mb']} MB")
                    
                    # Data quality issues
                    issues = []
                    if analysis['missing_values']['total_missing'] > 0:
                        issues.append(f"Missing values: {analysis['missing_values']['total_missing']:,} ({analysis['missing_values']['missing_percentage']}%)")
                    
                    if analysis['infinity_values']['total_infinity'] > 0:
                        issues.append(f"Infinity values: {analysis['infinity_values']['total_infinity']:,}")
                    
                    if analysis['duplicate_rows']['count'] > 0:
                        issues.append(f"Duplicates: {analysis['duplicate_rows']['count']:,} ({analysis['duplicate_rows']['percentage']}%)")
                    
                    if issues:
                        report.append(f"- **Issues**: {', '.join(issues)}")
                    else:
                        report.append("- **Issues**: None detected ✅")
                    
                    # Label distribution (if available)
                    if 'label_distribution' in analysis:
                        report.append(f"- **Label distribution**: {analysis['label_distribution']}")
                    
                    # Columns with missing values
                    if analysis['missing_values']['columns_with_missing']:
                        report.append("- **Columns with missing values**:")
                        for col, info in analysis['missing_values']['columns_with_missing'].items():
                            report.append(f"  - {col}: {info['count']} ({info['percentage']}%)")
                    
                    # Columns with infinity values
                    if analysis['infinity_values']['columns_with_infinity']:
                        report.append("- **Columns with infinity values**:")
                        for col, info in analysis['infinity_values']['columns_with_infinity'].items():
                            report.append(f"  - {col}: {info['count']} ({info['percentage']}%)")
                
                report.append("")
        
        # Data preprocessing recommendations
        report.append("## Data Preprocessing Recommendations")
        
        has_missing = self.summary_stats['total_missing_values'] > 0
        has_infinity = self.summary_stats['total_infinity_values'] > 0
        has_duplicates = self.summary_stats['total_duplicate_rows'] > 0
        
        if has_missing or has_infinity or has_duplicates:
            report.append("### Issues Found:")
            
            if has_missing:
                report.append("1. **Missing Values**: Consider imputation strategies:")
                report.append("   - Numerical columns: Mean/median imputation or forward fill")
                report.append("   - Categorical columns: Mode imputation or 'unknown' category")
                report.append("   - Time series: Forward fill or interpolation")
                report.append("")
            
            if has_infinity:
                report.append("2. **Infinity Values**: Handle infinite values:")
                report.append("   - Replace with NaN and apply missing value strategies")
                report.append("   - Use clipping to maximum finite values")
                report.append("   - Consider log transformation for highly skewed data")
                report.append("")
            
            if has_duplicates:
                report.append("3. **Duplicate Rows**: Address duplicates:")
                report.append("   - Review if duplicates are legitimate (e.g., identical packets)")
                report.append("   - Consider keeping first occurrence or aggregating")
                report.append("   - Analyze impact on temporal sequences")
                report.append("")
        else:
            report.append("✅ **No major preprocessing issues detected**")
            report.append("- All files loaded successfully")
            report.append("- No missing values found")
            report.append("- No infinity values detected")
            report.append("- Minimal duplicate rows")
            report.append("")
        
        report.append("### General Recommendations:")
        report.append("1. **Data Validation**: Implement automated data quality checks")
        report.append("2. **Feature Engineering**: Consider creating derived features from timestamps")
        report.append("3. **Normalization**: Apply scaling to numerical features for ML models")
        report.append("4. **Temporal Integrity**: Verify timestamp ordering and gaps")
        report.append("5. **Label Consistency**: Ensure consistent labeling across all datasets")
        
        return "\n".join(report)
    
    def save_results(self, output_dir):
        """Save results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save detailed JSON results
        with open(output_path / 'csv_quality_analysis.json', 'w') as f:
            json.dump({
                'summary': self.summary_stats,
                'detailed_results': self.results
            }, f, indent=2)
        
        # Save report
        report = self.generate_report()
        with open(output_path / 'csv_quality_report.md', 'w') as f:
            f.write(report)
        
        print(f"Results saved to {output_path}")
        return report

def main():
    base_path = "/mnt/c/Users/Intel/Desktop/InSDN_ddos_dataset/adversarial-ddos-attacks-sdn-dataset/dataset_generation/main_output"
    
    investigator = CSVQualityInvestigator(base_path)
    
    print("Starting CSV quality investigation...")
    investigator.investigate_all_datasets()
    
    print("Generating summary statistics...")
    investigator.generate_summary_statistics()
    
    print("Generating report...")
    report = investigator.save_results(base_path)
    
    print("\n" + "="*50)
    print("INVESTIGATION COMPLETE")
    print("="*50)
    print(report)

if __name__ == "__main__":
    main()