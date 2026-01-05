"""Home page for the Athlete Dashboard."""

import pandas as pd
from queries import load_activities_current_week, load_athlete_data, load_weekly_summary
import streamlit as st
from ui.activity_list import render_activity_list
from ui.viz_helper_functions import (
    render_discipline_donut,
    render_weekly_hours_chart,
    render_weekly_hours_per_sport_chart,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title='Athlete Dashboard - Overview', page_icon='🏃', layout='wide'
)

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
st.markdown('## This week`s activities')

df_week_activities = load_activities_current_week()

render_activity_list(
    df_week_activities,
    enable_pagination=False,  # weekly list is short
    key_prefix='home_week',
)
