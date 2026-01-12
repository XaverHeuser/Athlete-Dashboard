"""Helper functions for visualizing activities in the dashboard."""

from typing import cast

import altair as alt
import pandas as pd
import polyline
import pydeck as pdk
import streamlit as st
from ui.constants import (
    DEFAULT_COLOR,
    MAIN_DISCIPLINES,
    MAIN_SPORT_COLORS,
    SPORT_COLORS,
)


# -------------------
# Constants
# -------------------
COLOR_SCALE_MAIN_DISCIPLINES = alt.Scale(
    domain=list(MAIN_SPORT_COLORS.keys()), range=list(MAIN_SPORT_COLORS.values())
)


# ------------------------
# Internal Helpers
# ------------------------
def filter_main_disciplines(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe filtered to DISCIPLINES only."""
    return df.loc[df['discipline'].isin(MAIN_DISCIPLINES)].copy()


def base_hours_distance_tooltip() -> list[alt.Tooltip]:
    """Standard tooltip showing hours and distance."""
    return [
        alt.Tooltip('total_moving_time_h:Q', title='Hours', format='.1f'),
        alt.Tooltip('total_distance_km:Q', title='Distance (km)', format='.1f'),
    ]


def _prepare_weekly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weekly hours and distance for DISCIPLINES."""
    return (
        filter_main_disciplines(df)
        .groupby('activity_week', as_index=False)[
            ['total_moving_time_h', 'total_distance_km']
        ]
        .sum()
        .sort_values('activity_week')
        .tail(4)
        .copy()
    )


# -------------------------
# Render weekly charts
# -------------------------
def render_weekly_hours_chart(df: pd.DataFrame, title: str) -> alt.Chart:
    """Render a compact weekly hours bar chart (last 4 weeks)."""
    # Data prep
    df = _prepare_weekly_aggregation(df)
    df['week_label'] = df['activity_week'].dt.strftime('KW %V')

    # Create chart
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X('week_label:N', title=None, sort=None),
            y=alt.Y('total_moving_time_h:Q', title='Hours (h)'),
            color=alt.value('#d3d3d3'),
            tooltip=[
                alt.Tooltip('week_label:N', title='Week'),
                *base_hours_distance_tooltip(),
            ],
        )
        .properties(height=200, title=f'{title}')
    )

    return cast(alt.Chart, chart)


def render_weekly_hours_per_sport_chart(df: pd.DataFrame, title: str) -> alt.Chart:
    """Render grouped weekly hours per sport for the last 4 weeks."""
    # Data prep
    df = filter_main_disciplines(df)
    df['week_label'] = df['activity_week'].dt.strftime('KW %V')

    # Create chart
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X('discipline:N', title=None),
            xOffset=alt.XOffset('week_label:N', title='Week'),
            y=alt.Y('total_moving_time_h:Q', title='Hours (h)'),
            color=alt.Color(
                'discipline:N', scale=COLOR_SCALE_MAIN_DISCIPLINES, legend=None
            ),
            tooltip=[
                alt.Tooltip('discipline:N', title='Discipline'),
                alt.Tooltip('week_label:N', title='Week'),
                *base_hours_distance_tooltip(),
            ],
        )
        .properties(height=220, title=title)
    )
    return cast(alt.Chart, chart)


# ---------------------------------------
# Discipline distribution donut chart
# ---------------------------------------
def render_distribution_donut(df: pd.DataFrame) -> alt.LayerChart:
    """Render a discipline distribution donut chart based on moving time."""
    # Prepare data
    df = (
        filter_main_disciplines(df)
        .groupby('discipline', as_index=False)[
            ['total_moving_time_h', 'total_distance_km']
        ]
        .sum()
    )

    total_hours = df['total_moving_time_h'].sum()
    df['share_pct'] = df['total_moving_time_h'] / df['total_moving_time_h'].sum() * 100

    # Prepare chart
    theta = alt.Theta('total_moving_time_h:Q', stack='zero')
    order = alt.Order('discipline:N', sort='descending')

    # Create nice labels
    arc_labels = (
        alt.Chart(df)
        .mark_text(radius=90, size=12, fontWeight='bold')
        .encode(
            theta=theta,
            order=order,
            text=alt.Text('total_moving_time_h:Q', format='.1f'),
            color=alt.value('white'),
        )
    )

    # Center labels for each discipline
    center_text = (
        alt.Chart(pd.DataFrame({'label': [f'{total_hours:.1f} h']}))
        .mark_text(fontSize=20, fontWeight='bold', color='white')
        .encode(text='label:N')
    )

    # Final chart
    chart = alt.layer(
        alt.Chart(df)
        .mark_arc(innerRadius=60)
        .encode(
            theta=theta,
            order=order,
            color=alt.Color(
                'discipline:N', scale=COLOR_SCALE_MAIN_DISCIPLINES, legend=None
            ),
            tooltip=[
                alt.Tooltip('discipline:N', title='Discipline'),
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
# UI Elements
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
