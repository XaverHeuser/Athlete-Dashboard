"""Year-to-Date Progress Overview."""

import altair as alt
from queries import load_sport_types, load_time_series
import streamlit as st

st.set_page_config(
    page_title='Athlete Statistics Overview',
    page_icon='📈',
    layout='wide',
)

# =========================
# ACTIVITY TIME SERIES
# =========================

st.header('Activity Stats')

control_col1, control_col2, control_col3 = st.columns(3)

with control_col1:
    granularity = st.selectbox(
        'Time Granularity',
        ['daily', 'weekly', 'monthly', 'yearly'],
        index=2,
    )

with control_col2:
    metric = st.selectbox(
        'Metric',
        [
            'total_distance_km',
            'total_moving_time_h',
            'total_activities',
        ],
        format_func=lambda x: {
            'total_distance_km': 'Total Distance (km)',
            'total_moving_time_h': 'Moving Time (hours)',
            'total_activities': 'Number of Activities',
        }[x],
    )

sport_types = load_sport_types()
sport_type_options = ['All Sports'] + sport_types

with control_col3:
    sport_type = st.selectbox(
        'Sport Type',
        options=sport_type_options,
    )

sport_filter = None if sport_type == 'All Sports' else sport_type

# =========================
# LOAD DATA (unfiltered, for date bounds)
# =========================

df_ts_all = load_time_series(
    granularity=granularity,
    metric=metric,
    sport_type=sport_filter,
)

if df_ts_all.empty:
    st.warning('No data available for selected options.')
    st.stop()

# =========================
# TIME RANGE SELECTION
# =========================

min_date = df_ts_all['period'].min()
max_date = df_ts_all['period'].max()

start_date, end_date = st.date_input(
    'Time Range',
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# =========================
# LOAD DATA (filtered)
# =========================

df_ts = load_time_series(
    granularity=granularity,
    metric=metric,
    sport_type=sport_filter,
    start_date=start_date.isoformat(),
    end_date=end_date.isoformat(),
)

if df_ts.empty:
    st.warning('No data available for selected time range.')
    st.stop()

# =========================
# UNIT NORMALIZATION
# =========================

if metric == 'total_distance_km':
    y_title = 'Distance (km)'
elif metric == 'total_moving_time_h':
    y_title = 'Moving Time (hours)'
else:
    y_title = 'Activities'

chart_title = (
    f'{sport_type} – {y_title}'
    if sport_type != 'All Sports'
    else f'All Sports – {y_title}'
)

# =========================
# AXIS CONFIGURATION
# =========================

if granularity == 'daily':
    x_axis = alt.Axis(format='%d.%m', labelAngle=-45, grid=False)
elif granularity == 'weekly':
    x_axis = alt.Axis(format='KW %V\n%Y', grid=False)
elif granularity == 'monthly':
    x_axis = alt.Axis(format='%b %Y', grid=False)
else:  # yearly
    x_axis = alt.Axis(format='%Y', grid=False)

# =========================
# CHART
# =========================

base = alt.Chart(df_ts).encode(
    x=alt.X('period:T', title=None, axis=x_axis),
    y=alt.Y('value:Q', title=y_title, axis=alt.Axis(grid=True)),
    tooltip=[
        alt.Tooltip('period:T', title='Period'),
        alt.Tooltip('value:Q', title=y_title, format=',.2f'),
    ],
)

area = base.mark_area(opacity=0.2)
line = base.mark_line(strokeWidth=2.5)
points = base.mark_point(size=80, filled=True, opacity=0.9)

trend_chart = (
    (area + line + points)
    .properties(height=360, title=chart_title)
    .configure_title(fontSize=16, anchor='start')
)

st.altair_chart(trend_chart, use_container_width=True)
