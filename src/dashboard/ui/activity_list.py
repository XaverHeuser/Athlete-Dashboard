"""Module to render a list of activities with inline detail expansion."""

from typing import Optional

import pandas as pd
from queries import load_activity_streams
import streamlit as st
from ui.activity_details import render_activity_details
from ui.constants import KPI_ICONS, PAGE_SIZE
from ui.formatters import (
    format_pace_min_per_km,
    format_seconds_to_hhmmss,
    format_speed_kph,
)
from ui.routing import (
    clear_selected_activity_id,
    get_selected_activity_id_int,
    set_selected_activity_id,
)
from ui.viz_helper_functions import show_activity_map, sport_badge


def render_activity_list(
    df: pd.DataFrame,
    *,
    title: Optional[str] = None,
    enable_pagination: bool = False,
    session_limit_key: str = 'activities_limit',
    page_size: int = PAGE_SIZE,
    key_prefix: str = 'act',
) -> None:
    """
    Render a list of activities with inline detail expansion.

    Args:
      df: Activities dataframe (must contain your fct_activities columns).
      title: Optional section title (markdown).
      enable_pagination: If True, show only first N rows, with "Load more".
      session_limit_key: Session state key for pagination limit.
      page_size: Increment for pagination.
      key_prefix: Prefix for Streamlit widget keys to avoid collisions across pages.
    """
    if df is None or df.empty:
        st.info('No activities to display.')
        return

    if title:
        st.markdown(title)

    # Pagination state (optional)
    if enable_pagination:
        if session_limit_key not in st.session_state:
            st.session_state[session_limit_key] = page_size
        df_visible = df.head(st.session_state[session_limit_key])
    else:
        df_visible = df

    selected_activity_id = get_selected_activity_id_int()

    for _, row in df_visible.iterrows():
        activity_id = row['activity_id']

        with st.container():
            cols = st.columns([1.4, 2])

            # Left column: summary info + buttons
            with cols[0]:
                st.subheader(row['activity_name'])
                st.caption(row['start_date_local'].strftime('%Y-%m-%d %H:%M'))

                sport_badge(row['sport_type'])

                # KPIs
                moving_time_str = format_seconds_to_hhmmss(int(row['moving_time_s']))
                pace_str = format_pace_min_per_km(row['avg_pace_min_per_km'])
                speed_str = format_speed_kph(row['avg_speed_kph'])

                colL, colR = st.columns(2)
                with colL:
                    st.markdown(f'{KPI_ICONS["time"]} **Time:** {moving_time_str} h')
                    st.markdown(
                        f'{KPI_ICONS["distance"]} **Distance:** {row["distance_km"]:.2f} km'
                    )
                    st.markdown(f'{KPI_ICONS["speed"]} **Avg pace:** {pace_str} min/km')
                with colR:
                    st.markdown(
                        f'{KPI_ICONS["heartrate"]} **Avg HR:** {row["avg_heartrate"]:.0f} bpm'
                    )
                    st.markdown(
                        f'{KPI_ICONS["elevation_gain"]} **Elevation gain:** {row["elevation_gain_m"]:.0f} m'
                    )
                    st.markdown(f'{KPI_ICONS["speed"]} **Avg tempo:** {speed_str} km/h')

                # Buttons: show either Open or Close for this row
                btn1, _btn2 = st.columns([1, 1])
                with btn1:
                    if selected_activity_id != activity_id:
                        if st.button(
                            'View details', key=f'{key_prefix}_open_{activity_id}'
                        ):
                            set_selected_activity_id(str(activity_id))
                            st.rerun()
                    else:
                        if st.button('Close', key=f'{key_prefix}_close_{activity_id}'):
                            clear_selected_activity_id()
                            st.rerun()

            # Right column: map expander
            # TODO: Fix
            with cols[1]:
                with st.expander('Show route'):
                    if pd.notna(row['map_polyline']):
                        show_activity_map(row['map_polyline'])
                    else:
                        st.caption('No map available')

            # Inline details (streams)
            if selected_activity_id == activity_id:
                with st.container(border=True):
                    try:
                        df_streams = load_activity_streams(activity_id)
                    except Exception as e:
                        st.error(f'Failed to load activity streams: {e}')
                        df_streams = pd.DataFrame()

                    render_activity_details(activity_row=row, df_streams=df_streams)

            st.divider()

    # Pagination controls
    if enable_pagination and st.session_state[session_limit_key] < len(df):
        if st.button('Load more activities', key=f'{key_prefix}_load_more'):
            st.session_state[session_limit_key] += page_size
            st.rerun()
