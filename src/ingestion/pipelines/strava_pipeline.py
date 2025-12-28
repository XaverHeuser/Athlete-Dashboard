"""This module orchestrates the entire EL process for Strava."""

from datetime import datetime, timezone
import os
from typing import Any

from google.auth import default
from google.auth.transport.requests import AuthorizedSession
import pandas as pd

from ingestion.auth import strava_auth
from ingestion.extractors.strava_extractor import StravaExtractor
from ingestion.loaders.bigquery_loader import BigQueryLoader
from ingestion.schemas.strava_activity_streams_schema import ACTIVITY_STREAMS_SCHEMA
from ingestion.transformers.strava_streams import explode_streams


def trigger_dbt_job() -> None:
    project = os.environ.get('GCP_PROJECT_ID')
    region = os.environ.get('GCP_REGION')
    dbt_job_name = os.environ.get('CLOUD_RUN_DBT_JOB_NAME')

    url = f'https://{region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{project}/jobs/{dbt_job_name}:run'

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

    ingested_at = datetime.now(timezone.utc)

    # Authenticate
    access_token = strava_auth.get_access_token()
    client = StravaExtractor(access_token=access_token)

    # Initialize BigQuery loader and load data
    loader = BigQueryLoader()

    # Extract athlete info
    athlete_info = client.fetch_athlete_info()
    df_athlete_info = pd.DataFrame([athlete_info.model_dump()])

    # Extract athlete stats
    athlete_stats = client.fetch_athlete_stats(athlete_id=str(athlete_info.id))
    df_athlete_stats = pd.DataFrame([athlete_stats.model_dump()])

    # Extract activities
    activities_data = client.fetch_all_activities(days=3)
    df_activities = pd.DataFrame([
        {**a.model_dump(), 'ingested_at': ingested_at} for a in activities_data
    ])

    # Extract streams
    BATCH_SIZE = 5
    buffer: list[dict[str, Any]] = []

    for activity in activities_data:
        streams = explode_streams(
            activity.id, client.fetch_activity_streams(activity_id=str(activity.id))
        )
        buffer.extend({**r.model_dump(), 'ingested_at': ingested_at} for r in streams)

        if len(buffer) >= BATCH_SIZE * 5000:
            df = pd.DataFrame(buffer)
            loader.load_data(
                data=df,
                dataset=os.environ.get('BIGQUERY_DATASET'),
                table_name=os.environ.get('BIGQUERY_RAW_ACTIVITY_STREAMS'),
                write_disposition='WRITE_APPEND',
                schema=ACTIVITY_STREAMS_SCHEMA,
            )
            buffer.clear()

    # Extract gear details
    gear_details = []
    for gear_id in df_activities['gear_id'].unique():
        if gear_id and gear_id is not None:
            gear = client.fetch_gear_details(gear_id=gear_id)
            gear_details.append({**gear.model_dump(), 'ingested_at': ingested_at})
    df_gear_details = pd.DataFrame(gear_details)

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
                write_disposition='WRITE_APPEND',
            )

        if not df_gear_details.empty:
            loader.load_data(
                data=df_gear_details,
                dataset=os.environ.get('BIGQUERY_DATASET'),
                table_name=os.environ.get('BIGQUERY_RAW_GEAR_DETAILS'),
                write_disposition='WRITE_APPEND',
            )

        print('Triggering dbt-job...')
        trigger_dbt_job()
    except Exception as e:
        print(f'Load failed. dbt-job not triggered. Error: {e}')
