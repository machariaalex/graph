import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

# Load the dataset
df = pd.read_csv('mg.csv')

# Streamlit app title
st.title("Network Visualization App")

# Filter unique registration numbers
registration_options = df['Registration'].unique()

# Dropdown to select a specific registration number
selected_registration = st.selectbox("Select Registration Number", registration_options)

# Filter the dataframe based on the selected registration number
filtered_df = df[df['Registration'] == selected_registration]

# Check if there are rows for the selected registration
if not filtered_df.empty:
    # Select a row using a slider within the filtered dataframe
    row_index = st.slider("Select a row index", 0, len(filtered_df) - 1, 0)
    row = filtered_df.iloc[row_index]

    # Extract information
    start_location = row['Start Location']
    end_location = row['End Location']
    trip_distance = row['Trip Distance']

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    G.add_edge(start_location, end_location, weight=trip_distance)

    # Draw the network diagram
    fig, ax = plt.subplots()
    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    nx.draw_networkx_labels(G, pos)

    # Display the plot using Streamlit
    st.pyplot(fig)

    # Additional information about the selected row
    st.write("Start Location:", start_location)
    st.write("End Location:", end_location)
    st.write("Trip Distance:", trip_distance)
else:
    st.warning(f"No data available for the selected registration number: {selected_registration}")
