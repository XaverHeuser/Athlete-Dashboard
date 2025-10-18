"""This module orchestrates the entire EL process for Strava."""

import re
from typing import Any

import pandas as pd

from ingestion.auth import strava_auth
from ingestion.extractors.strava_exctractor import StravaExtractor
from ingestion.loaders.bigquery_loader import BigQueryLoader


def _preprocess_strava_data(data: list[dict[str, Any]]) -> pd.DataFrame:
    """Flattens nested JSON and cleans column names for BigQuery compatibility."""
    if not data:
        return []

    # Flatten columns from JSON
    df_raw = pd.json_normalize(data)

    # Clean column names
    df_cleaned = df_raw.copy()
    df_cleaned.columns = [
        re.sub(r'[^a-zA-Z0-9_]', '_', col) for col in df_cleaned.columns
    ]

    print('Cleaned column names for BigQuery.')
    return df_cleaned


def run() -> None:
    """Executes the full Strava Extract and Load pipeline."""
    print('Starting Strava EL pipeline...')

    access_token = strava_auth.get_access_token()

    client = StravaExtractor(access_token=access_token)
    activities_data = client.fetch_all_activities()

    if not activities_data:
        print('No new activities found. Pipeline finished.')
        return

    df_activities_to_load = _preprocess_strava_data(activities_data)

    loader = BigQueryLoader()
    loader.load_data(data=df_activities_to_load)

    print('Strava EL pipeline finished successfully.')
