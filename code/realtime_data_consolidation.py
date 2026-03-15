"""
realtime_data_consolidation.py

Merges all per-route real-time CSV files collected by realtime_data_collection.py
into a single consolidated CSV, sorted by route, vehicle, and timestamp.

Usage:
    python realtime_data_consolidation.py
"""

import glob
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "combined_realtime_activity.csv")


def consolidate_realtime_data(
    data_dir: str = DATA_DIR,
    output_file: str = OUTPUT_FILE
) -> pd.DataFrame:
    """
    Merge all per-route real-time CSV files into a single sorted DataFrame.

    Searches for files matching the pattern 'realtime_data_MTA_NYCT_*.csv'
    in the specified directory, concatenates them, standardizes column names,
    parses timestamps, sorts by route/vehicle/time, and saves the result.

    Args:
        data_dir: Directory containing the per-route CSV files.
        output_file: Path to write the consolidated CSV.

    Returns:
        Consolidated DataFrame with columns: route_id, vehicle_id,
        vehicle_lat, vehicle_lon, timestamp.

    Raises:
        FileNotFoundError: If no matching CSV files are found in data_dir.

    Example:
        >>> df = consolidate_realtime_data()
        >>> print(f"Consolidated {len(df)} records across {df['route_id'].nunique()} routes.")
    """
    # Filenames use underscores — matches the naming convention in
    # realtime_data_collection.py (spaces replaced with underscores)
    pattern = os.path.join(data_dir, "realtime_data_MTA_NYCT_*.csv")
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            f"No real-time data files found matching pattern: {pattern}\n"
            "Run realtime_data_collection.py first to collect data."
        )

    print(f"Found {len(files)} file(s). Consolidating...")

    real_time_data = pd.concat(
        [pd.read_csv(f) for f in files],
        ignore_index=True
    )

    real_time_data = real_time_data.rename(
        columns={
            "Route ID": "route_id",
            "Vehicle ID": "vehicle_id",
            "Latitude": "vehicle_lat",
            "Longitude": "vehicle_lon",
            "Timestamp": "timestamp",
        }
    )

    real_time_data["route_id"] = real_time_data["route_id"].str.strip()
    real_time_data["timestamp"] = pd.to_datetime(real_time_data["timestamp"])

    real_time_data = real_time_data.sort_values(
        ["route_id", "vehicle_id", "timestamp"]
    ).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    real_time_data.to_csv(output_file, index=False)
    print(f"Saved {len(real_time_data)} records to '{output_file}'.")

    return real_time_data


if __name__ == "__main__":
    consolidate_realtime_data()
