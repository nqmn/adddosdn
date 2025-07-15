import sys
from scapy.all import rdpcap
from pathlib import Path

# Define the absolute path to the PCAP file
# Assuming the script is run from the dataset_generation directory
BASE_DIR = Path(__file__).parent.resolve()
PCAP_FILE = BASE_DIR / "output" / "capture.pcap"

def check_timestamps(pcap_file_path):
    print(f"Checking timestamps in {pcap_file_path}...")
    if not pcap_file_path.exists():
        print(f"Error: PCAP file not found at {pcap_file_path}")
        return

    try:
        packets = rdpcap(str(pcap_file_path))
        if not packets:
            print("No packets found in the PCAP file.")
            return

        print(f"Found {len(packets)} packets. Displaying timestamps for the first 20 packets:")
        zero_timestamp_count = 0
        for i, p in enumerate(packets[:20]):
            print(f"Packet {i+1}: {p.time}")
            if p.time == 0.0:
                print(f"  WARNING: Packet {i+1} has a timestamp of 0.0")
                zero_timestamp_count += 1

        print(f"\nDisplaying timestamps for the last 20 packets:")
        for i, p in enumerate(packets[-20:]):
            print(f"Packet {len(packets) - 20 + i + 1}: {p.time}")
            if p.time == 0.0:
                print(f"  WARNING: Packet {len(packets) - 20 + i + 1} has a timestamp of 0.0")
                zero_timestamp_count += 1
        
        # Count all packets with 0.0 timestamp
        total_zero_timestamp_count = sum(1 for p in packets if p.time == 0.0)
        print(f"\nTotal packets with 0.0 timestamp: {total_zero_timestamp_count}")

    except Exception as e:
        print(f"An error occurred while reading the PCAP file: {e}")

if __name__ == "__main__":
    check_timestamps(PCAP_FILE)
