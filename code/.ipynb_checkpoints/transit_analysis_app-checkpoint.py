# Imports
import streamlit as st
import pickle
import gzip
import geopandas as gpd
import pandas as pd
import folium
import matplotlib.pyplot as plt
import seaborn as sns

from shapely.geometry import box
from streamlit_folium import st_folium
from matplotlib.colors import Normalize

# Load data
# Load the required data
@st.cache_data
def load_data():
    stops = gpd.read_file('../data/stops.csv')
    # real_time_data = pd.read_csv('../data/combined_realtime_activity.csv')
    return stops

@st.cache_data
def load_pickle(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_compressed_pickle(file_path):
    with gzip.open(file_path, "rb") as f:
        return pickle.load(f)

stops = load_data()

# Load pickled results
hdbscan_results = load_pickle('../data/hdbscan_temporal_model.pkl')
louvain_results = load_compressed_pickle('../data/louvain_communities.pkl.gz')
neighborhoods = load_pickle('../data/neighborhood_analysis.pkl')
real_time_data = load_pickle('../data/real_time_data.pkl')

# Helper function for creating maps
def create_heatmap(gdf, column, tooltip_column, palette="YlGnBu"):
    folium_map = folium.Map(location=[40.7282, -73.7949], zoom_start=11)
    folium.Choropleth(
        geo_data=gdf.to_json(),
        data=gdf,
        columns=[tooltip_column, column],
        key_on=f"feature.properties.{tooltip_column}",
        fill_color=palette,
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=column
    ).add_to(folium_map)
    return folium_map

# Create an interactive map
def create_interactive_map():
    interactive_map = folium.Map(location=[40.7282, -73.7949], zoom_start=11)

    # Plot all bus stops
    for _, stop in stops.iterrows():
        folium.CircleMarker(
            location=[stop['Latitude'], stop['Longitude']],
            radius=5,
            color='blue',
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(f"Stop ID: {stop['Stop ID']}<br>Name: {stop['Name']}", max_width=300)
        ).add_to(interactive_map)

    return interactive_map

# App structure
st.title('Analyzing Transit Service in Eastern Queens')
st.write('Explore underserved areas and transit hubs in Eastern Queens following data-driven insights with this AI-powered tool.')

# Create tabs
tabs = st.tabs([
    "Transit Overview",
    "Bus Activity Analysis",
    "Transit Network Analysis",
    "Interactive Map",
    "Recommendations"
])

# Tab 1: Interactive Map
with tabs[0]:
    st.header("Interactive Map of Bus Stops and Routes")
    interactive_map = create_interactive_map()
    st_folium(interactive_map, width=700, height=500)

# Tab 2: Transit Overview
with tabs[1]:
    st.header("Underserved Neighborhoods")
    heatmap = create_heatmap(neighborhoods, "Activity-to-Stop Ratio", "ntaname", palette="YlGnBu")
    st_folium(heatmap, width=700, height=500)
    st.write("### Key Statistics")
    st.dataframe(neighborhoods[["ntaname", "Activity-to-Stop Ratio"]].sort_values("Activity-to-Stop Ratio"))

# Tab 3: Bus Activity Analysis
with tabs[2]:
    st.header("Bus Activity Trends")
    unique_routes = real_time_data['route_id'].unique()
    num_routes = len(unique_routes)
    fig, axes = plt.subplots(nrows=num_routes, ncols=1, figsize=(12, num_routes * 3), sharex=True)

    cmap = sns.color_palette("muted", n_colors=num_routes)
    for i, (route, data) in enumerate(real_time_data.groupby("route_id")):
        hourly_avg = data.groupby(data['timestamp'].dt.hour)['vehicle_id'].count()
        axes[i].plot(hourly_avg.index, hourly_avg.values, label=f"Route {route}", color=cmap[i])
        axes[i].set_title(f"Route {route}")
        axes[i].set_ylabel("Avg Buses per Hour")
    plt.xlabel("Hour of Day")
    plt.tight_layout()
    st.pyplot(fig)

# Tab 4: Transit Network Analysis
with tabs[3]:
    st.header("Clustering and Community Detection")

    # HDBSCAN results
    st.subheader("HDBSCAN Clustering Results")
    st.write(hdbscan_results['summary'])
    st.pyplot(hdbscan_results['plot'])

    # Louvain results
    st.subheader("Louvain Community Detection Results")
    st.write(louvain_results['summary'])
    st.pyplot(louvain_results['plot'])

# Tab 5: Recommendations
with tabs[4]:
    st.header("Proposed Solutions")
    st.write("Provide summaries and actionable insights here.")

# Footer
st.sidebar.write("Developed by Deval Mehta")
st.sidebar.write("Data Sources: MTA BusTime API, NYC Open Data")