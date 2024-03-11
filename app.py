import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx

st.set_option('deprecation.showPyplotGlobalUse', False)



def plot_null_values(data, column):
    # Create a bar plot to visualize null values
    plt.figure(figsize=(8, 5))
    sns.barplot(x=data[column].isnull().value_counts().index, y=data[column].isnull().value_counts(), palette="viridis")
    plt.title(f'Null Values in {column}')
    plt.xlabel('Null Values')
    plt.ylabel('Count')
    st.pyplot()

def calculate_cost_on_fuel(row):
    # Calculate cost on fuel based on average consumption and distance
    average_consumption_per_litre = 9  # km per litre
    fuel_cost_per_litre = 3100  # TZS per litre
    return round((row['Distance'] / average_consumption_per_litre) * fuel_cost_per_litre, 2)

def draw_network_graph(df, selected_start_location):
    # Filter the dataframe based on the selected start location
    filtered_df = df[df['Start Location'] == selected_start_location]

    # Limit to only 5 trips
    filtered_df = filtered_df.head(5)

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    for index, row in filtered_df.iterrows():
        G.add_node(row['Start Location'])
        G.add_node(row['End Location'])
        G.add_edge(row['Start Location'], row['End Location'], weight=row['Distance'])

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
        "Distance": filtered_df['Distance'].round(2).tolist(),
        "Cost on Fuel (TZS)": filtered_df.apply(calculate_cost_on_fuel, axis=1).round(2).tolist()
    }
    st.table(pd.DataFrame(additional_info).round(2))

    st.write(f"Selected Start Location: {selected_start_location}")

def main():
    # Load dataset
    df = pd.read_csv('clean_trip.csv')

    # Streamlit app title
    st.title("Data Visualization App")

    # Visualization options
    visualization_options = ["Start Geofence Out of Route", "End Geofence Out of Route", "Network Graph"]
    selected_option = st.selectbox("Select Visualization Type", visualization_options)

    if selected_option == "Start Geofence Out of Route":
        # Plot null values for 'Start Geofence Out of Route'
        plot_null_values(df, 'Start Geofence')

    elif selected_option == "End Geofence Out of Route":
        # Plot null values for 'End Geofence Out of Route'
        plot_null_values(df, 'End Geofence')

    elif selected_option == "Network Graph":
        # Dropdown to select a specific start location
        start_location_options = df['Start Location'].unique()
        selected_start_location = st.selectbox("Select Start Location", start_location_options)

        # Draw the network graph for the selected start location
        draw_network_graph(df, selected_start_location)

if __name__ == "__main__":
    main()
