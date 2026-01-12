"""Home page for the Athlete Dashboard."""

from queries import load_activities_current_week, load_athlete_data
import streamlit as st
from ui.activity_list import render_activity_list
from ui.consistency import compute_weekly_multisport_stats, show_consistency_heatmap
from ui.visualization_charts import (
    render_distribution_donut,
    render_weekly_hours_chart,
    render_weekly_hours_per_sport_chart,
)
from ui.weekly_stats import (
    compute_weekly_dfs,
    compute_weekly_stats,
    load_prepare_activities_weekly,
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
if df_athlete.empty:
    st.error('No athlete data available.')
    st.stop()

athlete = df_athlete.iloc[0]
st.title(f'Athlete Dashboard - {athlete.firstname} {athlete.lastname}')

# --------------------------------------------------
# Weekly activity stats
# --------------------------------------------------
df_activities_weekly = load_prepare_activities_weekly()

df_current, df_previous, df_last_4_weeks = compute_weekly_dfs(df_activities_weekly)
current_hours, delta_hours, current_distance, delta_distance = compute_weekly_stats(
    df_current, df_previous
)

# ---------------------------------
# Weekly discipline distribution
# ---------------------------------
# Discipline distribution donuts
donut_current = render_distribution_donut(df_current)
donut_4w = render_distribution_donut(df_last_4_weeks)

# Weekly history (hours only)
weekly_history_chart = render_weekly_hours_chart(
    df_activities_weekly, title='Weekly training hours'
)

# Weekly hours per sport (last 4 weeks)
weekly_sport_chart = render_weekly_hours_per_sport_chart(
    df_last_4_weeks, title='Weekly hours per sport - last 4 weeks'
)


# --------------------------------------------------
# KPIs Multisport Consistency Stats
# --------------------------------------------------
all4_cov, all4_current, delta_weeks = compute_weekly_multisport_stats()


# ----------------------
# Dashboard Layout
# ----------------------
with st.container(border=True):
    # --------------------------------------------------
    # Row 1: KPIs + Discipline Distribution Donuts
    # --------------------------------------------------
    kpi_col, col_curr, col_4w = st.columns([1, 1, 1])

    with kpi_col:
        m1, m2 = st.columns(2)
        m1.metric(
            'Weekly hours', f'{current_hours:.2f} h', delta=f'{delta_hours:+.1f} h'
        )
        m2.metric(
            'Weekly distance',
            f'{current_distance:.2f} km',
            delta=f'{delta_distance:+.1f} km',
        )

        st.divider()

        m3, m4 = st.columns(2)
        m3.metric('All-4 coverage', f'{all4_cov * 100:.0f}%')
        m4.metric('All-4 current', f'{all4_current} w', delta=f'{delta_weeks:d} w')

    with col_curr:
        st.markdown('**Discipline distribution - current week**')
        st.altair_chart(donut_current)

    with col_4w:
        st.markdown('**Discipline distribution - last 4 weeks**')
        st.altair_chart(donut_4w)

    # --------------------------------------------------
    # Row 2: Weekly History + Weekly Hours per Sport
    # --------------------------------------------------
    hist_col, chart_col = st.columns([1, 3])

    with hist_col:
        st.altair_chart(weekly_history_chart)

    with chart_col:
        st.altair_chart(weekly_sport_chart)

    # -------------------------------
    # Row 3: Consistency Heatmap
    # -------------------------------
    show_consistency_heatmap()

# --------------------------------------------------
# Weekly activities at the bottom (Master–Detail)
# --------------------------------------------------
st.markdown('## This week`s activities')

df_activities_weekly_activities = load_activities_current_week()

render_activity_list(
    df_activities_weekly_activities,
    enable_pagination=False,  # weekly list is short
    key_prefix='home_week',
)
