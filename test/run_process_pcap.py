from src.utils.process_pcap_to_csv import process_pcap_to_csv

pcap_file = "output/capture.pcap"
output_csv_file = "output/temp_labeled_packet_features.csv"

# Call the function without a label_timeline for this test
process_pcap_to_csv(pcap_file, output_csv_file)