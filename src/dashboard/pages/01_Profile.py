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
**Username:** {athlete['username']}  # noqa W291
**Bio:** {athlete['bio']}  # noqa W291
**Athlete ID:** {athlete['athlete_id']}  # noqa W291
**Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  # noqa W291
**Gender:** {athlete['sex']}  # noqa W291
**Premium Member:** {athlete['is_premium_user']}  # noqa W291
**Created At:** {athlete['created_at']}
"""
)
