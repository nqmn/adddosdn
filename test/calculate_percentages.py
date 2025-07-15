import pandas as pd
import os
import argparse

def calculate_and_display_stats(file_path, column_name, group_by_column=None):
    """
    Calculates and displays the counts and percentages of unique values in a specified column of a CSV file.
    Can also group by another column to show subgroup statistics.

    Args:
        file_path (str): The path to the CSV file.
        column_name (str): The name of the column to analyze.
        group_by_column (str, optional): The column to group by. Defaults to None.
    """
    try:
        df = pd.read_csv(file_path)
        if column_name in df.columns:
            if group_by_column and group_by_column in df.columns:
                print(f"--- Statistics for {column_name} grouped by {group_by_column} in {os.path.basename(file_path)} ---")
                grouped = df.groupby([column_name, group_by_column]).size().reset_index(name='Counts')
                total_counts = df.groupby(column_name).size()
                
                # Calculate percentage
                grouped['Percentage'] = grouped.apply(lambda row: (row['Counts'] / total_counts[row[column_name]]) * 100, axis=1)
                
                for name, group in grouped.groupby(column_name):
                    print(f"\nClass: {name}")
                    print(group[[group_by_column, 'Counts', 'Percentage']].to_string(index=False))
                print("\n")
            else:
                counts = df[column_name].value_counts()
                percentages = (counts / len(df)) * 100
                
                # Create a DataFrame for a nice table format
                stats_df = pd.DataFrame({
                    'Class': counts.index,
                    'Total Packets': counts.values,
                    'Percentage': percentages.values
                })
                
                print(f"--- Statistics for {column_name} in {os.path.basename(file_path)} ---")
                print(stats_df.to_string(index=False))
                print("\n")
        else:
            print(f"Column '{column_name}' not found in {os.path.basename(file_path)}\n")
    except FileNotFoundError:
        print(f"File not found: {file_path}\n")
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}\n")

def main():
    """
    Main function to parse arguments and run the calculations.
    """
    parser = argparse.ArgumentParser(description="Calculate and display statistics for packet data.")
    parser.add_argument('output_dir', choices=['main_output', 'test_output'], 
                        help="Select the directory to process: 'main_output' or 'test_output'.")
    args = parser.parse_args()

    base_path = f"C:/Users/Intel/Desktop/InSDN_ddos_dataset/adversarial-ddos-attacks-sdn-dataset/dataset_generation/{args.output_dir}/"
    flow_features_path = os.path.join(base_path, "flow_features.csv")
    packet_features_path = os.path.join(base_path, "packet_features.csv")

    print(f"Processing files in: {base_path}\n")

    # Calculate and display stats for flow_features.csv
    calculate_and_display_stats(flow_features_path, "Label_multi")
    calculate_and_display_stats(flow_features_path, "Label_binary")

    # Calculate and display stats for packet_features.csv
    calculate_and_display_stats(packet_features_path, "Label_multi", group_by_column='ip_proto')
    calculate_and_display_stats(packet_features_path, "Label_binary", group_by_column='ip_proto')

if __name__ == "__main__":
    main()