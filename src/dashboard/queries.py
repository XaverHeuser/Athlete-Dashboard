"""Central module for loading data from BigQuery for the Streamlit dashboard."""

from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st

# --- BigQuery client setup ---
try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets['gcp_service_account']
    )
    client = bigquery.Client(credentials=creds, project=creds.project_id)
except Exception:
    # Local dev fallback (requires GOOGLE_APPLICATION_CREDENTIALS)
    client = bigquery.Client()


# ---------- Queries ----------


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_athlete_data() -> pd.DataFrame:
    """Load athlete metadata (one row per athlete)."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.dim_athlete_info`
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_latest_stats() -> pd.DataFrame:
    """Load the latest athlete statistics snapshot."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.fct_athlete_stats_latest`
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_stats_history() -> pd.DataFrame:
    """Load all historical athlete statistics snapshots."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.fct_athlete_stats_snapshot`
        ORDER BY snapshot_date
    """
    return client.query(query).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_activities() -> pd.DataFrame:
    """Load all activities from fact table."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.fct_activities`
        ORDER BY start_date_local DESC
    """
    return client.query(query).to_dataframe()
