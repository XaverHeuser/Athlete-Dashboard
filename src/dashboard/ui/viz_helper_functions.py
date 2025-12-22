"""Helper functions for visualizing activities in the dashboard."""

import altair as alt
import pandas as pd
import polyline
import pydeck as pdk
import streamlit as st
from ui.constants import DEFAULT_COLOR, MAIN_SPORT_COLORS, MAIN_SPORTS, SPORT_COLORS


# ------------------------
# Shared helopers
# ------------------------
def filter_main_sports(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe filtered to MAIN_SPORTS only."""
    return df.loc[df['sport_type'].isin(MAIN_SPORTS)].copy()


def base_hours_distance_tooltip() -> list[alt.Tooltip]:
    """Standard tooltip showing hours and distance."""
    return [
        alt.Tooltip('total_moving_time_h:Q', title='Hours', format='.1f'),
        alt.Tooltip('total_distance_km:Q', title='Distance (km)', format='.1f'),
    ]


COLOR_SCALE_MAIN_SPORTS = alt.Scale(
    domain=list(MAIN_SPORT_COLORS.keys()), range=list(MAIN_SPORT_COLORS.values())
)


# --------------------------
# Discipline donut chart
# --------------------------
def render_discipline_donut(df: pd.DataFrame, title: str) -> alt.Chart:
    """Render a discipline distribution donut chart based on moving time."""
    # Prepare data
    df = (
        filter_main_sports(df)
        .groupby('sport_type', as_index=False)[
            ['total_moving_time_h', 'total_distance_km']
        ]
        .sum()
    )

    total_hours = df['total_moving_time_h'].sum()
    df['share_pct'] = df['total_moving_time_h'] / df['total_moving_time_h'].sum() * 100

    # Prepare chart
    theta = alt.Theta('total_moving_time_h:Q', stack='zero')
    order = alt.Order('sport_type:N', sort='descending')

    arc_labels = (
        alt
        .Chart(df)
        .mark_text(radius=90, size=12, fontWeight='bold')
        .encode(
            theta=theta,
            order=order,
            text=alt.Text('total_moving_time_h:Q', format='.1f'),
            color=alt.value('white'),
        )
    )

    center_text = (
        alt
        .Chart(pd.DataFrame({'label': [f'{total_hours:.1f} h']}))
        .mark_text(fontSize=20, fontWeight='bold', color='white')
        .encode(text='label:N')
    )

    chart = alt.layer(
        alt
        .Chart(df)
        .mark_arc(innerRadius=60)
        .encode(
            theta=theta,
            order=order,
            color=alt.Color('sport_type:N', scale=COLOR_SCALE_MAIN_SPORTS, legend=None),
            tooltip=[
                alt.Tooltip('sport_type:N', title='Sport type'),
                alt.Tooltip('total_moving_time_h:Q', title='Hours', format='.1f'),
                alt.Tooltip('total_distance_km:Q', title='Distance (km)', format='.1f'),
                alt.Tooltip('share_pct:Q', title='PCT', format='.0f'),
            ],
        ),
        center_text,
        arc_labels,
    ).properties(height=260)

    return chart


# --------------------------
# Weekly charts rendering
# --------------------------
def _prepare_weekly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weekly hours and distance for MAIN_SPORTS."""
    return (
        filter_main_sports(df)
        .groupby('activity_week', as_index=False)[
            ['total_moving_time_h', 'total_distance_km']
        ]
        .sum()
        .sort_values('activity_week')
        .tail(4)
        .copy()
    )


def render_weekly_hours_chart(df: pd.DataFrame, title: str) -> alt.Chart:
    """Render a compact weekly hours bar chart (last 4 weeks)."""
    df = _prepare_weekly_aggregation(df)
    df['week_label'] = df['activity_week'].dt.strftime('KW %V')

    latest_week = df['activity_week'].max()
    df['is_latest'] = df['activity_week'].eq(latest_week)

    chart = (
        alt
        .Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X('week_label:N', title=None, sort=None),
            y=alt.Y('total_moving_time_h:Q', title='Hours (h)'),
            color=alt.condition(
                alt.datum.is_latest, alt.value('#1f77b4'), alt.value('#d3d3d3')
            ),
            tooltip=[
                alt.Tooltip('week_label:N', title='Week'),
                *base_hours_distance_tooltip(),
            ],
        )
        .properties(height=260, title=f'{title} - Last 4 weeks')
    )

    return chart


def render_weekly_hours_per_sport_chart(df: pd.DataFrame, title: str) -> alt.Chart:
    """Render grouped weekly hours per sport for the last 4 weeks."""
    df = filter_main_sports(df)
    df['week_label'] = df['activity_week'].dt.strftime('KW %V')

    return (
        alt
        .Chart(df)
        .mark_bar()
        .encode(
            x=alt.X('sport_type:N', title=None),
            xOffset=alt.XOffset('week_label:N', title='Week'),
            y=alt.Y('total_moving_time_h:Q', title='Hours (h)'),
            color=alt.Color('sport_type:N', scale=COLOR_SCALE_MAIN_SPORTS, legend=None),
            tooltip=[
                alt.Tooltip('sport_type:N', title='Sport'),
                alt.Tooltip('week_label:N', title='Week'),
                *base_hours_distance_tooltip(),
            ],
        )
        .properties(height=320, title=title)
    )


# --------------------------
# Map rendering
# --------------------------
def show_activity_map(map_polyline: str, height: int = 160, zoom: int = 12) -> None:
    """Render a small map preview for an activity using its encoded polyline."""
    try:
        coords = polyline.decode(map_polyline)
        if len(coords) < 5:
            st.caption('Route too short to display')
            return

        df = pd.DataFrame(coords, columns=['lat', 'lng'])
        path = df[['lng', 'lat']].values.tolist()

        layer = pdk.Layer(
            'PathLayer',
            data=[{'path': path}],
            get_path='path',
            get_color=[255, 87, 34],
            width_scale=3,
            width_min_pixels=3,
        )

        view_state = pdk.ViewState(
            latitude=df['lat'].mean(), longitude=df['lng'].mean(), zoom=zoom
        )

        st.pydeck_chart(
            pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=None),
            height=height,
        )

    except Exception:
        st.caption('Failed to render map')


# ----------------------
# UI helpers
# ----------------------
def sport_badge(sport: str) -> None:
    color = SPORT_COLORS.get(sport, DEFAULT_COLOR)

    st.markdown(
        f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        ">
            {sport}
        </span>
        """,
        unsafe_allow_html=True,
    )
