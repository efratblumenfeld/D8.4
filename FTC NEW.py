import pandas as pd
import networkx as nx
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import time


def create_ftc_clusters(availability_file, links_file, output_path):
    print("Loading availability data...")
    # Load the availability data
    availability_df = pd.read_csv(availability_file)

    print("Loading links data...")
    # Load the links data
    links_df = pd.read_csv(links_file)

    print("Merging availability data with links data...")
    # Merge availability data with links data to include the 'distance' column and node coordinates
    df_merged = availability_df.merge(links_df, on='internal_segment_id', how='left')

    print("Creating FTC clusters...")

    ftc_clusters = []

    # Iterate over each timestamp
    for timestamp in df_merged['timestamp'].unique():
        print(f"Processing timestamp {timestamp}...")
        # Filter data for this timestamp
        df_timestamp = df_merged[df_merged['timestamp'] == timestamp]

        # Filter out links with availability < 0.5
        df_filtered = df_timestamp[df_timestamp['availability'] >= 0.5]

        # Debug: Print the filtered data
        print(f"Filtered data for timestamp {timestamp}:")
        print(df_filtered)

        # Create a directed graph using the filtered links
        G = nx.DiGraph()
        for idx, row in df_filtered.iterrows():
            origin = (row['origin_lat'], row['origin_lon'])
            dest = (row['dest_lat'], row['dest_lon'])
            G.add_edge(origin, dest, length=row['distance'], availability=row['availability'])

        # Debug: Print the edges in the graph
        print(f"Edges added to the graph for timestamp {timestamp}:")
        print(G.edges(data=True))

        # Find strongly connected components (SCCs)
        sccs = list(nx.strongly_connected_components(G))

        # Debug: Print the SCCs found
        print(f"SCCs found for timestamp {timestamp}:")
        for scc in sccs:
            print(scc)

        # Process each SCC
        for i, scc in enumerate(sccs, start=1):
            scc_size = len(scc)
            print(f"Found SCC with {scc_size} nodes")
            if scc_size >= 2:  # Only include clusters with at least 2 links
                # Calculate the total length of the links in the SCC
                total_length = df_filtered[df_filtered.apply(
                    lambda row: (row['origin_lat'], row['origin_lon']) in scc and (
                    row['dest_lat'], row['dest_lon']) in scc, axis=1)]['distance'].sum()
                print(f"Including SCC as FTC({i}) with total length {total_length}")
                ftc_clusters.append({
                    'timestamp': timestamp,
                    'ftc_cluster': f'FTC({i})',
                    'number_of_links': scc_size,
                    'total_length': total_length
                })

    # Convert the FTC clusters to a DataFrame and save it
    ftc_df = pd.DataFrame(ftc_clusters)

    # Add a timestamp to the filename to make it unique
    timestamp_str = time.strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(output_path, f'ftc_clusters_{timestamp_str}.csv')

    if not ftc_df.empty:
        ftc_df.to_csv(output_file, index=False, sep=';')
        print(f"FTC clusters saved as {output_file}")
    else:
        print("No FTC clusters found that meet the criteria.")


def main():
    Tk().withdraw()  # This prevents the Tkinter root window from appearing

    print("Please select the availability data file to create FTC clusters.")
    availability_file = askopenfilename(title="Select the Availability CSV file", filetypes=[("CSV files", "*.csv")])
    if not availability_file:
        print("No availability data file selected. Exiting.")
        return

    print("Please select the links file to include distance information.")
    links_file = askopenfilename(title="Select the Links CSV file", filetypes=[("CSV files", "*.csv")])
    if not links_file:
        print("No links file selected. Exiting.")
        return

    # Get the directory of the availability file to save the result there
    output_path = os.path.dirname(availability_file)

    # Create FTC clusters based on the availability index
    create_ftc_clusters(availability_file, links_file, output_path)


if __name__ == "__main__":
    main()
