"""This module includes queries from bigquery for streamlit."""

from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st

try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets['gcp_service_account']
    )
    client = bigquery.Client(credentials=creds, project=creds.project_id)
except Exception:
    # Fallback for local development
    # GOOGLE_APPLICATION_CREDENTIALS environment variable must be set
    client = bigquery.Client()


@st.cache_data # type: ignore[misc]
def load_raw_data() -> pd.DataFrame:
    """Queries the BigQuery table and returns the data as a Pandas DataFrame."""
    # Define your BigQuery SQL query
    query = """
        SELECT * FROM `athlete-dashboard-467718.strava_data.strava_activities_raw`
    """
    print('Running BigQuery query...')
    # Run the query and convert the result to a Pandas DataFrame
    df = client.query(query).to_dataframe()
    return df
