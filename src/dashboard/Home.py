import altair as alt
import pandas as pd
import streamlit as st

from queries import load_athlete_data, load_weekly_summary

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Athlete Dashboard - Overview",
    page_icon="🏃",
    layout="wide",
)

# --------------------------------------------------
# LOAD ATHLETE
# --------------------------------------------------

df_athlete = load_athlete_data()
athlete = df_athlete.iloc[0]

st.title("Athlete Dashboard - Overview")

# --------------------------------------------------
# LOAD WEEKLY DATA
# --------------------------------------------------

df_week = load_weekly_summary()

if df_week.empty:
    st.warning("No weekly activity data available.")
    st.stop()

df_week["activity_week"] = pd.to_datetime(df_week["activity_week"])

# --------------------------------------------------
# CURRENT & PREVIOUS WEEK
# --------------------------------------------------

latest_week = df_week["activity_week"].max()
prev_week = latest_week - pd.Timedelta(days=7)

df_curr = df_week[df_week["activity_week"] == latest_week]
df_prev = df_week[df_week["activity_week"] == prev_week]

current_hours = df_curr["total_moving_time_h"].sum()
previous_hours = df_prev["total_moving_time_h"].sum()

delta_hours = current_hours - previous_hours
delta_pct = (delta_hours / previous_hours * 100) if previous_hours > 0 else 0

# --------------------------------------------------
# KPI ROW
# --------------------------------------------------
current_hours = df_curr["total_moving_time_h"].sum()
previous_hours = df_prev["total_moving_time_h"].sum()

current_distance = df_curr["total_distance_km"].sum()
previous_distance = df_prev["total_distance_km"].sum()

delta_hours = current_hours - previous_hours
delta_hours_pct = (
    delta_hours / previous_hours * 100
    if previous_hours > 0
    else 0
)

delta_distance = current_distance - previous_distance
delta_distance_pct = (
    delta_distance / previous_distance * 100
    if previous_distance > 0
    else 0
)

with st.container(border=True):
    col_time, col_dist = st.columns(2)

with col_time:
    st.metric(
        "Wochenzeit",
        f"{current_hours:.1f} h",
    )

    st.caption(
        f"Δ zur Vorwoche: "
        f"{delta_hours:+.1f} h "
        f"({delta_hours_pct:+.0f} %)"
    )

with col_dist:
    st.metric(
        "Wochendistanz",
        f"{current_distance:.1f} km",
    )

    st.caption(
        f"Δ zur Vorwoche: "
        f"{delta_distance:+.1f} km "
        f"({delta_distance_pct:+.0f} %)"
    )


metric = st.radio(
    "Metrik",
    options=["Stunden", "Distanz"],
    horizontal=True,
)

if metric == "Stunden":
    value_col = "total_moving_time_h"
    unit = "h"
    title = "Wochenstunden"
    tooltip_fmt = ".2f"
else:
    value_col = "total_distance_km"
    unit = "km"
    title = "Wochendistanz"
    tooltip_fmt = ".2f"

# --------------------------------------------------
# BREAKDOWN BY SPORT TYPE
# --------------------------------------------------

df_compare = (
    df_curr[["sport_type", value_col]]
    .merge(
        df_prev[["sport_type", value_col]],
        on="sport_type",
        how="left",
        suffixes=("_curr", "_prev"),
    )
    .fillna(0)
)

df_compare["delta_pct"] = (
    (df_compare[f"{value_col}_curr"]
     - df_compare[f"{value_col}_prev"])
    / df_compare[f"{value_col}_prev"]
).replace([float("inf"), -float("inf")], 0) * 100

breakdown_chart = (
    alt.Chart(df_compare)
    .mark_bar()
    .encode(
        x=alt.X("sport_type:N", title=None),
        y=alt.Y(f"{value_col}_curr:Q", title=unit),
        tooltip=[
            alt.Tooltip("sport_type:N", title="Sportart"),
            alt.Tooltip(
                f"{value_col}_curr:Q",
                title=title,
                format=tooltip_fmt,
            ),
            alt.Tooltip("delta_pct:Q", title="Δ %", format="+.2f"),
        ],
    )
    .properties(
        height=300,
        title=f"{title} nach Sportart",
    )
)

st.altair_chart(breakdown_chart, use_container_width=True)

###############
last_weeks = (
    df_week["activity_week"]
    .drop_duplicates()
    .sort_values()
    .tail(6)
)

df_last_weeks = df_week[df_week["activity_week"].isin(last_weeks)].copy()

df_last_weeks["week_label"] = df_last_weeks["activity_week"].dt.strftime("KW %V")


weekly_sport_chart = (
    alt.Chart(df_last_weeks)
    .mark_bar()
    .encode(
        x=alt.X(
            "sport_type:N",
            title=None,
        ),
        xOffset=alt.XOffset(
            "week_label:N",
            title="Woche",
        ),
        y=alt.Y(
            f"{value_col}:Q",
            title=f"{title} ({unit})",
        ),
        color=alt.Color(
            "week_label:N",
            title="Woche",
            legend=alt.Legend(orient="top"),
        ),
        tooltip=[
            alt.Tooltip("sport_type:N", title="Sportart"),
            alt.Tooltip("week_label:N", title="Woche"),
            alt.Tooltip(
                f"{value_col}:Q",
                title=title,
                format=".2f",
            ),
        ],
    )
    .properties(
        height=320,
        title=f"{title} pro Sportart – letzte 6 Wochen",
    )
)

st.altair_chart(weekly_sport_chart, use_container_width=True)

# --------------------------------------------------
# WEEKLY HISTORY (LAST 8 WEEKS)
# --------------------------------------------------

df_hist = (
    df_week.groupby("activity_week", as_index=False)[value_col]
    .sum()
    .sort_values("activity_week")
    .tail(6)
)

df_hist["week_label"] = df_hist["activity_week"].dt.strftime("KW %V")
latest_week = df_hist["activity_week"].max()


history_chart = (
    alt.Chart(df_hist)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X(
            "week_label:N",
            title=None,
            sort=None,
        ),
        y=alt.Y(
            f"{value_col}:Q",
            title=f"{title} ({unit})",
            axis=alt.Axis(grid=True),
        ),
        color=alt.condition(
            alt.datum.activity_week == latest_week,
            alt.value("#1f77b4"),   # aktuelle Woche
            alt.value("#d3d3d3"),   # frühere Wochen
        ),
        tooltip=[
            alt.Tooltip("week_label:N", title="Woche"),
            alt.Tooltip(
                f"{value_col}:Q",
                title=title,
                format=tooltip_fmt,
            ),
        ],
    )
    .properties(
        height=260,
        title=f"{title} - letzte 6 Wochen",
    )
)

st.altair_chart(history_chart, use_container_width=True)
