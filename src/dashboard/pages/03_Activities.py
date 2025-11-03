"""Activities — Detailed activity list and exploration."""

import polyline
import pydeck as pdk
import streamlit as st
import pandas as pd
from queries import load_activities

st.set_page_config(page_title="Activities", page_icon="📋", layout="wide")

# --- Load data ---
try:
    df_activities = load_activities()
    if df_activities.empty:
        st.warning("No activities found.")
        st.stop()
except Exception as e:
    st.error(f"❌ Failed to load activities: {e}")
    st.stop()

# --- Filters ---
st.title("📋 All Activities")

col1, col2, col3 = st.columns(3)
with col1:
    sport_filter = st.selectbox(
        "Sport Type",
        options=["All"] + sorted(df_activities["sport_type"].dropna().unique().tolist()),
        index=0,
    )
with col2:
    year_filter = st.selectbox(
        "Year",
        options=["All"] + sorted(df_activities["activity_year"].dropna().unique().tolist(), reverse=True),
        index=0,
    )
with col3:
    search_text = st.text_input("Search by name or keyword")

# --- Apply filters ---
filtered = df_activities.copy()
if sport_filter != "All":
    filtered = filtered[filtered["sport_type"] == sport_filter]
if year_filter != "All":
    filtered = filtered[filtered["activity_year"] == year_filter]
if search_text:
    filtered = filtered[filtered["activity_name"].str.contains(search_text, case=False, na=False)]

# --- Show compact table ---
st.markdown("### 🔍 Activity Overview")
st.caption(f"{len(filtered)} activities found")

# Select key columns for display
preview_cols = [
    "activity_date_local",
    "activity_name",
    "sport_type",
    "distance_km",
    "avg_speed_kph",
    "avg_heartrate",
    "moving_time_s",
]
preview = filtered[preview_cols].copy()

# Format columns
preview["distance_km"] = preview["distance_km"].map(lambda x: f"{x:.1f} km")
preview["avg_speed_kph"] = preview["avg_speed_kph"].map(lambda x: f"{x:.1f} km/h")
preview["avg_heartrate"] = preview["avg_heartrate"].map(lambda x: f"{x:.0f} bpm" if pd.notna(x) else "–")
preview["moving_time_s"] = preview["moving_time_s"].map(lambda x: f"{int(x/60)} min")

# Display interactive table
st.dataframe(
    preview,
    use_container_width=True,
    hide_index=True,
)

# --- Activity detail selection ---
st.markdown("---")
selected = st.selectbox(
    "Select an activity to view details",
    options=filtered["activity_name"].tolist(),
)

if selected:
    act = filtered[filtered["activity_name"] == selected].iloc[0]

    st.subheader(f"🏃 {act['activity_name']} ({act['sport_type']})")
    st.caption(f"Date: {pd.to_datetime(act['start_date_local']).date()} | Distance: {act['distance_km']:.1f} km")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Speed", f"{act['avg_speed_kph']:.1f} km/h")
    col2.metric("Max Speed", f"{act['max_speed_kph']:.1f} km/h")
    col3.metric("Elevation Gain", f"{act['elevation_gain_m']:.0f} m")
    col4.metric("Avg HR", f"{act['avg_heartrate']:.0f} bpm" if act["avg_heartrate"] else "–")

    st.markdown("#### ⚙️ Details")
    st.write(
        f"""
        **Elapsed Time:** {int(act['elapsed_time_s']/60)} min  
        **Idle Time:** {int((act['elapsed_time_s'] - act['moving_time_s'])/60)} min  
        **Weighted Power:** {act['weighted_watts']:.0f} W  
        **Kudos:** {act['kudos_count']}  
        **Comments:** {act['comment_count']}  
        """
    )

    if act["map_polyline"]:
        st.markdown("#### 🗺️ Map Preview")

        # Decode polyline → list of (lat, lon)
        coords = polyline.decode(act["map_polyline"])
        df_map = pd.DataFrame(coords, columns=["lat", "lon"])

        # Center map on the midpoint of the route
        mid_lat = df_map["lat"].mean()
        mid_lon = df_map["lon"].mean()

        # Define a pydeck Layer that draws a connected line
        layer = pdk.Layer(
            "PathLayer",
            data=df_map,
            get_path="coordinates",
            get_color=[255, 102, 0],  # Strava orange
            width_scale=2,
            width_min_pixels=3,
            rounded=True,
            opacity=0.8,
        )

        # We need to build a single Path entry per row:
        df_map = pd.DataFrame([{"coordinates": df_map[["lon", "lat"]].values.tolist()}])

        # Create the pydeck map
        view_state = pdk.ViewState(latitude=mid_lat, longitude=mid_lon, zoom=11)
        path_layer = pdk.Layer(
            "PathLayer",
            df_map,
            get_path="coordinates",
            get_color=[255, 102, 0],
            width_scale=2,
            width_min_pixels=3,
            opacity=0.9,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[path_layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/outdoors-v12"
        ))
