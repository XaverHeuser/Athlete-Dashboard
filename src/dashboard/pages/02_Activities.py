"""Detailed activity list and exploration."""

import math

from queries import load_activities
import streamlit as st
from ui.activity_list import render_activity_list
from ui.routing import get_selected_activity_id_int


# ------------------
# Configuration
# ------------------
st.set_page_config(page_title='Activities', page_icon='📋', layout='wide')

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
        'Discipline',
        options=['All']
        + sorted(df_activities['discipline'].dropna().unique().tolist()),
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

# ------------------
# Apply filters
# ------------------
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
    filtered = filtered[filtered['discipline'] == sport_filter]

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
# Activity list
# ----------------------------
st.divider()
render_activity_list(
    filtered,
    title='### 🏃 Activities',
    enable_pagination=True,
    session_limit_key='activities_limit',
    key_prefix='activities',
)
