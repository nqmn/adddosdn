import subprocess
import csv
import os
import sys
import pandas as pd

def generate_cicflow_dataset(input_pcap_file, output_csv_file, label):
    print(f"Generating CICFlowMeter dataset from {input_pcap_file} to {output_csv_file} with label '{label}'...")

    if not os.path.exists(input_pcap_file):
        print(f"Error: Input PCAP file not found at {input_pcap_file}")
        return

    temp_output_dir = "./temp_cicflow_output"
    os.makedirs(temp_output_dir, exist_ok=True)
    temp_csv_file = os.path.join(temp_output_dir, "cicflowmeter_output.csv")

    try:
        # Run cicflowmeter command
        # Assuming cicflowmeter is installed and in PATH
        # -f for pcap file, -c for output CSV
        command = ["cicflowmeter", "-f", input_pcap_file, "-c", temp_csv_file]
        print(f"Executing: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("CICFlowMeter processing complete.")

        # Read the generated CSV, add label, and save
        df = pd.read_csv(temp_csv_file)
        df['Label_multi'] = label
        df['Label_binary'] = 0 if label == 'normal' else 1
        df.to_csv(output_csv_file, index=False)
        print(f"Successfully generated dataset with {len(df.columns)} features (83 CICFlowMeter + 2 Labels).")

    except FileNotFoundError:
        print("Error: 'cicflowmeter' command not found. Please ensure CICFlowMeter is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error running CICFlowMeter: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_output_dir):
            for f in os.listdir(temp_output_dir):
                os.remove(os.path.join(temp_output_dir, f))
            os.rmdir(temp_output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_cicflow_dataset.py <input_pcap_file> <output_csv_file> <label>")
        sys.exit(1)

    input_pcap = sys.argv[1]
    output_csv = sys.argv[2]
    data_label = sys.argv[3]

    generate_cicflow_dataset(input_pcap, output_csv, data_label)
