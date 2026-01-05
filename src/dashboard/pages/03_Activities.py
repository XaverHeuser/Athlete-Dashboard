"""Detailed activity list and exploration."""

import math

import pandas as pd
from queries import load_activities, load_activity_streams
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


# ------------------
# Configuration
# ------------------
st.set_page_config(page_title='Activities', page_icon='📋', layout='wide')

if 'activities_limit' not in st.session_state:
    st.session_state.activities_limit = PAGE_SIZE


# --------------
# Load data
# --------------
try:
    df_activities = load_activities()
    if df_activities.empty:
        st.warning('No activities found.')
        st.stop()
except Exception as e:
    st.error(f'Failed to load activities: {e}')
    st.stop()


# -------------
# Filters
# -------------
st.title('All Activities')

# First filter row
row1_col1, row1_col2, row1_col3 = st.columns([2, 1, 1])

# Search text
with row1_col1:
    search_text = st.text_input('Search activity name')

# Year dropdown
with row1_col2:
    year_options = ['All'] + sorted(
        df_activities['activity_year'].dropna().unique().tolist(), reverse=True
    )
    year_filter = st.selectbox('Year', options=year_options)

# Month dropdown
with row1_col3:
    if year_filter != 'All':
        month_options = ['All'] + sorted(
            df_activities.loc[
                df_activities['activity_year'] == year_filter, 'activity_month'
            ]
            .dropna()
            .unique()
            .tolist()
        )
    else:
        month_options = ['All']
    month_filter = st.selectbox('Month', options=month_options)

# Second filter row
row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 2])

# Sport type dropdown
with row2_col1:
    sport_filter = st.selectbox(
        'Sport Type',
        options=['All']
        + sorted(df_activities['sport_type'].dropna().unique().tolist()),
    )

# Distance slider
dist_max = float(math.ceil(df_activities['distance_km'].dropna().max()))
with row2_col2:
    min_dist, max_dist = st.slider(
        'Distance (km)',
        min_value=0.0,
        max_value=dist_max,
        value=(0.0, dist_max),
        step=1.0,
    )

# Moving time slider
time_max = int(math.ceil(df_activities['moving_time_s'].dropna().max() / 60))
with row2_col3:
    min_time, max_time = st.slider(
        'Moving Time (min)',
        min_value=0,
        max_value=time_max,
        value=(0, time_max),
        step=5,
    )

# Summary of applied filters
st.caption(
    f'Filters: {year_filter}'
    f'{" · " + str(month_filter) if month_filter != "All" else ""} · '
    f'{sport_filter} · {min_dist:.0f}-{max_dist:.0f} km · {min_time}-{max_time} min'
)

# =========================
# Apply filters
# =========================
filtered = df_activities.copy()

# Apply filters one by one
if search_text:
    filtered = filtered[
        filtered['activity_name'].str.contains(search_text, case=False, na=False)
    ]
if year_filter != 'All':
    filtered = filtered[filtered['activity_year'] == year_filter]
if month_filter != 'All':
    filtered = filtered[filtered['activity_month'] == month_filter]
if sport_filter != 'All':
    filtered = filtered[filtered['sport_type'] == sport_filter]

filtered = filtered[
    (filtered['distance_km'] >= min_dist) & (filtered['distance_km'] <= max_dist)
]
filtered = filtered[
    (filtered['moving_time_s'] >= min_time * 60)
    & (filtered['moving_time_s'] <= max_time * 60)
]

# Sort by date descending
filtered = filtered.sort_values('activity_date_local', ascending=False).reset_index(
    drop=True
)

# --------------------------------
# Selected activity (from URL)
# --------------------------------
selected_activity_id_int = get_selected_activity_id_int()

# ----------------------------
# Activity cards + details
# ----------------------------
st.divider()
visible = filtered.head(st.session_state.activities_limit)

for _, row in visible.iterrows():
    activity_id = row['activity_id']

    with st.container():
        cols = st.columns([1.4, 2])

        # Left column: summary + buttons
        with cols[0]:
            st.subheader(row['activity_name'])
            st.caption(row['start_date_local'].strftime('%Y-%m-%d %H:%M'))

            sport_badge(row['sport_type'])

            moving_time_str = format_seconds_to_hhmmss(row['moving_time_s'])
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

            # Buttons: show either Open or Close for THIS row
            btn1, btn2 = st.columns([1, 1])
            with btn1:
                if selected_activity_id_int != activity_id:
                    if st.button('View details', key=f'open_{activity_id}'):
                        set_selected_activity_id(str(activity_id))
                        st.rerun()
                else:
                    if st.button('Close', key=f'close_{activity_id}'):
                        clear_selected_activity_id()
                        st.rerun()

        # Right column: map
        # TODO: Fix
        with cols[1]:
            with st.expander('Show route'):
                if pd.notna(row['map_polyline']):
                    show_activity_map(row['map_polyline'])
                else:
                    st.caption('No map available')

        # ---- INLINE DETAILS: only for the selected row ----
        if selected_activity_id_int == activity_id:
            with st.container(border=True):
                try:
                    df_streams = load_activity_streams(activity_id)
                except Exception as e:
                    st.error(f'Failed to load activity streams: {e}')
                    df_streams = pd.DataFrame()

                render_activity_details(activity_row=row, df_streams=df_streams)

        st.divider()

# ----------------
# Pagination
# ----------------
if st.session_state.activities_limit < len(filtered):
    if st.button('Load more activities'):
        st.session_state.activities_limit += PAGE_SIZE
        st.rerun()
