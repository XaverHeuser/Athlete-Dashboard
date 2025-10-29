"""Detailed Athlete Profile."""

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
    width=300,
)

st.subheader('Personal Details')
st.markdown(
    f"""
**Username:** {athlete['username']}  
**Bio:** {athlete['bio']}  
**Athlete ID:** {athlete['athlete_id']}  
**Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  
**Gender:** {athlete['sex']}  
**Premium Member:** {athlete['is_premium_user']}  
**Created At:** {athlete['created_at']}
"""  # noqa: W291
)
