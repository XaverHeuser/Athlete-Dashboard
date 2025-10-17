"""This module orchestrates the entire EL process for Strava."""

from ingestion.auth import strava_auth
from ingestion.extractors.strava_exctractor import StravaExtractor
from ingestion.loaders.bigquery_loader import BigQueryLoader


def run() -> None:
    """Executes the full Strava Extract and Load pipeline."""
    print('Starting Strava EL pipeline...')

    access_token = strava_auth.get_access_token(mode='cloud')

    client = StravaExtractor(access_token=access_token)
    activities_data = client.fetch_all_activities()

    if not activities_data:
        print('No new activities found. Pipeline finished.')
        return

    loader = BigQueryLoader()
    loader.load_data(data=activities_data)

    print('Strava EL pipeline finished successfully.')
