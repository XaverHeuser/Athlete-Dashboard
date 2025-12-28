"""Central module for loading data from BigQuery for the Streamlit dashboard."""

import os

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st
import re

load_dotenv()

# CONSTANTS
_ALLOWED_TABLES = {
    "dim_athlete_info",
    "fct_athlete_stats_latest",
    "fct_activities_daily",
    "fct_activities_weekly",
    "fct_activities_monthly",
    "fct_activities_yearly",
}
_ID_RE = re.compile(r"^[A-Za-z0-9_]+$")

_GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
_BQ_DATASET_MARTS = os.getenv('BIGQUERY_DATASET_MARTS')


# Helper to format table names
def _safe_table_name(name: str) -> str:
    """Validate and return safe table name."""
    if name not in _ALLOWED_TABLES:
        raise ValueError(f"Table not allowlisted: {name}")
    # optional zusätzliche harte Validierung
    if not _ID_RE.fullmatch(name):
        raise ValueError(f"Invalid table identifier: {name}")
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
    query = f'SELECT * FROM {table_fqn}' # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_latest_stats() -> pd.DataFrame:
    """Load the latest athlete statistics snapshot."""
    table_fqn = _table('fct_athlete_stats_latest')
    query = f'SELECT * FROM {table_fqn}' # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_stats_history() -> pd.DataFrame:
    """Load all historical athlete statistics snapshots."""
    table_fqn = _table('fct_athlete_stats_snapshot')
    query = f'SELECT * FROM {table_fqn} ORDER BY snapshot_date' # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_activities() -> pd.DataFrame:
    """Load all activities from fact table."""
    table_fqn = _table('fct_activities')
    query = f'SELECT * FROM {table_fqn} ORDER BY start_date_local DESC' # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_gear_details() -> pd.DataFrame:
    """Load gear details from dimension table."""
    table_fqn = _table('dim_gear')
    query = f'SELECT * FROM {table_fqn}' # nosec B608: table_fqn is built from allowlisted identifiers only
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_time_series(
    granularity: str,
    metric: str,
    sport_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    table_map = {
        'daily': 'fct_activities_daily',
        'weekly': 'fct_activities_weekly',
        'monthly': 'fct_activities_monthly',
        'yearly': 'fct_activities_yearly',
    }

    time_col_map = {
        'daily': 'activity_date',
        'weekly': 'activity_week',
        'monthly': 'activity_month',
        'yearly': 'activity_year',
    }

    allowed_metrics = {'total_distance_km', 'total_moving_time_h', 'total_activities'}

    if granularity not in table_map:
        raise ValueError('Invalid granularity')
    if metric not in allowed_metrics:
        raise ValueError('Invalid metric')

    table_fqn = _table(table_map[granularity])
    time_col = time_col_map[granularity]

    conditions: list[str] = []
    params: list[bigquery.ScalarQueryParameter] = []

    if sport_type:
        conditions.append('sport_type = @sport_type')
        params.append(bigquery.ScalarQueryParameter('sport_type', 'STRING', sport_type))

    if start_date and end_date:
        conditions.append(f'{time_col} BETWEEN @start_date AND @end_date')
        params.extend([
            bigquery.ScalarQueryParameter('start_date', 'DATE', start_date),
            bigquery.ScalarQueryParameter('end_date', 'DATE', end_date),
        ])

    where_clause = f'WHERE {" AND ".join(conditions)}' if conditions else ''

    query = f"""
        SELECT
            {time_col} AS period,
            SUM({metric}) AS value
        FROM {table_fqn}
        {where_clause}
        GROUP BY period
        ORDER BY period
    """  # nosec B608: table_fqn is built from allowlisted identifiers only

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    return client.query(query, job_config=job_config).to_dataframe()


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
    """ # nosec B608: table_fqn is built from allowlisted identifiers only
    params = {}

    if start_week:
        query += ' AND activity_week >= %(start_week)s'
        params['start_week'] = start_week

    if end_week:
        query += ' AND activity_week <= %(end_week)s'
        params['end_week'] = end_week

    query += ' ORDER BY activity_week' # nosec B608: table_fqn is built from allowlisted identifiers only

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    return client.query(query, job_config=job_config).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_sport_types() -> list[str]:
    """
    Load distinct sport types from activity facts.
    """
    table_fqn = _table('fct_activities_daily')
    query = f"""
        SELECT DISTINCT sport_type
        FROM {table_fqn}
        WHERE sport_type IS NOT NULL
        ORDER BY sport_type
    """ # nosec B608: table_fqn is built from allowlisted identifiers only

    df: pd.DataFrame = client.query(query).to_dataframe()

    sport_types: list[str] = [str(x) for x in df['sport_type'].dropna().tolist()]

    return sport_types


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
    """ # nosec B608: table_fqn is built from allowlisted identifiers only

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter('activity_id', 'INT64', activity_id)
        ]
    )

    return client.query(query, job_config=job_config).to_dataframe()
