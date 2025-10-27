"""Year-to-Date Progress Overview."""

import streamlit as st
import altair as alt
from queries import load_stats_history

st.set_page_config(page_title="Athlete Statistics Overview", page_icon="📈", layout="wide")

# --- Load snapshot history ---
df_history = load_stats_history()

if df_history.empty or len(df_history) < 2:
    st.info("Not enough historical snapshots yet to show trends.")
    st.stop()

# Convert meters → kilometers
df_history["ytd_ride_km"] = df_history["ytd_ride_distance_m"] / 1000
df_history["ytd_run_km"] = df_history["ytd_run_distance_m"] / 1000

st.title("📈 Year-to-Date Progress")

ride_chart = (
    alt.Chart(df_history)
    .mark_line(point=True)
    .encode(
        x="snapshot_date:T",
        y=alt.Y("ytd_ride_km:Q", title="Ride Distance (km)"),
        tooltip=["snapshot_date", "ytd_ride_km"],
    )
    .properties(height=300)
)

run_chart = (
    alt.Chart(df_history)
    .mark_line(point=True, color="orange")
    .encode(
        x="snapshot_date:T",
        y=alt.Y("ytd_run_km:Q", title="Run Distance (km)"),
        tooltip=["snapshot_date", "ytd_run_km"],
    )
    .properties(height=300)
)

st.altair_chart(ride_chart | run_chart, use_container_width=True)
