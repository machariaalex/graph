import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx

# Function to calculate the total cost on fuel
def calculate_total_fuel_cost(distance):
    # 1 litre covers 9 km, and 1 litre is sold at 3100 TZS
    consumption_per_km = 1 / 9
    cost_per_litre = 3100
    return round((distance * consumption_per_km * cost_per_litre), 2)

# Function to calculate the total fuel cost per month
def calculate_total_fuel_cost_per_month(df):
    df['Total Cost on Fuel (TZS)'] = df['Distance'].apply(calculate_total_fuel_cost)
    total_fuel_cost_per_month = df.groupby(df['Start Time'].dt.month)['Total Cost on Fuel (TZS)'].sum().reset_index(name='Total Fuel Cost')
    total_fuel_cost_per_month['Start Month'] = total_fuel_cost_per_month['Start Time']  # Add the 'Start Month' column
    return total_fuel_cost_per_month

def plot_null_values(data, column):
    # Create a bar plot to visualize null values with a colored background
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=data[column].isnull().value_counts().index, y=data[column].isnull().value_counts(), palette=["#ff7f0e", "#1f77b4"])

    total = len(data[column])
    for p in ax.patches:
        percentage = '{:.2f}%'.format(100 * p.get_height()/total)
        x = p.get_x() + p.get_width() / 2
        y = p.get_height()
        ax.annotate(percentage, (x, y), ha='center', va='center', color='black', size=12)

    plt.title(f'Events Out of Route on {column}')
    plt.xlabel('Out of Route')
    plt.ylabel('Count')
    st.pyplot()

def draw_network_graph(df, selected_registration, selected_start_location, show_trips_per_day):
    # Filter the dataframe based on the selected registration number and start location
    filtered_df = df[(df['Registration'] == selected_registration) & (df['Start Location'] == selected_start_location)]

    # Limit to only 5 trips for network diagram
    filtered_df_network = filtered_df.head(5)

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges for network diagram
    for index, row in filtered_df_network.iterrows():
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
    st.subheader(f"Registration Number: {selected_registration}")
    st.subheader(f"Start Location: {selected_start_location}")

    # Table showing start month, start location, end time, end location, distance, and total cost on fuel of trips plotted on the network diagram
    st.write("Trips Plotted on Network Diagram:")
    additional_info_table = filtered_df_network[['Start Time', 'End Time', 'Start Location', 'End Location', 'Distance']]
    additional_info_table['Total Cost on Fuel (TZS)'] = additional_info_table['Distance'].apply(calculate_total_fuel_cost)
    additional_info_table['Start Month'] = additional_info_table['Start Time'].dt.month
    st.table(additional_info_table)

    # Total number of trips made per month for the selected registration number and start location
    total_trips_per_month = filtered_df.groupby([filtered_df['Start Time'].dt.month, 'Registration']).size().reset_index(name='Total Trips')
    total_trips_per_month['Total Cost'] = total_trips_per_month['Total Trips'] * 90000  # Assuming 1 trip costs 90000 TZS
    total_trips_per_month = total_trips_per_month.rename(columns={'Start Time': 'Start Month'})

    # Add a 'Totals' row
    totals_row = pd.DataFrame({
        'Start Month': ['Totals'],
        'Registration': [''],
        'Total Trips': [total_trips_per_month['Total Trips'].sum()],
        'Total Cost': [total_trips_per_month['Total Cost'].sum()]
    })

    total_trips_per_month = pd.concat([total_trips_per_month, totals_row], ignore_index=True)

    # Calculate total fuel cost per month
    total_fuel_cost_per_month = calculate_total_fuel_cost_per_month(filtered_df_network)
    st.write("Total Fuel Cost per Month (Network Diagram):")
    st.table(total_fuel_cost_per_month)

    st.write("Total Number of Trips per Month:")
    st.table(total_trips_per_month.head(30))  # Limiting to 30 trips

    # Line chart showing trips made per day for the selected registration number if checkbox is selected
    if show_trips_per_day:
        draw_trips_per_day_chart(filtered_df)

def draw_out_of_route_network_graph(df, selected_registration, selected_start_location, show_trips_per_day_out_of_route):
    # Filter the dataframe for trips where both Start and End Geofence are null (Out of Route)
    out_of_route_df = df[(df['Start Geofence'].isnull()) & (df['End Geofence'].isnull()) & (df['Registration'] == selected_registration) & (df['Start Location'] == selected_start_location)]

    # Limit to only 5 trips for out of route network diagram
    out_of_route_df_network = out_of_route_df.head(5)

    # Create a directed graph for out of route network diagram
    G = nx.DiGraph()

    # Add nodes and edges for out of route network diagram
    for index, row in out_of_route_df_network.iterrows():
        G.add_node(row['Start Location'])
        G.add_node(row['End Location'])
        G.add_edge(row['Start Location'], row['End Location'], weight=row['Distance'])

    # Draw the out of route network graph
    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, seed=42)  # Seed for reproducibility
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='orange')  # Use orange for out of route trips
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrowsize=20)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    nx.draw_networkx_labels(G, pos, font_color='black')

    # Display the plot using Streamlit
    st.pyplot(fig)

    # Additional information in a table below the graph for out of route trips
    st.subheader(f"Registration Number: {selected_registration}")
    st.subheader(f"Start Location: {selected_start_location}")

    # Table showing start month, start location, end time, end location, distance, and total cost on fuel of out of route trips
    st.write("Trips Out of Route:")
    out_of_route_table = out_of_route_df_network[['Start Time', 'End Time', 'Start Location', 'End Location', 'Distance']]
    out_of_route_table['Total Cost on Fuel (TZS)'] = out_of_route_table['Distance'].apply(calculate_total_fuel_cost)
    out_of_route_table['Start Month'] = out_of_route_table['Start Time'].dt.month
    st.table(out_of_route_table)

    # Total number of trips per month that were out of route for the selected registration number and start location
    total_out_of_route_per_month = out_of_route_df.groupby([out_of_route_df['Start Time'].dt.month, 'Registration']).size().reset_index(name='Total Trips Out of Route')
    total_out_of_route_per_month['Total Cost'] = total_out_of_route_per_month['Total Trips Out of Route'] * 90000  # Assuming 1 trip costs 90000 TZS
    total_out_of_route_per_month = total_out_of_route_per_month.rename(columns={'Start Time': 'Start Month'})

    # Add a 'Totals' row
    totals_row = pd.DataFrame({
        'Start Month': ['Totals'],
        'Registration': [''],
        'Total Trips Out of Route': [total_out_of_route_per_month['Total Trips Out of Route'].sum()],
        'Total Cost': [total_out_of_route_per_month['Total Cost'].sum()]
    })

    total_out_of_route_per_month = pd.concat([total_out_of_route_per_month, totals_row], ignore_index=True)

    # Calculate total fuel cost per month for out of route trips
    total_fuel_cost_out_of_route_per_month = calculate_total_fuel_cost_per_month(out_of_route_df_network)
    st.write("Total Fuel Cost per Month (Out of Route):")
    st.table(total_fuel_cost_out_of_route_per_month)

    st.write("Total Number of Trips Out of Route per Month:")
    st.table(total_out_of_route_per_month)

    # Line chart showing trips made per day for the selected registration number if checkbox is selected
    if show_trips_per_day_out_of_route:
        draw_trips_per_day_chart(out_of_route_df)

def draw_trips_per_day_chart(df):
    # Line chart showing trips made per day
    trips_per_day_chart = df.groupby(df['Start Time'].dt.date).size().reset_index(name='Trips per Day')
    trips_per_day_chart['Start Time'] = pd.to_datetime(trips_per_day_chart['Start Time'])
    st.subheader("Trips Made per Day:")
    st.line_chart(trips_per_day_chart.set_index('Start Time'))

def main():
    # Load dataset
    df = pd.read_csv('clean_tripdd.csv')
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])

    # Streamlit app title
    st.title("Graphical Network Theory: Optimizing Route Planning App")

    # Visualization options
    visualization_options = ["Start Geofence Out of Route", "End Geofence Out of Route", "Network Graph", "Out of Route Network Diagram", "Total Fuel Cost Comparison"]
    selected_option = st.selectbox("Select Visualization Type", visualization_options)

    if selected_option == "Start Geofence Out of Route":
        # Plot null values for 'Start Geofence'
        plot_null_values(df, 'Start Geofence')

    elif selected_option == "End Geofence Out of Route":
        # Plot null values for 'End Geofence'
        plot_null_values(df, 'End Geofence')

    elif selected_option == "Network Graph":
        # Dropdowns to select a specific registration number and start location
        registration_options = df['Registration'].unique()
        selected_registration = st.selectbox("Select Registration Number", registration_options)

        start_location_options = df['Start Location'].unique()
        selected_start_location = st.selectbox("Select Start Location", start_location_options)

        # Checkbox for visualizing number of trips per day on the selected registration number
        show_trips_per_day = st.checkbox("Show Trips Per Day")

        # Draw the network graph for the selected registration number and start location
        draw_network_graph(df, selected_registration, selected_start_location, show_trips_per_day)

    elif selected_option == "Out of Route Network Diagram":
        # Dropdowns to select a specific registration number and start location for out of route network diagram
        registration_options = df['Registration'].unique()
        selected_registration_out_of_route = st.selectbox("Select Registration Number", registration_options)

        start_location_options = df['Start Location'].unique()
        selected_start_location_out_of_route = st.selectbox("Select Start Location", start_location_options)

        # Checkbox for visualizing number of trips per day on the selected registration number for out of route network diagram
        show_trips_per_day_out_of_route = st.checkbox("Show Trips Per Day")

        # Draw the out of route network graph for the selected registration number and start location
        draw_out_of_route_network_graph(df, selected_registration_out_of_route, selected_start_location_out_of_route, show_trips_per_day_out_of_route)

    elif selected_option == "Total Fuel Cost Comparison":
        # Dropdowns to select a specific registration number and month for fuel cost comparison
        registration_options = df['Registration'].unique()
        selected_registration_fuel_comparison = st.selectbox("Select Registration Number", registration_options)

        month_options = df['Start Time'].dt.month.unique()
        selected_month_fuel_comparison = st.selectbox("Select Month", month_options)

        # Filter the dataframe based on the selected registration number and month
        filtered_df_fuel_comparison = df[(df['Registration'] == selected_registration_fuel_comparison) & (df['Start Time'].dt.month == selected_month_fuel_comparison)]

        # Calculate total fuel cost for both on-route and out-of-route trips
        total_fuel_cost_network = filtered_df_fuel_comparison[~filtered_df_fuel_comparison['Start Geofence'].isnull() & ~filtered_df_fuel_comparison['End Geofence'].isnull()]['Distance'].apply(calculate_total_fuel_cost).sum()
        total_fuel_cost_out_of_route = filtered_df_fuel_comparison[filtered_df_fuel_comparison['Start Geofence'].isnull() & filtered_df_fuel_comparison['End Geofence'].isnull()]['Distance'].apply(calculate_total_fuel_cost).sum()

        # Bar plot for the comparison
        fig, ax = plt.subplots()
        ax.bar(['Network Diagram', 'Out of Route Network Diagram'], [total_fuel_cost_network, total_fuel_cost_out_of_route], color=['skyblue', 'orange'])
        ax.set_ylabel('Total Fuel Cost (TZS)')
        ax.set_title('Total Fuel Cost Comparison')
        st.pyplot(fig)

if __name__ == "__main__":
    main()
