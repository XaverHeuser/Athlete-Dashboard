"""Detailed Athlete Profile."""

import streamlit as st
import pandas as pd
from queries import load_athlete_data

# --- Page Config ---
st.set_page_config(page_title="Athlete Profile", page_icon="👤", layout="centered")

# --- Load athlete metadata ---
try:
    df_athlete = load_athlete_data()

    if isinstance(df_athlete, pd.DataFrame):
        if df_athlete.empty:
            st.warning("No athlete data found.")
            st.stop()
        # Assume one athlete, take the first row
        athlete = df_athlete.iloc[0]
    else:
        # If function returns a dict or Series
        athlete = df_athlete

except Exception as e:
    st.error(f"❌ Failed to load athlete data: {e}")
    st.stop()

# --- Page Content ---
st.title(f"{athlete['firstname']} {athlete['lastname']}")

# Display large profile image
st.image(
    athlete["profile_img_url"],
    caption=f"{athlete['firstname']} {athlete['lastname']}",
    width=300,
)

# Personal details section
st.subheader("Personal Details")
st.markdown(f"""
**Username:** {athlete['username']}  
**Bio:** {athlete['bio']}  
**Athlete ID:** {athlete['athlete_id']}  
**Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  
**Gender:** {athlete['sex']}  
**Premium Member:** {athlete['is_premium_user']}  
**Created At:** {athlete['created_at']}  
""")
