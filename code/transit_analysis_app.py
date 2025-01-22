# Imports
import streamlit as st
import geopandas as gpd
import pandas as pd
import folium

from shapely.geometry import box
from streamlit_folium import st_folium

# Load data
stops = gpd.read_file('../data/stops.csv')
neighborhoods = gpd.read_file('../data/nyc_by_neighborhood_2020.geojson')
activity_data = pd.read_csv('../data/combined_realtime')