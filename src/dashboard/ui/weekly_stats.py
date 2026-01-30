"""File for computing weekly activity stats."""

import pandas as pd
from queries import load_activities_weekly
import streamlit as st


# -----------------------
# Load and prepare data
# ------------------------
@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def load_prepare_activities_weekly() -> pd.DataFrame:
    """Load and prepare activities weekly"""
    # Load data
    df_raw = load_activities_weekly()
    if df_raw.empty:
        return pd.DataFrame()

    # Convert to datetime
    df_raw['activity_week'] = pd.to_datetime(df_raw['activity_week'])
    return df_raw


# ---------------------------------
# Compute weekly dfs and stats
# ---------------------------------
def compute_weekly_dfs(
    df_activities_weekly: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute df for current week and last 4 weeks."""
    # Get latest week and previous week
    latest_week = df_activities_weekly['activity_week'].max()
    previous_week = latest_week - pd.Timedelta(days=7)

    # Get data for current and previous week
    df_current = df_activities_weekly[
        df_activities_weekly['activity_week'] == latest_week
    ]
    df_previous = df_activities_weekly[
        df_activities_weekly['activity_week'] == previous_week
    ]

    # Create df last 4 weeks
    available_weeks = (
        df_activities_weekly['activity_week'].drop_duplicates().sort_values()
    )
    last_8_weeks = available_weeks.tail(8)
    df_last_8_weeks = df_activities_weekly[
        df_activities_weekly['activity_week'].isin(last_8_weeks)
    ].copy()

    return df_current, df_previous, df_last_8_weeks


def compute_weekly_stats(
    df_current: pd.DataFrame, df_previous: pd.DataFrame
) -> tuple[int, float, int, float]:
    """Compute weekly hours, distance and delta to previuos week."""
    # Weekly hours
    current_hours = df_current['total_moving_time_h'].sum()
    previous_hours = df_previous['total_moving_time_h'].sum()
    delta_hours = current_hours - previous_hours

    # Weekly distance
    current_distance = df_current['total_distance_km'].sum()
    previous_distance = df_previous['total_distance_km'].sum()
    delta_distance = current_distance - previous_distance

    return current_hours, delta_hours, current_distance, delta_distance
