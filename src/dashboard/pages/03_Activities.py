"""Detailed activity list and exploration."""

import pandas as pd
from queries import load_activities
import streamlit as st
from ui.constants import KPI_ICONS, PAGE_SIZE
from ui.viz_helper_functions import show_activity_map, sport_badge


# =========================
# Configuration
# =========================
st.set_page_config(page_title='Activities', page_icon='📋', layout='wide')


# =========================
# Session state
# =========================
if 'activities_limit' not in st.session_state:
    st.session_state.activities_limit = PAGE_SIZE


# =========================
# Load data
# =========================
try:
    df_activities = load_activities()
    if df_activities.empty:
        st.warning('No activities found.')
        st.stop()
except Exception as e:
    st.error(f'Failed to load activities: {e}')
    st.stop()


# =========================
# Filters
# =========================
st.title('All Activities')

# -------- Filter Row 1 --------
row1_col1, row1_col2, row1_col3 = st.columns([2, 1, 1])

with row1_col1:
    search_text = st.text_input('Search activity name')

with row1_col2:
    year_options = ['All'] + sorted(
        df_activities['activity_year'].dropna().unique().tolist(), reverse=True
    )
    year_filter = st.selectbox('Year', options=year_options)

with row1_col3:
    if year_filter != 'All':
        month_options = ['All'] + sorted(
            df_activities
            .loc[
                df_activities['activity_year'] == year_filter, 'activity_month'
            ]
            .dropna()
            .unique()
            .tolist()
        )
    else:
        month_options = ['All']

    month_filter = st.selectbox('Month', options=month_options)


# -------- Filter Row 2 --------
row2_col1, row2_col2, row2_col3 = st.columns([1, 2, 2])

with row2_col1:
    sport_filter = st.selectbox(
        'Sport Type',
        options=['All']
        + sorted(df_activities['sport_type'].dropna().unique().tolist()),
    )

with row2_col2:
    min_dist, max_dist = st.slider(
        'Distance (km)',
        min_value=0.0,
        max_value=float(df_activities['distance_km'].max()),
        value=(0.0, float(df_activities['distance_km'].max())),
        step=1.0,
    )

with row2_col3:
    min_time, max_time = st.slider(
        'Moving Time (min)',
        min_value=0,
        max_value=int(df_activities['moving_time_s'].max() / 60),
        value=(0, int(df_activities['moving_time_s'].max() / 60)),
        step=5,
    )

st.caption(
    f'Filters: '
    f'{year_filter}'
    f'{" · " + month_filter if month_filter != "All" else ""} · '
    f'{sport_filter} · '
    f'{min_dist:.0f}–{max_dist:.0f} km · '
    f'{min_time}–{max_time} min'
)

# =========================
# Apply filters
# =========================
filtered = df_activities.copy()

# Name
if search_text:
    filtered = filtered[
        filtered['activity_name'].str.contains(search_text, case=False, na=False)
    ]

# Year
if year_filter != 'All':
    filtered = filtered[filtered['activity_year'] == year_filter]

# Month
if month_filter != 'All':
    filtered = filtered[filtered['activity_month'] == month_filter]

# Sport
if sport_filter != 'All':
    filtered = filtered[filtered['sport_type'] == sport_filter]

# Distance
filtered = filtered[
    (filtered['distance_km'] >= min_dist) & (filtered['distance_km'] <= max_dist)
]

# Moving time (seconds)
filtered = filtered[
    (filtered['moving_time_s'] >= min_time * 60)
    & (filtered['moving_time_s'] <= max_time * 60)
]

filtered = filtered.sort_values('activity_date_local', ascending=False).reset_index(
    drop=True
)

# =========================
# Activity cards (lazy maps)
# =========================
st.divider()
st.markdown('### 🏃 Activities')

visible = filtered.head(st.session_state.activities_limit)

for _, row in visible.iterrows():
    with st.container():
        cols = st.columns([1.4, 2])

        with cols[0]:
            st.subheader(row['activity_name'])
            st.caption(row['activity_date_local'])

            sport_badge(row['sport_type'])

            st.markdown(
                f"""
                <div style="margin-top: 8px; line-height: 1.6;">
                    <div>{KPI_ICONS['distance']} <strong>Distance:</strong> {row['distance_km']:.2f} km</div>
                    <div>{KPI_ICONS['speed']} <strong>Avg speed:</strong> {row['avg_speed_kph']:.2f} km/h</div>
                    <div>{KPI_ICONS['heartrate']} <strong>Avg HR:</strong> {row['avg_heartrate']:.0f} bpm</div>
                    <div>{KPI_ICONS['time']} <strong>Moving time:</strong> {int(row['moving_time_s'] / 60)} min</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with cols[1]:
            with st.expander('Show route'):
                if pd.notna(row['map_polyline']):
                    show_activity_map(row['map_polyline'])
                else:
                    st.caption('No map available')

        st.divider()


# =========================
# Pagination
# =========================
if st.session_state.activities_limit < len(filtered):
    if st.button('Load more activities'):
        st.session_state.activities_limit += PAGE_SIZE
