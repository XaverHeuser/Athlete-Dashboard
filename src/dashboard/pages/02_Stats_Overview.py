"""Year-to-Date Progress Overview."""

from __future__ import annotations

from queries import load_athlete_stats
import streamlit as st


# -----------------------------------------------------------------------------
# Page setup
# -----------------------------------------------------------------------------
st.set_page_config(page_title='Stats Overview', page_icon='📈', layout='wide')

st.title('📈 Stats Overview')

st.caption('NOTE: This page is work-in-progress and the data needs further validation.')
# -----------------------------------------------------------------------------
# Load + prepare data
# -----------------------------------------------------------------------------
df = load_athlete_stats()

if df is None or df.empty:
    st.warning('No athlete statistics data available.')
    st.stop()

st.dataframe(df, use_container_width=True)
