"""This module orchestrates the entire EL process for Strava."""

from google.auth import default
from google.auth.transport.requests import AuthorizedSession
import pandas as pd

from ingestion.auth import strava_auth
from ingestion.extractors.strava_extractor import StravaExtractor
from ingestion.loaders.bigquery_loader import BigQueryLoader


def trigger_dbt_job():
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

    access_token = strava_auth.get_access_token()
    client = StravaExtractor(access_token=access_token)
    activities_data = client.fetch_all_activities()

    if not activities_data:
        print('No new activities found. Pipeline finished.')
        return

    # Create dataframe from data
    df_activities = pd.DataFrame([a.model_dump() for a in activities_data])

    loader = BigQueryLoader()

    try:
        loader.load_data(data=df_activities)
        print('Load successful. Triggering dbt-job...')
        trigger_dbt_job()
    except Exception as e:
        print(f'Load failed. dbt-job not triggered. Error: {e}')
