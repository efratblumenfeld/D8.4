import pandas as pd
import networkx as nx
import folium
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os

def create_network_map(nodes_file, links_file, output_path):
    print("Loading data...")
    # Load the data
    nodes_df = pd.read_csv(nodes_file)
    links_df = pd.read_csv(links_file)

    print("Creating the network...")
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with attributes
    for idx, row in nodes_df.iterrows():
        # Add the node with its position (lat, lon) as a separate entry in the graph
        G.add_node(row['node_id'], pos=(row['node_lat'], row['node_lon']))

    # Add edges with attributes using the information from links_df
    for idx, row in links_df.iterrows():
        origin = (row['origin_lat'], row['origin_lon'])
        dest = (row['dest_lat'], row['dest_lon'])
        G.add_edge(origin, dest, distance=row['distance'], lanes=row['number_of_lanes'])

    print("Generating the map...")
    # Create a base map centered on the average location of all nodes
    lat_center = links_df[['origin_lat', 'dest_lat']].mean().mean()
    lon_center = links_df[['origin_lon', 'dest_lon']].mean().mean()
    network_map = folium.Map(location=[lat_center, lon_center], zoom_start=12)

    # Add edges to the map (without adding markers for nodes)
    for u, v, data in G.edges(data=True):
        folium.PolyLine(locations=[u, v], color='blue', weight=2.5 + data['lanes'], opacity=1).add_to(network_map)

    # Save the map to an HTML file in the same directory as the nodes file
    output_file = os.path.join(output_path, 'network_map.html')
    network_map.save(output_file)
    print(f"Map saved as {output_file}")

# Use Tkinter to open file dialog for selecting files
def main():
    Tk().withdraw()  # This prevents the Tkinter root window from appearing

    print("Please select the nodes file.")
    # Ask the user to select the nodes file
    nodes_file = askopenfilename(title="Select the Nodes CSV file", filetypes=[("CSV files", "*.csv")])
    if not nodes_file:
        print("No nodes file selected. Exiting.")
        return

    print("Please select the links file.")
    # Ask the user to select the links file
    links_file = askopenfilename(title="Select the Links CSV file", filetypes=[("CSV files", "*.csv")])
    if not links_file:
        print("No links file selected. Exiting.")
        return

    # Get the directory of the nodes file to save the map there
    output_path = os.path.dirname(nodes_file)

    # Generate the network map
    create_network_map(nodes_file, links_file, output_path)

if __name__ == "__main__":
    main()
import pandas as pd
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import time

def calculate_availability(measurements_file, output_path):
    print("Loading measurement data...")
    # Load the measurements data
    measurements_df = pd.read_csv(measurements_file)

    print("Calculating availability index...")
    # Calculate the maximum velocity for each link
    max_velocity = measurements_df.groupby('internal_segment_id')['velocity'].max()

    # Merge the max velocity back into the original dataframe
    measurements_df = measurements_df.merge(max_velocity, on='internal_segment_id', suffixes=('', '_max'))

    # Calculate the availability for each measurement
    measurements_df['availability'] = measurements_df['velocity'] / measurements_df['velocity_max']

    # Generate a unique filename by adding a timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(output_path, f'availability_data_{timestamp}.csv')

    # Save the results with the availability index to a new CSV file
    measurements_df.to_csv(output_file, index=False)
    print(f"Availability data saved as {output_file}")

def main():
    Tk().withdraw()  # This prevents the Tkinter root window from appearing

    print("Please select the measurements file to calculate availability.")
    # Ask the user to select the measurements file
    measurements_file = askopenfilename(title="Select the Measurements CSV file", filetypes=[("CSV files", "*.csv")])
    if not measurements_file:
        print("No measurements file selected. Exiting.")
        return

    # Get the directory of the measurements file to save the result there
    output_path = os.path.dirname(measurements_file)

    # Calculate the availability index and save the data
    calculate_availability(measurements_file, output_path)

if __name__ == "__main__":
    main()
