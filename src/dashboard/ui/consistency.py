""""""

from typing import Optional

import altair as alt
import pandas as pd
from queries import (
    load_consistency_multisport_weekly_data,
    load_consistency_weekly_data,
)
import streamlit as st
from ui.constants import MAIN_DISCIPLINES


# -----------------------------
# Configuration
# -----------------------------
DEFAULT_WINDOW_WEEKS = 52


# -----------------------------
# Single-call orchestration
# -----------------------------
def show_consistency_heatmap(
    *, window_weeks: int = DEFAULT_WINDOW_WEEKS, title: Optional[str] = None
) -> None:
    """Single-call orchestration for Streamlit pages."""
    df_weekly_window = create_consistency_dataframe(window_weeks=window_weeks)

    if df_weekly_window.empty:
        st.info('No consistency data available yet.')
        return

    chart_title = title or f'Weekly status by discipline (last {window_weeks} weeks)'
    heatmap_chart = render_consistency_heatmap(df_weekly_window, title=chart_title)

    st.altair_chart(heatmap_chart)


# --------------------------------
# Data preparation and rendering
# --------------------------------
@st.cache_data(ttl=3600, show_spinner=False)  # type: ignore[misc]
def create_consistency_dataframe(
    *, window_weeks: int = DEFAULT_WINDOW_WEEKS
) -> pd.DataFrame:
    """Load and prepare weekly consistency data for visualization (cached)."""
    df_raw = load_consistency_weekly_data()
    if df_raw.empty:
        return pd.DataFrame()

    # Restrict to last N weeks based on the maximum week present in the data.
    max_week = df_raw['activity_week'].max()
    window_start = max_week - pd.Timedelta(weeks=window_weeks)
    df_window = df_raw[df_raw['activity_week'] >= window_start].copy()

    return df_window


def render_consistency_heatmap(
    df_weekly_window: pd.DataFrame, *, title: str = ''
) -> alt.Chart:
    """Render a weekly consistency heatmap."""
    if df_weekly_window.empty:
        # Return an empty chart that won't break Streamlit rendering.
        return alt.Chart(pd.DataFrame({'x': [], 'y': []})).mark_text().encode()

    data = df_weekly_window.copy()

    # Tile width: [week_start, week_end)
    data['activity_week_end'] = data['activity_week'] + pd.Timedelta(days=7)

    # Robust color scale max: avoid outliers flattening the gradient.
    hours = data['total_moving_time_h'].fillna(0.0)
    max_hours = _robust_quantile(hours, q=0.95, fallback=1.0)

    # Dynamic height (avoid label overlap)
    chart_height = _heatmap_height(n_rows=len(MAIN_DISCIPLINES))

    heatmap = (
        alt.Chart(data)
        .mark_rect(stroke='#e6e6e6', strokeWidth=0.6)
        .encode(
            x=alt.X(
                'activity_week:T',
                title=None,
                axis=alt.Axis(
                    format='%Y-%m', tickCount='month', labelAngle=0, labelOverlap=True
                ),
            ),
            x2=alt.X2('activity_week_end:T'),
            y=alt.Y(
                'discipline:N',
                title=None,
                sort=MAIN_DISCIPLINES,
                axis=alt.Axis(labelLimit=220, labelPadding=8, labelOverlap=False),
            ),
            # Make "zero weeks" clearly inactive (gray), and "active weeks" green gradient by hours
            color=alt.condition(
                'datum.total_moving_time_h == 0',
                alt.value('#f3f3f3'),
                alt.Color(
                    'total_moving_time_h:Q',
                    title='Hours',
                    scale=alt.Scale(domain=[0, max_hours], scheme='greens', clamp=True),
                    legend=alt.Legend(orient='right'),
                ),
            ),
            tooltip=[
                alt.Tooltip('activity_week:T', title='Week start'),
                alt.Tooltip('discipline:N', title='Discipline'),
                alt.Tooltip('total_activities:Q', title='Sessions'),
                alt.Tooltip('total_moving_time_h:Q', title='Hours', format='.2f'),
                alt.Tooltip('total_distance_km:Q', title='Distance (km)', format='.1f'),
                alt.Tooltip(
                    'total_elevation_gain_m:Q', title='Elevation gain (m)', format='.1f'
                ),
            ],
        )
        .properties(title=title, height=chart_height)
    )

    return heatmap


# --------------------
# Weekly Multisport
# --------------------
def compute_weekly_multisport_stats() -> tuple[float, int, int]:
    """Compute multisport stats."""
    df_multisport = load_consistency_multisport_weekly_data()

    if df_multisport.empty:
        # return all4_cov, all4_current, all4_longest
        return 0.0, 0, 0

    df_multisport['activity_week'] = pd.to_datetime(df_multisport['activity_week'])

    # Get last 52 weeks
    # TODO: Check for unification?!
    max_week = df_multisport['activity_week'].max()
    window_start = max_week - pd.Timedelta(weeks=52)

    df_multisport_window = df_multisport[
        df_multisport['activity_week'] >= window_start
    ].copy()
    all4_cov = (
        float(df_multisport_window['all4_covered'].mean())
        if 'all4_covered' in df_multisport_window.columns
        else 0.0
    )

    streak_all4 = (
        df_multisport_window.sort_values('activity_week')['all4_covered']
        if 'all4_covered' in df_multisport_window.columns
        else pd.Series([])
    )
    all4_current = _current_streak(streak_all4) if len(streak_all4) else 0
    all4_longest = _longest_streak(streak_all4) if len(streak_all4) else 0
    delta_weeks = all4_current - all4_longest

    return all4_cov, all4_current, delta_weeks


# -----------------------------
# Internal helpers
# -----------------------------
def _robust_quantile(series: pd.Series, *, q: float, fallback: float) -> float:
    """Compute a robust upper bound for color scaling."""
    try:
        val = float(series.quantile(q))
        return val if val > 0 else fallback
    except Exception:
        return fallback


def _heatmap_height(*, n_rows: int) -> int:
    """Determine a reasonable chart height for categorical rows."""
    row_height_px = 26
    min_height_px = 160
    return max(min_height_px, row_height_px * n_rows + 40)


def _current_streak(binary_series: pd.Series) -> int:
    """Calculate the current streak of consecutive True (1) values in a binary series."""
    s = binary_series.astype(int).tolist()
    streak = 0
    for v in reversed(s):
        if v == 1:
            streak += 1
        else:
            break
    return streak


def _longest_streak(binary_series: pd.Series) -> int:
    """Calculate the longest streak of consecutive True (1) values in a binary series."""
    longest = run = 0
    for v in binary_series.astype(int).tolist():
        if v == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return longest
