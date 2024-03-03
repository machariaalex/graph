import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_option('deprecation.showPyplotGlobalUse', False)

def plot_out_of_route(data, geofence_column):
    # Create a new column to indicate out of route events
    data['Out of Route'] = (data[geofence_column] == 'X') | (data[geofence_column] == 'Y')

    # Plot the distribution of out of route events
    plt.figure(figsize=(10, 6))
    sns.countplot(x='Out of Route', data=data)
    plt.title(f'Distribution of Out of Route Events in {geofence_column}')
    plt.xlabel('Out of Route Event')
    plt.ylabel('Count')
    st.pyplot()

def draw_network_graph(df, selected_start_location):
    # Filter the dataframe based on the selected start location
    filtered_df = df[df['Position Description'] == selected_start_location]

    # Limit to only 5 trips
    filtered_df = filtered_df.head(5)

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    for index, row in filtered_df.iterrows():
        G.add_node(row['Position Description'])
        G.add_node(row['End Location'])
        G.add_edge(row['Position Description'], row['End Location'], weight=row['Trip Distance'])

    # Draw the network graph
    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=42)  # Seed for reproducibility
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrowsize=20)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    nx.draw_networkx_labels(G, pos, font_color='black')

    # Display the plot using Streamlit
    st.pyplot(fig)

    # Additional information in a table below the graph
    st.subheader("Additional Information:")
    additional_info = {
        "Trip Number": list(range(1, len(filtered_df) + 1)),
        "End Location": filtered_df['End Location'].tolist(),
        "Trip Distance": filtered_df['Trip Distance'].tolist()
    }
    st.table(pd.DataFrame(additional_info))

    st.write(f"Selected Start Location: {selected_start_location}")

def main():
    # Load datasets
    df_network_graph = pd.read_csv('sg.csv')
    df_geofence = pd.read_csv('geofence.csv')

    # Streamlit app title
    st.title("Route Planning App")

    # Visualization options
    visualization_options = ["Start Geofence Out of Route", "End Geofence Out of Route", "Network Graph"]
    selected_option = st.selectbox("Select Visualization Type", visualization_options)

    if selected_option == "Start Geofence Out of Route":
        # Visualize out of route events for Start Geofence
        plot_out_of_route(df_geofence, "Start Geofence")

    elif selected_option == "End Geofence Out of Route":
        # Visualize out of route events for End Geofence
        plot_out_of_route(df_geofence, "End Geofence")

    elif selected_option == "Network Graph":
        # Dropdown to select a specific start location for the network graph
        start_location_options = df_network_graph['Position Description'].unique()
        selected_start_location_network_graph = st.selectbox("Select Start Location", start_location_options)

        # Draw the network graph for the selected start location
        draw_network_graph(df_network_graph, selected_start_location_network_graph)

if __name__ == "__main__":
    main()
