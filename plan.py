import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
import calendar

st.set_option('deprecation.showPyplotGlobalUse', False)

# Function to calculate the total cost on fuel
def calculate_total_fuel_cost(distance):
    # 1 litre covers 9 km, and 1 litre is sold at 3100 TZS
    consumption_per_km = 1 / 9
    cost_per_litre = 3100
    return round((distance * consumption_per_km * cost_per_litre), 2)

# Function to calculate the total fuel cost per month
def calculate_total_fuel_cost_per_month(df):
    df['Total Cost on Fuel (TZS)'] = df['Distance'].apply(calculate_total_fuel_cost)
    total_fuel_cost_per_month = df.groupby(df['Start Month'])['Total Cost on Fuel (TZS)'].sum().reset_index(name='Total Fuel Cost')
    return total_fuel_cost_per_month

# Function to calculate fuel costs and percentages for the selected month
def calculate_fuel_costs(df):
    on_route_df = df[~df['Start Geofence'].isnull() & ~df['End Geofence'].isnull()]
    out_of_route_df = df[df['Start Geofence'].isnull() & df['End Geofence'].isnull()]

    on_route_fuel_cost = on_route_df['Distance'].apply(calculate_total_fuel_cost).sum()
    out_of_route_fuel_cost = out_of_route_df['Distance'].apply(calculate_total_fuel_cost).sum()

    total_fuel_cost = on_route_fuel_cost + out_of_route_fuel_cost

    # Calculate percentages
    percentage_on_route = (on_route_fuel_cost / total_fuel_cost) * 100
    percentage_out_of_route = (out_of_route_fuel_cost / total_fuel_cost) * 100

    return on_route_fuel_cost, out_of_route_fuel_cost, percentage_on_route, percentage_out_of_route

def plot_null_values(data, column):
    # Create a bar plot to visualize null values with a colored background
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(x=data[column].isnull().value_counts().index, y=data[column].isnull().value_counts(), palette=["#ff7f0e", "#013220"])

    total = len(data[column])
    for p in ax.patches:
        percentage = '{:.2f}%'.format(100 * p.get_height()/total)
        x = p.get_x() + p.get_width() / 2
        y = p.get_height()
        ax.annotate(percentage, (x, y), ha='center', va='center', color='black', size=12)

    plt.title(f'Trips that Started Out of Geofence' if column == 'Start Geofence' else f'Trips that Ended Out of Geofence')
    plt.xlabel('Out of Route')
    plt.ylabel('No. of Trips')
    st.pyplot()
    # Add insights below the chart
    if column == 'Start Geofence':
        st.subheader("Insights:")
        st.write("i.  An average of 60% of the amount spent on fuel was out of the geofence.")
        st.write("ii.  3 out of 5 trips made by RMs in day started out of the geofence.")
    elif column == 'End Geofence':
        st.subheader("Insights:")
        st.write("i.  An average of 64% of the amount spent on fuel was out of the end of the geofence.")
        st.write("ii.  3 out of 5 trips made by RMs in day started out of the geofence.")

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
    additional_info_table = filtered_df_network[['Start Month', 'End Time', 'Start Location', 'End Location', 'Distance']]
    additional_info_table['Total Cost on Fuel (TZS)'] = additional_info_table['Distance'].apply(calculate_total_fuel_cost)
    st.table(additional_info_table)

    # Total number of trips made per month for the selected registration number and start location
    total_trips_per_month = filtered_df.groupby(['Start Month', 'Registration']).size().reset_index(name='Total Trips')
    total_trips_per_month = total_trips_per_month.rename(columns={'Start Month': 'Month'})

    # Add a 'Totals' row
    totals_row = pd.DataFrame({
        'Month': ['Totals'],
        'Registration': [''],
        'Total Trips': [total_trips_per_month['Total Trips'].sum()]
    })

    total_trips_per_month = pd.concat([total_trips_per_month, totals_row], ignore_index=True)

    # Calculate total fuel cost per month
    total_fuel_cost_per_month = calculate_total_fuel_cost_per_month(filtered_df_network)
    # Add total distance covered for the selected registration number to the table
    total_fuel_cost_per_month['Total Distance Covered (km)'] = filtered_df['Distance'].sum()

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
    out_of_route_table = out_of_route_df_network[['Start Month', 'End Time', 'Start Location', 'End Location', 'Distance']]
    out_of_route_table['Total Cost on Fuel (TZS)'] = out_of_route_table['Distance'].apply(calculate_total_fuel_cost)
    st.table(out_of_route_table)

    # Total number of trips per month that were out of route for the selected registration number and start location
    total_out_of_route_per_month = out_of_route_df.groupby(['Start Month', 'Registration']).size().reset_index(name='Total Trips Out of Route')
    total_out_of_route_per_month = total_out_of_route_per_month.rename(columns={'Start Month': 'Month'})

    # Add a 'Totals' row
    totals_row = pd.DataFrame({
        'Month': ['Totals'],
        'Registration': [''],
        'Total Trips Out of Route': [total_out_of_route_per_month['Total Trips Out of Route'].sum()]
    })

    total_out_of_route_per_month = pd.concat([total_out_of_route_per_month, totals_row], ignore_index=True)

    # Calculate total fuel cost per month for out of route trips
    total_fuel_cost_out_of_route_per_month = calculate_total_fuel_cost_per_month(out_of_route_df_network)
    # Add total distance covered for the selected registration number to the table
    total_fuel_cost_out_of_route_per_month['Total Distance Covered (km)'] = out_of_route_df['Distance'].sum()

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
logo_path = '/home/ndegwa/mlfow/sanku.jpeg'
