import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

def calculate_tq(ftc_file, output_path):
    print("Loading FTC clusters data...")
    # Load the FTC clusters data
    ftc_df = pd.read_csv(ftc_file, sep=';')

    tq_results = []

    # Iterate over each timestamp
    for timestamp in ftc_df['timestamp'].unique():
        print(f"Calculating TQ for timestamp {timestamp}...")
        # Filter data for this timestamp
        df_timestamp = ftc_df[ftc_df['timestamp'] == timestamp]

        # Rank FTCs based on their total length (largest to smallest)
        df_timestamp = df_timestamp.sort_values(by='total_length', ascending=False)
        df_timestamp['rank'] = range(1, len(df_timestamp) + 1)

        # Calculate the TQ value
        tq_value = sum(df_timestamp['total_length'] / df_timestamp['rank'])

        # Append the result
        tq_results.append({'timestamp': timestamp, 'TQ': tq_value})

    # Convert the results to a DataFrame and save it
    tq_df = pd.DataFrame(tq_results)
    output_file = os.path.join(output_path, 'tq_results.csv')
    tq_df.to_csv(output_file, index=False, sep=';')
    print(f"TQ values saved as {output_file}")

def main():
    Tk().withdraw()  # This prevents the Tkinter root window from appearing

    print("Please select the FTC clusters file to calculate TQ.")
    ftc_file = askopenfilename(title="Select the FTC Clusters CSV file", filetypes=[("CSV files", "*.csv")])
    if not ftc_file:
        print("No FTC clusters file selected. Exiting.")
        return

    # Get the directory of the FTC file to save the TQ results there
    output_path = os.path.dirname(ftc_file)

    # Calculate the TQ value
    calculate_tq(ftc_file, output_path)

if __name__ == "__main__":
    main()
