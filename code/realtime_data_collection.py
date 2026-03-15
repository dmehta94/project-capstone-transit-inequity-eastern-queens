"""
realtime_data_collection.py

Fetches real-time bus location data for Eastern Queens bus routes from the
MTA BusTime SIRI API and saves each route's data to a separate CSV file.

Usage:
    python realtime_data_collection.py

Requirements:
    MTA_API_KEY environment variable must be set before running.
"""

import os
import requests
import pandas as pd
from datetime import datetime
from typing import Optional

# Route IDs for the 23 bus routes serving the Eastern Queens Transit Desert.
# Percent-encoding (%20) is required by the static data endpoint but stripped
# here since the SIRI API accepts plain route IDs (e.g., "MTA NYCT_Q27").
ROUTE_IDS: list[str] = [
    "MTA NYCT_Q1", "MTA NYCT_Q2", "MTA NYCT_Q3", "MTA NYCT_Q4",
    "MTA NYCT_Q5", "MTA NYCT_Q12", "MTA NYCT_Q13", "MTA NYCT_Q20A",
    "MTA NYCT_Q20B", "MTA NYCT_Q27", "MTA NYCT_Q28", "MTA NYCT_Q30",
    "MTA NYCT_Q31", "MTA NYCT_Q36", "MTA NYCT_Q43", "MTA NYCT_Q44+",
    "MTA NYCT_Q46", "MTA NYCT_Q76", "MTA NYCT_Q77", "MTA NYCT_Q83",
    "MTA NYCT_Q84", "MTA NYCT_Q85", "MTA NYCT_Q88"
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")


def fetch_realtime_data(route_id: str, api_key: str) -> Optional[pd.DataFrame]:
    """
    Fetch real-time vehicle location data for a single bus route.

    Sends a GET request to the MTA BusTime SIRI vehicle-monitoring endpoint
    and parses active vehicle positions. Returns None if no vehicles are
    currently active on the route or if the request fails.

    Args:
        route_id: MTA route identifier (e.g., 'MTA NYCT_Q27').
        api_key: MTA BusTime API key.

    Returns:
        DataFrame with columns: Route ID, Vehicle ID, Latitude, Longitude,
        Timestamp. Returns None if no active vehicles are found or the
        request fails.

    Example:
        >>> df = fetch_realtime_data("MTA NYCT_Q27", api_key)
        >>> if df is not None:
        ...     print(f"Found {len(df)} active vehicles on Q27.")
    """
    endpoint = "https://api.prod.obanyc.com/api/siri/vehicle-monitoring.json"
    params = {
        "key": api_key,
        "OperatorRef": "MTA",
        "MonitoringRef": "308209",
        "LineRef": route_id
    }

    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        vehicles = (
            data
            .get("Siri", {})
            .get("ServiceDelivery", {})
            .get("VehicleMonitoringDelivery", [{}])[0]
            .get("VehicleActivity", [])
        )

        if not vehicles:
            return None

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
        print(f"  Warning: could not fetch data for {route_id} — {e}")
        return None


def save_data_to_csv(data: pd.DataFrame, output_file: str) -> None:
    """
    Append a DataFrame to a CSV file, creating it if it does not exist.

    Creates any missing parent directories before writing. Appends without
    a header if the file already exists, preserving previously collected data
    across multiple collection runs.

    Args:
        data: DataFrame to save. Must be non-empty.
        output_file: Full path to the target CSV file.

    Example:
        >>> save_data_to_csv(df, "../data/realtime_data_MTA_NYCT_Q27.csv")
    """
    if data is None or data.empty:
        return

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(output_file):
        data.to_csv(output_file, mode="a", header=False, index=False)
    else:
        data.to_csv(output_file, index=False)


def collect_data_for_routes(route_ids: list[str], api_key: str) -> None:
    """
    Fetch and save real-time location data for a list of bus routes.

    For each route, fetches current vehicle positions and appends them to a
    per-route CSV file. File names use underscores in place of spaces for
    filesystem compatibility (e.g., 'MTA NYCT_Q27' → 'realtime_data_MTA_NYCT_Q27.csv').

    Args:
        route_ids: List of MTA route identifiers.
        api_key: MTA BusTime API key.

    Example:
        >>> collect_data_for_routes(ROUTE_IDS, api_key)
    """
    for route_id in route_ids:
        print(f"Fetching data for {route_id}...")
        data = fetch_realtime_data(route_id, api_key)

        if data is not None:
            # Replace spaces with underscores for a valid, consistent filename
            safe_route_id = route_id.replace(" ", "_")
            output_file = os.path.join(DATA_DIR, f"realtime_data_{safe_route_id}.csv")
            save_data_to_csv(data, output_file)
            print(f"  Saved {len(data)} records → {output_file}")
        else:
            print(f"  No active vehicles found for {route_id}.")


if __name__ == "__main__":
    api_key = os.getenv("MTA_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "MTA_API_KEY environment variable not set. "
            "Export it before running: export MTA_API_KEY='your_key_here'"
        )

    collect_data_for_routes(ROUTE_IDS, api_key)
