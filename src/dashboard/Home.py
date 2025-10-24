"""Homepage of Dashboard."""

import streamlit as st
import pandas as pd
from queries import load_athlete_data

# --- Page Configuration ---
st.set_page_config(page_title='Athlete Dashboard', page_icon='🏃', layout='wide')

# st.title('🏠 Athlete Dashboard')
# st.markdown('Visualizing personal activity data from Strava via BigQuery.')

# --- Load athlete metadata ---
try:
    df_athlete = load_athlete_data()

    if isinstance(df_athlete, pd.DataFrame):
        if df_athlete.empty:
            st.warning("No athlete data found.")
            st.stop()
        # assume one athlete, take the first row
        athlete = df_athlete.iloc[0]
    else:
        # if function returns a dict or Series
        athlete = df_athlete

except Exception as e:
    st.error(f"❌ Failed to load athlete data: {e}")
    st.stop()

# --- Header Layout ---
st.markdown("---")
col1, col2 = st.columns([1, 3])

with col1:
    st.image(athlete["profile_medium_img_url"], width=150)

with col2:
    st.markdown(f"""
    ### {athlete['firstname']} {athlete['lastname']}  (*{athlete['username']}*)
    {athlete['bio']}  
    **Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  
    **Gender:** {athlete['sex']}  
    """)

st.markdown("---")
