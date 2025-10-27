"""Central module for loading data from BigQuery for the Streamlit dashboard."""

from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import streamlit as st

# --- BigQuery client setup ---
try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=creds, project=creds.project_id)
except Exception:
    # Local dev fallback: GOOGLE_APPLICATION_CREDENTIALS must be set
    client = bigquery.Client()


# ---------- Queries ----------

@st.cache_data(show_spinner=False)
def load_athlete_data() -> pd.DataFrame:
    """Load athlete metadata (one row per athlete)."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.dim_athlete_info`
    """
    return client.query(query).to_dataframe()


@st.cache_data(show_spinner=False)
def load_latest_stats() -> pd.DataFrame:
    """Load the latest athlete statistics snapshot (one row per athlete)."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.fct_athlete_stats_latest`
    """
    return client.query(query).to_dataframe()


@st.cache_data(show_spinner=False)
def load_stats_history() -> pd.DataFrame:
    """Load all historical athlete statistics snapshots."""
    query = """
        SELECT *
        FROM `athlete-dashboard-467718.strava_marts.fct_athlete_stats_snapshot`
        ORDER BY snapshot_date
    """
    return client.query(query).to_dataframe()
