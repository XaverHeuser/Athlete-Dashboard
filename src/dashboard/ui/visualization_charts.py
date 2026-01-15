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
from ui.formatters import fmt_hours_hhmm, hours_to_hhmm_series


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
        alt.Tooltip('moving_time_hhmm', title='Hours'),
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
    df['moving_time_hhmm'] = hours_to_hhmm_series(df['total_moving_time_h'])
    df['week_label'] = df['activity_week'].dt.strftime('KW %V')

    # Create chart
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X('week_label:N', title=None, sort=None),
            y=alt.Y('total_moving_time_h:Q', title='Hours'),
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
    df['moving_time_hhmm'] = hours_to_hhmm_series(df['total_moving_time_h'])
    df['week_label'] = df['activity_week'].dt.strftime('KW %V')

    # Create chart
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X('discipline:N', title=None),
            xOffset=alt.XOffset('week_label:N', title='Week'),
            y=alt.Y('total_moving_time_h:Q', title='Hours'),
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
@st.cache_data(show_spinner=False, ttl=3600)  # type: ignore[misc]
def prepare_donut_df(df: pd.DataFrame) -> pd.DataFrame:
    d = (
        filter_main_disciplines(df)
        .groupby('discipline', as_index=False)[
            ['total_moving_time_h', 'total_distance_km']
        ]
        .sum()
    )

    total_hours = float(d['total_moving_time_h'].sum())
    d['share_pct'] = (
        (d['total_moving_time_h'] / total_hours * 100) if total_hours else 0.0
    )
    d['moving_time_hhmm'] = hours_to_hhmm_series(d['total_moving_time_h'])
    d.attrs['total_hours'] = total_hours  # stash for center label
    return d


def render_distribution_donut(df: pd.DataFrame) -> alt.LayerChart:
    d = prepare_donut_df(df)
    total_hours = float(d.attrs.get('total_hours', 0.0))

    theta = alt.Theta('total_moving_time_h:Q', stack='zero')
    order = alt.Order('discipline:N', sort='descending')

    arcs = (
        alt.Chart(d)
        .mark_arc(innerRadius=60)
        .encode(
            theta=theta,
            order=order,
            color=alt.Color(
                'discipline:N', scale=COLOR_SCALE_MAIN_DISCIPLINES, legend=None
            ),
            tooltip=[
                alt.Tooltip('discipline:N', title='Discipline'),
                alt.Tooltip('moving_time_hhmm', title='Hours'),
                alt.Tooltip('total_distance_km:Q', title='Distance (km)', format='.1f'),
                alt.Tooltip('share_pct:Q', title='Share', format='.0f'),
            ],
        )
    )

    center_text = (
        alt.Chart(pd.DataFrame({'label': [fmt_hours_hhmm(total_hours)]}))
        .mark_text(fontSize=20, fontWeight='bold', color='white')
        .encode(text='label:N')
    )

    chart = alt.layer(arcs, center_text).properties(height=260)
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
