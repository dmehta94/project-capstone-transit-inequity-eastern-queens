#Imports
import os
import requests
import pandas as pd

# Access API Key
api_key = os.getenv("MTA_API_KEY")

# List of routes to collect
route_ids = [
    "MTA%20NYCT_Q1", "MTA%20NYCT_Q2", "MTA%20NYCT_Q3", "MTA%20NYCT_Q4",
    "MTA%20NYCT_Q5", "MTA%20NYCT_Q12", "MTA%20NYCT_Q13", "MTA%20NYCT_Q20A", 
    "MTA%20NYCT_Q20B", "MTA%20NYCT_Q27", "MTA%20NYCT_Q28", "MTA%20NYCT_Q30",
    "MTA%20NYCT_Q31", "MTA%20NYCT_Q36", "MTA%20NYCT_Q43", "MTA%20NYCT_Q44+",
    "MTA%20NYCT_Q46", "MTA%20NYCT_Q76", "MTA%20NYCT_Q77", "MTA%20NYCT_Q83",
    "MTA%20NYCT_Q84", "MTA%20NYCT_Q85", "MTA%20NYCT_Q88"
]

def fetch_stops_for_route(route_id, api_key):
    # Set the endpoint
    endpoint = f"https://bustime.mta.info/api/where/stops-for-route/{route_id}.json"
    
    params = {
        "key": api_key,
        "includePolylines": "false",
        "version": "2"
    }
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch data for {route_id}: {response.status_code}")
    
    # Parse the data response
    data = response.json()
    
    # Check the structure of the stops data
    stops_data = data['data']['references']['stops']
    
    if isinstance(stops_data, list):
        # If stops_data is a list, iterate over the list
        stops = [
            {
                "Route ID": route_id,
                "Stop ID": stop.get('id', 'N/A'),
                "Stop Name": stop.get('name', 'N/A'),
                "Latitude": stop.get('lat', 'N/A'),
                "Longitude": stop.get('lon', 'N/A')
            }
            for stop in stops_data
        ]
    elif isinstance(stops_data, dict):
        # If stops_data is a dictionary, iterate over items
        stops = [
            {
                "Route ID": route_id,
                "Stop ID": stop_id,
                "Stop Name": stop_info.get('name', 'N/A'),
                "Latitude": stop_info.get('lat', 'N/A'),
                "Longitude": stop_info.get('lon', 'N/A')
            }
            for stop_id, stop_info in stops_data.items()
        ]
    else:
        raise ValueError(f"Unexpected stops data format for {route_id}")
    
    return pd.DataFrame(stops)

def collect_all_stops(route_ids, api_key, output_file="../data/stops.csv"):
    all_stops = []

    for route_id in route_ids:
        print(f"Fetching stops for {route_id}...")
        try:
            stops = fetch_stops_for_route(route_id, api_key)
            all_stops.append(stops)
        except Exception as e:
            print(f"Error fetching stops for {route_id}: {e}")

    # Concatenate all stop dataframes
    if all_stops:
        stops_df = pd.concat(all_stops, ignore_index=True)
        stops_df.to_csv(output_file, index=False)
        print(f"Stop data saved to '{output_file}'.")
    else:
        print("No stop data collected.")