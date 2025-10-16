"""Homepage of Dashboard."""

import streamlit as st
from queries import load_raw_data

# --- Page Configuration ---
st.set_page_config(
    page_title="Athlete Dashboard",
    page_icon="🏃",
    layout="wide"
)


st.title('Athlete Dashboard')
st.markdown("Visualizing personal activity data from Strava via BigQuery.")

# Load the data from BigQuery
try:
    df_activities_raw = load_raw_data()

    # --- Data Visualization ---
    st.header("Monthly Activity Summary")
    
    if not df_activities_raw.empty:
        # Display a bar chart of monthly distance
        st.subheader("Raw Data")
        st.write(len(df_activities_raw))
        st.dataframe(df_activities_raw)
    else:
        st.warning("No activity data found in BigQuery.")

except Exception as e:
    st.error(f"An error occurred while loading data from BigQuery: {e}")
