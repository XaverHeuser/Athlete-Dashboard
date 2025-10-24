"""Detailed Athlete Profile."""

import pandas as pd
from queries import load_athlete_data
import streamlit as st

# --- Page Config ---
st.set_page_config(page_title='Athlete Profile', page_icon='👤', layout='centered')

# --- Load athlete metadata ---
try:
    df_athlete = load_athlete_data()

    if isinstance(df_athlete, pd.DataFrame):
        if df_athlete.empty:
            st.warning('No athlete data found.')
            st.stop()
        # Assume one athlete, take the first row
        athlete = df_athlete.iloc[0]
    else:
        # If function returns a dict or Series
        athlete = df_athlete

except Exception as e:
    st.error(f'❌ Failed to load athlete data: {e}')
    st.stop()

# --- Page Content ---
st.title(f'{athlete["firstname"]} {athlete["lastname"]}')

# Display large profile image
st.image(
    athlete['profile_img_url'],
    caption=f'{athlete["firstname"]} {athlete["lastname"]}',
    width=300,
)

# Personal details section
st.subheader('Personal Details')
st.markdown(
    f"""
**Username:** {athlete['username']}  # noqa: W291
**Bio:** {athlete['bio']}  # noqa: W291
**Athlete ID:** {athlete['athlete_id']}  # noqa: W291
**Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  # noqa: W291
**Gender:** {athlete['sex']}  # noqa: W291
**Premium Member:** {athlete['is_premium_user']}  # noqa: W291
**Created At:** {athlete['created_at']}  # noqa: W291
"""
)
