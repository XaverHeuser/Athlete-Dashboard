"""Athlete Dashboard — Overview page."""

import pandas as pd
import altair as alt
from queries import load_athlete_data, load_latest_stats, load_stats_history
import streamlit as st

# --- Page config ---
st.set_page_config(page_title="Athlete Dashboard", page_icon="🏃", layout="wide")

# --- Load athlete data ---
try:
    df_athlete = load_athlete_data()
    if df_athlete.empty:
        st.warning("No athlete data found.")
        st.stop()
    athlete = df_athlete.iloc[0]
except Exception as e:
    st.error(f"❌ Failed to load athlete data: {e}")
    st.stop()

# --- Header ---
st.title("🏃 Athlete Dashboard Overview")

with st.container(border=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(athlete["profile_medium_img_url"], width=160)
    with col2:
        st.markdown(
            f"""
            ### {athlete['firstname']} {athlete['lastname']}
            {athlete['bio']}

            **Username:** {athlete['username']}  
            **Location:** {athlete['city']}, {athlete['state']}, {athlete['country']}  
            **Gender:** {athlete['sex']}  
            **Premium:** {'✅ Yes' if athlete['is_premium_user'] else '❌ No'}  
            """
        )

# --- Activity Summary ---
with st.container(border=True):
    st.subheader("📊 Activity Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Activities", int(athlete["total_activities"]))
    col2.metric("First Activity", pd.to_datetime(athlete["first_activity_date"]).strftime("%Y-%m-%d"))
    col3.metric("Last Activity", pd.to_datetime(athlete["last_activity_date"]).strftime("%Y-%m-%d"))

    days_active = (
        pd.to_datetime(athlete["last_activity_date"])
        - pd.to_datetime(athlete["first_activity_date"])
    ).days
    if days_active > 0:
        freq = athlete["total_activities"] / (days_active / 7)
        col4.metric("Avg Activities / Week", f"{freq:.1f}")

# --- Latest Stats ---
try:
    df_stats = load_latest_stats()
    if df_stats.empty:
        st.warning("No latest stats found.")
        st.stop()
    stats = df_stats.iloc[0]
except Exception as e:
    st.error(f"❌ Failed to load athlete stats: {e}")
    st.stop()

with st.container(border=True):
    st.subheader("🚴 Latest Athlete Statistics (YTD)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Ride Distance", f"{stats['ytd_ride_distance_m'] / 1000:.1f} km")
    col2.metric("Run Distance", f"{stats['ytd_run_distance_m'] / 1000:.1f} km")
    col3.metric("Swim Distance", f"{stats['ytd_swim_distance_m'] / 1000:.1f} km")

    st.caption(f"Last updated: {pd.to_datetime(stats['snapshot_ts']).date()}")

# --- Trend Visualization ---
import altair as alt

try:
    df_history = load_stats_history()
    df_history["snapshot_date"] = pd.to_datetime(df_history["snapshot_date"])

    # Werte in km umrechnen
    df_history["ride_km"] = df_history["ytd_ride_distance_m"] / 1000
    df_history["run_km"] = df_history["ytd_run_distance_m"] / 1000

    # Gemeinsame Chart-Konfiguration
    base = alt.Chart(df_history).encode(
        x=alt.X(
            "snapshot_date:T",
            title="Datum",
            axis=alt.Axis(format="%b %d", labelAngle=-45, labelFontSize=11, titleFontSize=12),
        ),
        tooltip=[
            alt.Tooltip("snapshot_date:T", title="Datum", format="%Y-%m-%d"),
            alt.Tooltip("ride_km:Q", title="Ride (km)", format=".1f"),
            alt.Tooltip("run_km:Q", title="Run (km)", format=".1f"),
        ],
    ).properties(height=320)

    # 🚴 Ride Chart
    ride_chart = (
        base.mark_line(color="#1f77b4", strokeWidth=3, interpolate="monotone")
        .encode(
            y=alt.Y(
                "ride_km:Q",
                title="Ride Distance (km)",
                axis=alt.Axis(labelFontSize=11, titleFontSize=12, grid=True),
                scale=alt.Scale(zero=False),
            )
        )
        .mark_point(size=50, filled=True, color="#1f77b4", opacity=0.9)
        .properties(title="🚴 Ride Distance Over Time")
    )

    # 🏃 Run Chart
    run_chart = (
        base.mark_line(color="#ff7f0e", strokeWidth=3, interpolate="monotone")
        .encode(
            y=alt.Y(
                "run_km:Q",
                title="Run Distance (km)",
                axis=alt.Axis(labelFontSize=11, titleFontSize=12, grid=True),
                scale=alt.Scale(zero=False),
            )
        )
        .mark_point(size=50, filled=True, color="#ff7f0e", opacity=0.9)
        .properties(title="🏃 Run Distance Over Time")
    )

    # Kombinieren mit Altair VConcat für gleiche X-Skala
    chart = alt.vconcat(
        ride_chart,
        run_chart,
        spacing=30,
    ).resolve_scale(x="shared")

    # Globales Styling
    chart = chart.configure_title(
        fontSize=16, fontWeight="bold", anchor="start", color="#333"
    ).configure_axis(
        gridColor="#E5E5E5", gridDash=[2, 3], labelColor="#444", titleColor="#444"
    ).configure_view(strokeOpacity=0)

    st.altair_chart(chart, use_container_width=True)

except Exception as e:
    st.warning(f"Trend chart not available: {e}")
