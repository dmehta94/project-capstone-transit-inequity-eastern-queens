"""
static_data_collection.py

Collects static bus stop data for Eastern Queens bus routes from the MTA BusTime API
and saves results to a CSV file.

Usage:
    python static_data_collection.py

Requirements:
    MTA_API_KEY environment variable must be set before running.
"""

import os
import requests
import pandas as pd
from typing import Optional

# Route IDs for the 23 bus routes serving the Eastern Queens Transit Desert
ROUTE_IDS: list[str] = [
    "MTA%20NYCT_Q1", "MTA%20NYCT_Q2", "MTA%20NYCT_Q3", "MTA%20NYCT_Q4",
    "MTA%20NYCT_Q5", "MTA%20NYCT_Q12", "MTA%20NYCT_Q13", "MTA%20NYCT_Q20A",
    "MTA%20NYCT_Q20B", "MTA%20NYCT_Q27", "MTA%20NYCT_Q28", "MTA%20NYCT_Q30",
    "MTA%20NYCT_Q31", "MTA%20NYCT_Q36", "MTA%20NYCT_Q43", "MTA%20NYCT_Q44+",
    "MTA%20NYCT_Q46", "MTA%20NYCT_Q76", "MTA%20NYCT_Q77", "MTA%20NYCT_Q83",
    "MTA%20NYCT_Q84", "MTA%20NYCT_Q85", "MTA%20NYCT_Q88"
]

DEFAULT_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/stops.csv")


def fetch_stops_for_route(route_id: str, api_key: str) -> pd.DataFrame:
    """
    Fetch static stop data for a single bus route from the MTA BusTime API.

    Sends a GET request to the stops-for-route endpoint and parses the stop
    references from the response. Handles both list and dict response formats
    observed in the MTA API.

    Args:
        route_id: URL-encoded MTA route identifier (e.g., 'MTA%20NYCT_Q27').
        api_key: MTA BusTime API key.

    Returns:
        DataFrame with columns: Route ID, Stop ID, Stop Name, Latitude, Longitude.

    Raises:
        ValueError: If the API request fails or returns an unexpected data format.

    Example:
        >>> df = fetch_stops_for_route("MTA%20NYCT_Q27", api_key)
        >>> print(df.head())
    """
    endpoint = f"https://bustime.mta.info/api/where/stops-for-route/{route_id}.json"
    params = {
        "key": api_key,
        "includePolylines": "false",
        "version": "2"
    }

    response = requests.get(endpoint, params=params, timeout=10)

    if response.status_code != 200:
        raise ValueError(
            f"Failed to fetch data for {route_id}: HTTP {response.status_code}"
        )

    data = response.json()
    stops_data = data["data"]["references"]["stops"]

    if isinstance(stops_data, list):
        stops = [
            {
                "Route ID": route_id,
                "Stop ID": stop.get("id"),
                "Stop Name": stop.get("name"),
                "Latitude": stop.get("lat"),
                "Longitude": stop.get("lon")
            }
            for stop in stops_data
        ]
    elif isinstance(stops_data, dict):
        stops = [
            {
                "Route ID": route_id,
                "Stop ID": stop_id,
                "Stop Name": stop_info.get("name"),
                "Latitude": stop_info.get("lat"),
                "Longitude": stop_info.get("lon")
            }
            for stop_id, stop_info in stops_data.items()
        ]
    else:
        raise ValueError(
            f"Unexpected stops data format for {route_id}: {type(stops_data)}"
        )

    return pd.DataFrame(stops)


def collect_all_stops(
    route_ids: list[str],
    api_key: str,
    output_file: str = DEFAULT_OUTPUT_FILE
) -> Optional[pd.DataFrame]:
    """
    Collect stop data for all specified routes and save results to CSV.

    Iterates over route IDs, fetches stop data for each, and concatenates
    results into a single DataFrame. Routes that fail are skipped with a
    printed warning. Saves the combined data to the specified output path,
    creating parent directories if needed.

    Args:
        route_ids: List of URL-encoded MTA route identifiers.
        api_key: MTA BusTime API key.
        output_file: Path to save the combined CSV. Defaults to ../data/stops.csv
            relative to this script's location.

    Returns:
        Combined DataFrame of all stops, or None if no data was collected.

    Example:
        >>> df = collect_all_stops(ROUTE_IDS, api_key)
        >>> print(f"Collected {len(df)} stops across {df['Route ID'].nunique()} routes.")
    """
    all_stops = []

    for route_id in route_ids:
        print(f"Fetching stops for {route_id}...")
        try:
            stops_df = fetch_stops_for_route(route_id, api_key)
            all_stops.append(stops_df)
        except Exception as e:
            print(f"  Warning: skipping {route_id} — {e}")

    if not all_stops:
        print("No stop data collected. Check API key and network connection.")
        return None

    combined_df = pd.concat(all_stops, ignore_index=True)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Stop data saved to '{output_file}' ({len(combined_df)} stops).")

    return combined_df


if __name__ == "__main__":
    api_key = os.getenv("MTA_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "MTA_API_KEY environment variable not set. "
            "Export it before running: export MTA_API_KEY='your_key_here'"
        )

    collect_all_stops(ROUTE_IDS, api_key)
