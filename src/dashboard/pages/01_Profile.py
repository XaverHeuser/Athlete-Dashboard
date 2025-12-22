"""Detailed Athlete Profile."""

import pandas as pd
from queries import load_athlete_data
import streamlit as st


# --- Page config ---
st.set_page_config(page_title='Athlete Profile', page_icon='👤', layout='centered')

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

# --- Profile content ---
st.title(f'{athlete["firstname"]} {athlete["lastname"]}')
st.image(
    athlete['profile_img_url'],
    caption=f'{athlete["firstname"]} {athlete["lastname"]}',
    width=320,
)

st.divider()
st.subheader('👤 Personal Details')

st.markdown(
    f"""
**Username:** {athlete['username']}  
**Bio:** {athlete['bio']}  
**Athlete ID:** {athlete['athlete_id']}  
**Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  
**Gender:** {athlete['sex']}  
**Premium Member:** {'✅ Yes' if athlete['is_premium_user'] else '❌ No'}  
**Weight:** {athlete['weight_kg']} kg  
**Account Created:** {pd.to_datetime(athlete['created_at']).date()}  
**First Activity:** {pd.to_datetime(athlete['first_activity_date']).date()}  
**Last Activity:** {pd.to_datetime(athlete['last_activity_date']).date()}  
**Total Activities:** {int(athlete['total_activities'])}
"""  # noqa: W291
)

st.divider()
st.caption(f'Data last loaded at: {pd.to_datetime(athlete["mart_loaded_at"])}')
