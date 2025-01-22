# Imports
import datetime
import glob
import pandas as pd

# File Paths
data_directory = "../data/"
real_time_files_pattern = f"{data_directory}realtime_data_MTA NYCT_*.csv"


# Load Real-Time data
real_time_files = glob.glob(real_time_files_pattern)
real_time_data = pd.concat([pd.read_csv(file) for file in real_time_files], ignore_index = True)

# Rename columns for consistency
real_time_data.rename(
    columns={
        "Route ID": "route_id",
        "Vehicle ID": "vehicle_id",
        "Latitude": "vehicle_lat",
        "Longitude": "vehicle_lon",
        "Timestamp": "timestamp",
    },
    inplace=True,
)

real_time_data["route_id"] = real_time_data["route_id"].str.strip()

# Ensure timestamp is parsed
real_time_data["timestamp"] = pd.to_datetime(real_time_data["timestamp"])

# Sort by route, vehicle, and timestamp
real_time_data = real_time_data.sort_values(["route_id", "vehicle_id", "timestamp"])

# Save as single csv
real_time_data.to_csv('../data/combined_realtime_activity.csv')