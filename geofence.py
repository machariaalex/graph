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

def draw_network_diagram(start_location, end_location, trip_distance):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    G.add_edge(start_location, end_location, weight=trip_distance)

    # Draw the route diagram
    fig, ax = plt.subplots()
    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    nx.draw_networkx_labels(G, pos)

    # Display the plot using Streamlit
    st.pyplot(fig)

def draw_on_route_network_diagram(data, selected_registration, selected_index):
    # Filter data based on selected registration number
    filtered_data = data[data['Registration'] == selected_registration]

    # Create a directed graph for on route events
    G = nx.DiGraph()

    # Add nodes and edges for the selected row where 'Start Geofence' and 'End Geofence' are not null
    row = filtered_data.iloc[selected_index]
    if not pd.isnull(row['Start Geofence']) and not pd.isnull(row['End Geofence']):
        G.add_edge(row['Start Geofence'], row['End Geofence'], weight=row['Trip Distance'])

        # Draw the on route diagram
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        nx.draw_networkx_labels(G, pos)

        # Display the plot using Streamlit
        st.pyplot(fig)

        # Additional information about tstreamlithe selected row
        st.write("Start Geofence:", row['Start Geofence'])
        st.write("End Geofence:", row['End Geofence'])
        st.write("Trip Distance:", row['Trip Distance'])
    else:
        st.warning("Start Geofence and End Geofence must not be null for this visualization.")

def main():
    # Load datasets
    df_geofence = pd.read_csv('geofence.csv')
    df_route = pd.read_csv('new.csv')
    
    # Streamlit app title
    st.title("Route Planning App")

    # Visualization options
    visualization_options = ["Start Geofence Out of Route", "End Geofence Out of Route", "Route Diagram", "On Route Diagram"]
    selected_option = st.selectbox("Select Visualization Type", visualization_options)

    if selected_option == "Start Geofence Out of Route":
        # Visualize out of route events for Start Geofence
        plot_out_of_route(df_geofence, "Start Geofence")

    elif selected_option == "End Geofence Out of Route":
        # Visualize out of route events for End Geofence
        plot_out_of_route(df_geofence, "End Geofence")

    elif selected_option == "Route Diagram":
        # Filter unique registration numbers
        registration_options = df_route['Registration'].unique()

        # Dropdown to select a specific registration number
        selected_registration = st.selectbox("Select Registration Number", registration_options)

        # Filter the dataframe based on the selected registration number
        filtered_df = df_route[df_route['Registration'] == selected_registration]

        # Check if there are rows for the selected registration
        if not filtered_df.empty:
            # Select a row using a slider within the filtered dataframe
            row_index = st.slider("Select a row index", 0, len(filtered_df) - 1, 0)
            row = filtered_df.iloc[row_index]

            # Extract information
            start_location = row['Start Location']
            end_location = row['End Location']
            trip_distance = row['Trip Distance']

            # Draw the route diagram
            draw_network_diagram(start_location, end_location, trip_distance)

            # Additional information about the selected row
            st.write("Start Location:", start_location)
            st.write("End Location:", end_location)
            st.write("Trip Distance:", trip_distance)
        else:
            st.warning(f"No data available for the selected registration number: {selected_registration}")

    elif selected_option == "On Route Diagram":
        # Dropdown to select a specific registration number for the on route network diagram
        registration_options = df_geofence['Registration'].unique()
        selected_registration_on_route = st.selectbox("Select Registration Number", registration_options)

        # Filter the dataframe based on the selected registration number
        filtered_df_on_route = df_geofence[df_geofence['Registration'] == selected_registration_on_route]

        # Check if there are rows for the selected registration
        if not filtered_df_on_route.empty:
            # Select a row using a slider within the filtered dataframe
            row_index_on_route = st.slider("Select a row index", 0, len(filtered_df_on_route) - 1, 0)

            # Draw the on route diagram for the selected index
            draw_on_route_network_diagram(filtered_df_on_route, selected_registration_on_route, row_index_on_route)
        else:
            st.warning(f"No data available for the selected registration number: {selected_registration_on_route}")

if __name__ == "__main__":
    main()
