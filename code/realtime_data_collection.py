import os
import requests
import pandas as pd
from datetime import datetime

# Fetch real-time data function
def fetch_realtime_data(route_id, api_key):
    """
    Fetch real-time data for a specific bus route.
    """
    try:
        # API endpoint and parameters
        endpoint = "https://api.prod.obanyc.com/api/siri/vehicle-monitoring.json"
        params = {
            "key": api_key,
            "OperatorRef": "MTA",
            "MonitoringRef": "308209",
            "LineRef": route_id
        }

        # Make the API request
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()

        # Parse response
        data = response.json()
        vehicles = data.get("Siri", {}).get("ServiceDelivery", {}).get("VehicleMonitoringDelivery", [{}])[0].get("VehicleActivity", [])

        # Check if there are no vehicles active
        if not vehicles:
            return None

        # Collect vehicle data
        records = []
        for vehicle in vehicles:
            journey = vehicle["MonitoredVehicleJourney"]
            location = journey["VehicleLocation"]
            records.append({
                "Route ID": route_id,
                "Vehicle ID": journey["VehicleRef"],
                "Latitude": location.get("Latitude"),
                "Longitude": location.get("Longitude"),
                "Timestamp": datetime.now().isoformat()
            })

        return pd.DataFrame(records)
    except Exception as e:
        print(f"Error fetching data for route {route_id}: {e}")
        return None

def save_data_to_csv(data, output_file):
    """
    Save data to CSV.
    """
    if data is not None and not data.empty:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if os.path.exists(output_file):
            data.to_csv(output_file, mode='a', header=False, index=False)
        else:
            data.to_csv(output_file, index=False)

def collect_data_for_routes(route_ids, api_key):
    """
    Collect and save real-time data for multiple routes.
    """
    for route_id in route_ids:
        print(f"Fetching data for {route_id}...")
        data = fetch_realtime_data(route_id, api_key)
        if data is not None:
            save_data_to_csv(data, output_file=f"../data/realtime_data_{route_id.replace('%20', '_')}.csv")