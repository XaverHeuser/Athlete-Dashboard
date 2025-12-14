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


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_time_series(
    granularity: str,
    metric: str,
    sport_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:

    table_map = {
        "daily": "athlete-dashboard-467718.strava_marts.fct_activities_daily",
        "weekly": "athlete-dashboard-467718.strava_marts.fct_activities_weekly",
        "monthly": "athlete-dashboard-467718.strava_marts.fct_activities_monthly",
        "yearly": "athlete-dashboard-467718.strava_marts.fct_activities_yearly",
    }

    time_col_map = {
        "daily": "activity_date",
        "weekly": "activity_week",
        "monthly": "activity_month",
        "yearly": "activity_year",
    }

    if granularity not in table_map:
        raise ValueError("Invalid granularity")

    if metric not in {
        "total_distance_m",
        "total_activities",
        "total_moving_time_s",
    }:
        raise ValueError("Invalid metric")

    table = table_map[granularity]
    time_col = time_col_map[granularity]

    conditions = []
    params = []

    if sport_type:
        conditions.append("sport_type = @sport_type")
        params.append(
            bigquery.ScalarQueryParameter("sport_type", "STRING", sport_type)
        )

    if start_date and end_date:
        conditions.append(f"{time_col} BETWEEN @start_date AND @end_date")
        params.extend(
            [
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""  # nosec B608: metric, table and columns are allowlisted; values are parameterized
        SELECT
            {time_col} AS period,
            SUM({metric}) AS value
        FROM `{table}`
        {where_clause}
        GROUP BY period
        ORDER BY period
    """

    job_config = bigquery.QueryJobConfig(query_parameters=params)

    return client.query(query, job_config=job_config).to_dataframe()


@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_sport_types() -> list[str]:
    """
    Load distinct sport types from activity facts.
    """
    query = """
        SELECT DISTINCT sport_type
        FROM `athlete-dashboard-467718.strava_marts.fct_activities_daily`
        WHERE sport_type IS NOT NULL
        ORDER BY sport_type
    """

    df: pd.DataFrame = client.query(query).to_dataframe()

    sport_types: list[str] = [str(x) for x in df['sport_type'].dropna().tolist()]

    return sport_types
