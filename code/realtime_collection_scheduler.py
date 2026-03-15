"""
realtime_collection_scheduler.py

Runs the real-time bus data collection on a fixed interval using the
`schedule` library. Intended to be run as a background process for the
duration of a data collection period.

Usage:
    python realtime_collection_scheduler.py

    Leave running in a terminal for as long as you want to collect data.
    Press Ctrl+C to stop.

Requirements:
    MTA_API_KEY environment variable must be set before running.
    schedule library: pip install schedule
"""

import os
import time
from datetime import datetime

import schedule

from realtime_data_collection import ROUTE_IDS, collect_data_for_routes

# How often to poll the API (in minutes)
COLLECTION_INTERVAL_MINUTES = 30


def fetch_data_for_all_routes() -> None:
    """
    Fetch real-time bus location data for all Eastern Queens routes.

    Called automatically by the scheduler at each interval. Reads the API
    key from the environment and delegates to collect_data_for_routes().
    Prints a timestamped status message before and after each run.

    Raises:
        EnvironmentError: If MTA_API_KEY is not set.

    Example:
        >>> fetch_data_for_all_routes()  # Typically called by scheduler, not directly
    """
    api_key = os.getenv("MTA_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "MTA_API_KEY environment variable not set. "
            "Export it before running: export MTA_API_KEY='your_key_here'"
        )

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting collection...")
    collect_data_for_routes(ROUTE_IDS, api_key)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collection complete.")


if __name__ == "__main__":
    print(f"Scheduler started. Collecting every {COLLECTION_INTERVAL_MINUTES} minutes.")
    print("Press Ctrl+C to stop.\n")

    # Run once immediately so you don't wait a full interval for the first batch
    fetch_data_for_all_routes()

    schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(fetch_data_for_all_routes)

    while True:
        schedule.run_pending()
        time.sleep(1)
