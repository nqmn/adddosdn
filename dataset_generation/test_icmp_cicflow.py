#!/usr/bin/env python3
"""
Test script to debug CICFlowMeter processing of ICMP traffic
"""

import subprocess
import pandas as pd
from pathlib import Path

def test_cicflowmeter_icmp():
    """Test CICFlowMeter processing of ICMP PCAP"""
    
    pcap_file = "test_output/icmp_flood.pcap"
    output_file = "icmp_test_output.csv"
    
    print(f"Testing CICFlowMeter on {pcap_file}")
    
    # Run CICFlowMeter
    try:
        cmd = ['cicflowmeter', '-f', pcap_file, '-c', output_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Check if output file was created
        output_path = Path(output_file)
        if output_path.exists():
            print(f"Output file created: {output_file}")
            
            # Try to read the CSV
            try:
                df = pd.read_csv(output_file)
                print(f"Rows in output: {len(df)}")
                print(f"Columns in output: {len(df.columns)}")
                if len(df) > 0:
                    print("First few rows:")
                    print(df.head())
                else:
                    print("CSV file is empty (no flows extracted)")
            except Exception as e:
                print(f"Error reading CSV: {e}")
                # Try to read as text to see what's in the file
                try:
                    with open(output_file, 'r') as f:
                        content = f.read()
                    print(f"Raw file content:\n{content}")
                except Exception as e2:
                    print(f"Error reading raw file: {e2}")
        else:
            print("No output file created")
            
    except subprocess.TimeoutExpired:
        print("CICFlowMeter timed out")
    except FileNotFoundError:
        print("CICFlowMeter not found in PATH")
    except Exception as e:
        print(f"Error running CICFlowMeter: {e}")

if __name__ == "__main__":
    test_cicflowmeter_icmp()