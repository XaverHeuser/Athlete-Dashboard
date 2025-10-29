"""Athlete Dashboard — Overview page."""

import pandas as pd
from queries import load_athlete_data, load_latest_stats
import streamlit as st

# --- Page config ---
st.set_page_config(page_title='Athlete Dashboard', page_icon='🏃', layout='wide')

# --- Load athlete data ---
try:
    df_athlete = load_athlete_data()
    if df_athlete.empty:
        st.warning('No athlete data found.')
        st.stop()
    athlete = df_athlete.iloc[0]
except Exception as e:
    st.error(f'❌ Failed to load athlete data: {e}')
    st.stop()

# --- Header ---
st.markdown('---')
col1, col2 = st.columns([1, 3])

with col1:
    st.image(athlete['profile_medium_img_url'], width=150)

with col2:
    st.markdown(
        f"""
        ### {athlete['firstname']} {athlete['lastname']}
        {athlete['bio']}
        **Username:** {athlete['username']}  
        **Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  
        **Gender:** {athlete['sex']}
        """ 
    ) # noqa: W291

st.markdown('---')

# --- Load latest stats ---
try:
    df_stats = load_latest_stats()
    if df_stats.empty:
        st.warning('No latest stats found.')
        st.stop()
    stats = df_stats.iloc[0]
except Exception as e:
    st.error(f'❌ Failed to load athlete stats: {e}')
    st.stop()

# --- Summary cards ---
st.subheader('Latest Athlete Statistics')

col1, col2, col3 = st.columns(3)
col1.metric('YTD Ride Distance', f'{stats["ytd_ride_distance_m"] / 1000:.1f} km')
col2.metric('YTD Run Distance', f'{stats["ytd_run_distance_m"] / 1000:.1f} km')
col3.metric('YTD Swim Distance', f'{stats["ytd_swim_distance_m"] / 1000:.1f} km')

st.caption(f'Last updated: {pd.to_datetime(stats["snapshot_ts"]).date()}')
st.markdown('---')
