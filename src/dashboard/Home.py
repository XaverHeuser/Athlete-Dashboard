import altair as alt
import pandas as pd
from queries import load_athlete_data, load_weekly_summary
import streamlit as st

# TODO: Beautify - colors, layout, ...
# TODO: Outsource - functions, colors, ...
# TODO: Rearange layout
# TODO: Define fixed KPIs

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title='Athlete Dashboard - Overview',
    page_icon='🏃',
    layout='wide',
)

# --------------------------------------------------
# LOAD ATHLETE
# --------------------------------------------------

df_athlete = load_athlete_data()
athlete = df_athlete.iloc[0]

st.title('Athlete Dashboard - Overview')

ALLOWED_SPORTS = [
    "Run",
    "Ride",
    "Swim",
    "WeightTraining",
]

SPORT_LABELS = {
    "Run": "Laufen",
    "Ride": "Radfahren",
    "Swim": "Schwimmen",
    "WeightTraining": "Krafttraining",
}

COLOR_SCALE = alt.Scale(
    domain=list(SPORT_LABELS.values()),
    range=[
        "#2ca02c",  # Laufen
        "#1f77b4",  # Radfahren
        "#17becf",  # Schwimmen
        "#7f7f7f",  # Krafttraining
    ],
)

# --------------------------------------------------
# LOAD WEEKLY DATA
# --------------------------------------------------

df_week = load_weekly_summary()

if df_week.empty:
    st.warning('No weekly activity data available.')
    st.stop()

df_week['activity_week'] = pd.to_datetime(df_week['activity_week'])

# --------------------------------------------------
# CURRENT & PREVIOUS WEEK
# --------------------------------------------------

latest_week = df_week['activity_week'].max()
prev_week = latest_week - pd.Timedelta(days=7)

df_curr = df_week[df_week['activity_week'] == latest_week]
df_prev = df_week[df_week['activity_week'] == prev_week]

current_hours = df_curr['total_moving_time_h'].sum()
previous_hours = df_prev['total_moving_time_h'].sum()

delta_hours = current_hours - previous_hours
delta_pct = (delta_hours / previous_hours * 100) if previous_hours > 0 else 0

# --------------------------------------------------
# KPI ROW
# --------------------------------------------------
current_hours = df_curr['total_moving_time_h'].sum()
previous_hours = df_prev['total_moving_time_h'].sum()

current_distance = df_curr['total_distance_km'].sum()
previous_distance = df_prev['total_distance_km'].sum()

delta_hours = current_hours - previous_hours
delta_hours_pct = delta_hours / previous_hours * 100 if previous_hours > 0 else 0

delta_distance = current_distance - previous_distance
delta_distance_pct = (
    delta_distance / previous_distance * 100 if previous_distance > 0 else 0
)

with st.container(border=True):
    col_time, col_dist = st.columns(2)

with col_time:
    st.metric(
        'Wochenzeit',
        f'{current_hours:.1f} h',
    )

    st.caption(f'Δ zur Vorwoche: {delta_hours:+.1f} h ({delta_hours_pct:+.0f} %)')

with col_dist:
    st.metric(
        'Wochendistanz',
        f'{current_distance:.1f} km',
    )

    st.caption(
        f'Δ zur Vorwoche: {delta_distance:+.1f} km ({delta_distance_pct:+.0f} %)'
    )


metric = st.radio(
    'Metrik',
    options=['Stunden', 'Distanz'],
    horizontal=True,
)

if metric == 'Stunden':
    value_col = 'total_moving_time_h'
    unit = 'h'
    title = 'Wochenstunden'
    tooltip_fmt = '.2f'
else:
    value_col = 'total_distance_km'
    unit = 'km'
    title = 'Wochendistanz'
    tooltip_fmt = '.2f'


#####################

last_weeks = df_week['activity_week'].drop_duplicates().sort_values().tail(4)

df_last_weeks = df_week[df_week['activity_week'].isin(last_weeks)].copy()

df_last_weeks['week_label'] = df_last_weeks['activity_week'].dt.strftime('KW %V')


weekly_sport_chart = (
    alt.Chart(df_last_weeks)
    .mark_bar()
    .encode(
        x=alt.X(
            'sport_type:N',
            title=None,
        ),
        xOffset=alt.XOffset(
            'week_label:N',
            title='Woche',
        ),
        y=alt.Y(
            f'{value_col}:Q',
            title=f'{title} ({unit})',
        ),
        color=alt.Color(
            'week_label:N',
            title='Woche',
            legend=alt.Legend(orient='top'),
        ),
        tooltip=[
            alt.Tooltip('sport_type:N', title='Sportart'),
            alt.Tooltip('week_label:N', title='Woche'),
            alt.Tooltip(
                f'{value_col}:Q',
                title=title,
                format='.2f',
            ),
        ],
    )
    .properties(
        height=320,
        title=f'{title} pro Sportart – letzte 4 Wochen',
    )
)

st.altair_chart(weekly_sport_chart, use_container_width=True)

##############################

def render_discipline_donut(df: pd.DataFrame, title: str) -> alt.Chart:
    df_pie = (
        df.groupby("sport_type", as_index=False)["total_moving_time_h"]
        .sum()
    )

    df_pie = df_pie[df_pie["sport_type"].isin(ALLOWED_SPORTS)].copy()
    df_pie["sport_label"] = df_pie["sport_type"].map(SPORT_LABELS)

    df_pie["share_pct"] = (
        df_pie["total_moving_time_h"]
        / df_pie["total_moving_time_h"].sum()
        * 100
    )

    chart = (
        alt.Chart(df_pie)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta(
                "total_moving_time_h:Q",
                title="Stunden",
            ),
            color=alt.Color(
                "sport_label:N",
                scale=COLOR_SCALE,
                title="Disziplin",
                legend=alt.Legend(orient="right"),
            ),
            tooltip=[
                alt.Tooltip("sport_label:N", title="Disziplin"),
                alt.Tooltip(
                    "total_moving_time_h:Q",
                    title="Stunden",
                    format=".1f",
                ),
                alt.Tooltip(
                    "share_pct:Q",
                    title="Anteil",
                    format=".0f",
                ),
            ],
        )
        .properties(
            height=300,
            title=title,
        )
    )

    return chart

last_4_weeks = (
    df_week["activity_week"]
    .drop_duplicates()
    .sort_values()
    .tail(4)
)

df_4w = df_week[
    df_week["activity_week"].isin(last_4_weeks)
].copy()

donut_4w = render_discipline_donut(
    df_4w,
    "Disziplinen-Verteilung – letzte 4 Wochen (Zeit)",
)



donut_curr = render_discipline_donut(
    df_curr,
    "Disziplinen-Verteilung – aktuelle Woche (Zeit)",
)


c1, c2 = st.columns(2)
with c1:
    st.altair_chart(donut_curr, use_container_width=True)
with c2:
    st.altair_chart(donut_4w, use_container_width=True)

# --------------------------------------------------
# WEEKLY HISTORY (LAST 4 WEEKS)
# --------------------------------------------------

df_hist = (
    df_week.groupby('activity_week', as_index=False)[value_col]
    .sum()
    .sort_values('activity_week')
    .tail(4)
)

df_hist['week_label'] = df_hist['activity_week'].dt.strftime('KW %V')
latest_week = df_hist['activity_week'].max()


history_chart = (
    alt.Chart(df_hist)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X(
            'week_label:N',
            title=None,
            sort=None,
        ),
        y=alt.Y(
            f'{value_col}:Q',
            title=f'{title} ({unit})',
            axis=alt.Axis(grid=True),
        ),
        color=alt.condition(
            alt.datum.activity_week == latest_week,
            alt.value('#1f77b4'),  # aktuelle Woche
            alt.value('#d3d3d3'),  # frühere Wochen
        ),
        tooltip=[
            alt.Tooltip('week_label:N', title='Woche'),
            alt.Tooltip(
                f'{value_col}:Q',
                title=title,
                format=tooltip_fmt,
            ),
        ],
    )
    .properties(
        height=260,
        title=f'{title} - letzte 4 Wochen',
    )
)

st.altair_chart(history_chart, use_container_width=True)
