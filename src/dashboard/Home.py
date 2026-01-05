"""Home page for the Athlete Dashboard."""

import pandas as pd
from queries import load_athlete_data, load_weekly_summary, load_activities_current_week
import streamlit as st
from ui.viz_helper_functions import (
    render_discipline_donut,
    render_weekly_hours_chart,
    render_weekly_hours_per_sport_chart,
)
from ui.activity_details import render_activity_details
from ui.constants import KPI_ICONS


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title='Athlete Dashboard - Overview', page_icon='🏃', layout='wide'
)

# --------------------------------------------------
# Query param helpers (same as Activities page)
# --------------------------------------------------
def get_selected_activity_id() -> str | None:
    qp = st.query_params
    val = qp.get("activity_id")
    if isinstance(val, list):
        return val[0] if val else None
    return val


def set_selected_activity_id(activity_id: str) -> None:
    st.query_params["activity_id"] = activity_id


def clear_selected_activity_id() -> None:
    qp = dict(st.query_params)
    qp.pop("activity_id", None)
    st.query_params.clear()
    for k, v in qp.items():
        st.query_params[k] = v


# --------------------------------------------------
# Load athlete information
# --------------------------------------------------
df_athlete = load_athlete_data()
athlete = df_athlete.iloc[0]

st.title(f'Athlete Dashboard - {athlete.firstname} {athlete.lastname}')

# NOTE: Here, I would implement the visualization for the consistency chart

# --------------------------------------------------
# Load weekly summary data
# --------------------------------------------------
df_week = load_weekly_summary()

if df_week.empty:
    st.warning('No weekly activity data available.')
    st.stop()

df_week['activity_week'] = pd.to_datetime(df_week['activity_week'])

# --------------------------------------
# Current and previous week calculations
# --------------------------------------
# Get latest week and previous week
latest_week = df_week['activity_week'].max()
previous_week = latest_week - pd.Timedelta(days=7)

# Get data for current and previous week
df_current = df_week[df_week['activity_week'] == latest_week]
df_previous = df_week[df_week['activity_week'] == previous_week]

# Weekly hours
current_hours = df_current['total_moving_time_h'].sum()
previous_hours = df_previous['total_moving_time_h'].sum()
delta_hours = current_hours - previous_hours

# Weekly distance
current_distance = df_current['total_distance_km'].sum()
previous_distance = df_previous['total_distance_km'].sum()
delta_distance = current_distance - previous_distance


# ------------------------------
# Prepare data for discipline donuts
# ------------------------------
available_weeks = df_week['activity_week'].drop_duplicates().sort_values()

previous_week_date = available_weeks.tail(2).iloc[0]
last_4_weeks = available_weeks.tail(4)

df_previous_week = df_week[df_week['activity_week'] == previous_week_date]
df_last_4_weeks = df_week[df_week['activity_week'].isin(last_4_weeks)].copy()

# ------------------------------
# create visualizations
# ------------------------------
# Discipline distribution donuts
donut_current = render_discipline_donut(
    df_current, 'Discipline distribution – current week (Time)'
)

donut_previous = render_discipline_donut(
    df_previous_week, 'Discipline distribution – previous week (Time)'
)

donut_4w = render_discipline_donut(
    df_last_4_weeks, 'Discipline distribution – last 4 weeks (Time)'
)

# Weekly history (hours only)
weekly_history_chart = render_weekly_hours_chart(df_week, title='Weekly training hours')

# Weekly hours per sport (last 4 weeks)
weekly_sport_chart = render_weekly_hours_per_sport_chart(
    df_last_4_weeks, title='Weekly hours per sport – last 4 weeks'
)

# ----------------------
# Dashboard Layout
# ----------------------
with st.container(border=True):
    # --------------------------------------------------
    # Row 1: KPIs + Discipline Distribution Donuts
    # --------------------------------------------------
    kpi_col, col_curr, col_prev, col_4w = st.columns([1, 1, 1, 1])

    with kpi_col:
        st.metric(
            'Weekly hours', f'{current_hours:.2f} h', delta=f'{delta_hours:+.1f} h'
        )
        st.metric(
            'Weekly distance',
            f'{current_distance:.2f} km',
            delta=f'{delta_distance:+.1f} km',
        )

    with col_curr:
        st.markdown('**Discipline distribution – current week**')
        st.altair_chart(donut_current, use_container_width=True)

    with col_prev:
        st.markdown('**Discipline distribution – previous week**')
        st.altair_chart(donut_previous, use_container_width=True)

    with col_4w:
        st.markdown('**Discipline distribution – last 4 weeks**')
        st.altair_chart(donut_4w, use_container_width=True)

    # --------------------------------------------------
    # Row 2: Weekly History + Weekly Hours per Sport
    # --------------------------------------------------
    st.divider()

    hist_col, chart_col = st.columns([1, 3])

    with hist_col:
        st.altair_chart(weekly_history_chart, use_container_width=True)

    with chart_col:
        st.altair_chart(weekly_sport_chart, use_container_width=True)

# --------------------------------------------------
# Weekly activities at the bottom (Master–Detail)
# --------------------------------------------------
st.divider()
st.markdown("## This week’s activities")

df_week_activities = load_activities_current_week()
if df_week_activities.empty:
    st.info("No activities found for the current week.")
else:
    # Details panel
    selected_activity_id = get_selected_activity_id()
    try:
        selected_activity_id_int = int(selected_activity_id)
    except ValueError:
        st.warning("Invalid activity_id in URL. Clearing selection.")
        clear_selected_activity_id()
        st.rerun()
        
    if selected_activity_id:
        selected_row_df = df_week_activities[df_week_activities["activity_id"] == selected_activity_id_int]

        if selected_row_df.empty:
            # The selected activity might be outside this week; still try to load streams if you want
            # For now, just close selection.
            st.warning("Selected activity is not in the current week list.")
            clear_selected_activity_id()
        else:
            with st.container(border=True):
                top_cols = st.columns([4, 1])
                with top_cols[0]:
                    st.markdown("### Activity details")
                with top_cols[1]:
                    if st.button("Close", key="home_close_details"):
                        clear_selected_activity_id()
                        st.rerun()

                activity_row = selected_row_df.iloc[0]
                try:
                    df_streams = load_activity_streams(selected_activity_id_int)
                except Exception as e:
                    st.error(f"Failed to load activity streams: {e}")
                    df_streams = pd.DataFrame()

                render_activity_details(activity_row=activity_row, df_streams=df_streams)

    # Weekly list (compact)
    for _, row in df_week_activities.iterrows():
        with st.container():
            cols = st.columns([1.4, 2])

            with cols[0]:
                st.subheader(row['activity_name'])
                st.caption(row['start_date_local'].strftime('%Y-%m-%d %H:%M'))

                sport_badge(row['sport_type'])
                
                moving_time_str = format_seconds_to_hhmmss(int(row["moving_time_s"]))
                pace_str = format_pace_min_per_km(row["avg_pace_min_per_km"])
                speed_str = format_speed_kph(row["avg_speed_kph"])

                colL, colR = st.columns(2, gap="large")

                with colL:
                    st.markdown(f"{KPI_ICONS['time']} **Time:** {moving_time_str} h")
                    st.markdown(f"{KPI_ICONS['distance']} **Distance:** {row['distance_km']:.2f} km")
                    st.markdown(f"{KPI_ICONS['speed']} **Avg pace:** {pace_str} min/km")

                with colR:
                    st.markdown(f"{KPI_ICONS['heartrate']} **Avg HR:** {row['avg_heartrate']:.0f} bpm")
                    st.markdown(f"{KPI_ICONS['elevation_gain']} **Elevation gain:** {row['elevation_gain_m']:.0f} m")
                    st.markdown(f"{KPI_ICONS['speed']} **Avg tempo:** {speed_str} km/h")
                
                if st.button("View details", key=f"open_{row['activity_id']}"):
                    set_selected_activity_id(str(row["activity_id"]))
                    st.rerun()


            with cols[1]:
                with st.expander('Show route'):
                    if pd.notna(row['map_polyline']):
                        show_activity_map(row['map_polyline'])
                    else:
                        st.caption('No map available')

            st.divider()
