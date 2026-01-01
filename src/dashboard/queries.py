"""Central module for loading data from BigQuery for the Streamlit dashboard."""

import os
import re

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st


load_dotenv()

# CONSTANTS
_ALLOWED_TABLES = {
    'dim_athlete_info',
    'dim_gear',
    'fct_activities',
    'fct_activity_streams',
    'fct_activities_daily',
    'fct_activities_weekly',
    'fct_activities_monthly',
    'fct_activities_yearly',
    'fct_athlete_stats',
    'fct_athlete_stats_latest',
    'fct_athlete_stats_snapshot'
}
_ID_RE = re.compile(r'^[A-Za-z0-9_]+$')

_GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
_BQ_DATASET_MARTS = os.getenv('BIGQUERY_DATASET_MARTS')


# Helper to format table names
def _safe_table_name(name: str) -> str:
    """Validate and return safe table name."""
    if name not in _ALLOWED_TABLES:
        raise ValueError(f'Table not allowlisted: {name}')
    # optional zusätzliche harte Validierung
    if not _ID_RE.fullmatch(name):
        raise ValueError(f'Invalid table identifier: {name}')
    return name


def _table(name: str) -> str:
    """Helper to format full table names."""
    name = _safe_table_name(name)
    return f'`{_GCP_PROJECT_ID}.{_BQ_DATASET_MARTS}.{name}`'


# BIGQUERY CLIENT
try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets['gcp_service_account']
    )
    client = bigquery.Client(credentials=creds, project=creds.project_id)
except Exception:
    # Local dev fallback (requires GOOGLE_APPLICATION_CREDENTIALS)
    client = bigquery.Client()


# ------------------------------
# DATA LOADING QUERIES
# ------------------------------
@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_athlete_data() -> pd.DataFrame:
    """Load athlete metadata (one row per athlete)."""
    table_fqn = _table('dim_athlete_info')
    query = f'SELECT * FROM {table_fqn}'  # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_athlete_stats() -> pd.DataFrame:
    """Load the latest athlete statistics snapshot."""
    table_fqn = _table('fct_athlete_stats')
    query = f'SELECT * FROM {table_fqn}'  # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_activities() -> pd.DataFrame:
    """Load all activities from fact table."""
    table_fqn = _table('fct_activities')
    query = f'SELECT * FROM {table_fqn} ORDER BY start_date_local DESC'  # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_gear_details() -> pd.DataFrame:
    """Load gear details from dimension table."""
    table_fqn = _table('dim_gear')
    query = f'SELECT * FROM {table_fqn}'  # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_weekly_summary(
    start_week: str | None = None, end_week: str | None = None
) -> pd.DataFrame:
    """
    Load weekly summary statistics for the athlete.
    """
    table_fqn = _table('fct_activities_weekly')
    query = f"""
        SELECT
            sport_type,
            activity_week,
            total_distance_km,
            total_moving_time_h,
        FROM {table_fqn}
        WHERE 1 = 1
    """  # nosec B608: table_fqn is built from allowlisted identifiers only
    params = {}

    if start_week:
        query += ' AND activity_week >= %(start_week)s'
        params['start_week'] = start_week

    if end_week:
        query += ' AND activity_week <= %(end_week)s'
        params['end_week'] = end_week

    query += ' ORDER BY activity_week'  # nosec B608: table_fqn is built from allowlisted identifiers only

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    return client.query(query, job_config=job_config).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_activity_streams(activity_id: int) -> pd.DataFrame:
    """
    Load time-series streams for a single activity.
    """
    table_fqn = _table('fct_activity_streams')
    query = f"""
        SELECT
            sequence_index,
            time_s,
            distance_m,
            heartrate_bpm,
            velocity_smooth_mps,
            altitude_m,
            cadence_rpm,
            power_w,
            grade_smooth_pct,
            lat,
            lng
        FROM {table_fqn}
        WHERE activity_id = @activity_id
        ORDER BY sequence_index
    """  # nosec B608: table_fqn is built from allowlisted identifiers only

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('activity_id', 'INT64', activity_id)
        ]
    )

    return client.query(query, job_config=job_config).to_dataframe()
