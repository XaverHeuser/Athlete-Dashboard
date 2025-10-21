"""This module orchestrates the entire EL process for Strava."""

import re
from typing import Any

import pandas as pd

from ingestion.auth import strava_auth
from ingestion.extractors.strava_extractor import StravaExtractor
from ingestion.loaders.bigquery_loader import BigQueryLoader
from models.strava_activity_model import StravaActivity



def run() -> None:
    """Executes the full Strava Extract and Load pipeline."""
    print('Starting Strava EL pipeline...')

    access_token = strava_auth.get_access_token()

    client = StravaExtractor(access_token=access_token)
    activities_data = client.fetch_all_activities()

    if not activities_data:
        print('No new activities found. Pipeline finished.')
        return

    # Create dataframe from data
    df_activities = pd.DataFrame([a.model_dump() for a in activities_data])

    loader = BigQueryLoader()
    loader.load_data(data=df_activities)

    print('Strava EL pipeline finished successfully.')
