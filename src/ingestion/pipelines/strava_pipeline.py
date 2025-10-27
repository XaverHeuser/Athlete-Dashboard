"""This module orchestrates the entire EL process for Strava."""

import os

from google.auth import default
from google.auth.transport.requests import AuthorizedSession
import pandas as pd

from ingestion.auth import strava_auth
from ingestion.extractors.strava_extractor import StravaExtractor
from ingestion.loaders.bigquery_loader import BigQueryLoader


def trigger_dbt_job() -> None:
    project = 'athlete-dashboard-467718'
    region = 'europe-west1'
    job_name = 'dbt-job'

    url = f'https://{region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{project}/jobs/{job_name}:run'

    creds, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    authed_session = AuthorizedSession(creds)
    response = authed_session.post(url)

    if response.status_code == 200:
        print('Successfully triggered dbt-job')
    else:
        print(f'Failed to trigger dbt-job: {response.status_code} - {response.text}')


def run() -> None:
    """Executes the full Strava Extract and Load pipeline."""
    print('Starting Strava EL pipeline...')

    # Authenticate
    access_token = strava_auth.get_access_token()
    client = StravaExtractor(access_token=access_token)

    # Extract athlete info
    athlete_info = client.fetch_athlete_info()
    df_athlete_info = pd.DataFrame([athlete_info.model_dump()])

    # Extract athlete stats
    athlete_stats = client.fetch_athlete_stats(athlete_id=str(athlete_info.id))
    df_athlete_stats = pd.DataFrame([athlete_stats.model_dump()])

    # Extract activities
    activities_data = client.fetch_all_activities()
    df_activities = pd.DataFrame([a.model_dump() for a in activities_data])

    # Initialize BigQuery loader and load data
    loader = BigQueryLoader()
    try:
        if not df_athlete_info.empty:
            loader.load_data(
                data=df_athlete_info,
                dataset=os.environ.get('BIGQUERY_DATASET'),
                table_name=os.environ.get('BIGQUERY_RAW_ATHLETE_INFO'),
                write_disposition='WRITE_TRUNCATE',
            )

        if not df_athlete_stats.empty:
            loader.load_data(
                data=df_athlete_stats,
                dataset=os.environ.get('BIGQUERY_DATASET'),
                table_name=os.environ.get('BIGQUERY_RAW_ATHLETE_STATS'),
                write_disposition='WRITE_TRUNCATE',
            )

        if not df_activities.empty:
            loader.load_data(
                data=df_activities,
                dataset=os.environ.get('BIGQUERY_DATASET'),
                table_name=os.environ.get('BIGQUERY_RAW_ACTIVITIES'),
                write_disposition='WRITE_TRUNCATE',
            )

        print('Triggering dbt-job...')
        trigger_dbt_job()
    except Exception as e:
        print(f'Load failed. dbt-job not triggered. Error: {e}')
