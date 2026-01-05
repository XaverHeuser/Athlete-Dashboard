"""Activity details panel UI."""

import altair as alt
import pandas as pd
import streamlit as st
from ui.formatters import format_pace_min_per_km, format_seconds_to_hhmmss


def _downsample_streams(df: pd.DataFrame, max_points: int = 2500) -> pd.DataFrame:
    """Downsample by row stride to keep charts fast."""
    if df.empty:
        return df
    if len(df) <= max_points:
        return df
    step = max(1, len(df) // max_points)
    return df.iloc[::step].reset_index(drop=True)


def render_activity_details(
    *, activity_row: pd.Series, df_streams: pd.DataFrame
) -> None:
    """Render detail panel for a selected activity."""
    st.subheader(f'Details – {activity_row.get("activity_name", "Activity")}')

    # ---- High-level KPIs ----
    moving_time_str = format_seconds_to_hhmmss(
        int(activity_row.get('moving_time_s', 0) or 0)
    )
    pace_str = format_pace_min_per_km(activity_row.get('avg_pace_min_per_km'))

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric(
            'Distance', f'{float(activity_row.get("distance_km", 0.0) or 0.0):.2f} km'
        )
    with c2:
        st.metric('Moving time', f'{moving_time_str} h')
    with c3:
        st.metric('Avg pace', f'{pace_str} min/km')
    with c4:
        st.metric(
            'Avg HR', f'{float(activity_row.get("avg_heartrate", 0.0) or 0.0):.0f} bpm'
        )
    with c5:
        st.metric(
            'Avg speed',
            f'{float(activity_row.get("avg_speed_kph", 0.0) or 0.0):.2f} km/h',
        )
    with c6:
        st.metric(
            'Elev gain',
            f'{float(activity_row.get("elevation_gain_m", 0.0) or 0.0):.0f} m',
        )

    st.divider()

    # ---- Streams section ----
    if df_streams is None or df_streams.empty:
        st.info('No stream data available for this activity.')
        return

    df = df_streams.copy()

    # Ensure numeric types where present
    numeric_cols = [
        'time_s',
        'distance_m',
        'heartrate_bpm',
        'altitude_m',
        'velocity_smooth_mps',
        'cadence_rpm',
        'grade_smooth_pct',
        'lat',
        'lng',
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Derived fields
    if 'distance_m' in df.columns:
        df['distance_km'] = df['distance_m'] / 1000.0
    if 'velocity_smooth_mps' in df.columns:
        df['speed_kph'] = df['velocity_smooth_mps'] * 3.6
    if 'time_s' in df.columns:
        df['time_min'] = df['time_s'] / 60.0

    if 'time_s' not in df.columns:
        st.warning('Stream data has no time axis (time_s).')
        return

    df = df.dropna(subset=['time_s']).reset_index(drop=True)
    df = _downsample_streams(df, max_points=2500)

    chart_tab, map_tab = st.tabs(['Charts', 'Map'])

    with chart_tab:
        x_mode = st.radio(
            'X-axis',
            options=['Time (min)', 'Distance (km)'],
            horizontal=True,
            index=0,
            key=f'x_mode_{activity_row.get("activity_id", "unknown")}',
        )

        x_col = 'time_min' if x_mode == 'Time (min)' else 'distance_km'
        if x_col not in df.columns or df[x_col].isna().all():
            st.warning('Selected X-axis not available in stream data.')
            return

        def line_chart(y_col: str, title: str, y_title: str) -> None:
            if y_col not in df.columns or df[y_col].dropna().empty:
                st.caption(f'{title}: not available')
                return
            chart = (
                alt.Chart(df)
                .mark_line()
                .encode(
                    x=alt.X(x_col, title=x_mode),
                    y=alt.Y(y_col, title=y_title),
                    tooltip=[
                        alt.Tooltip(x_col, title=x_mode),
                        alt.Tooltip(y_col, title=y_title),
                    ],
                )
                .properties(title=title, height=220)
            )
            st.altair_chart(chart)

        cL, cR = st.columns(2)
        with cL:
            line_chart('heartrate_bpm', 'Heart rate', 'bpm')
            line_chart('altitude_m', 'Altitude', 'm')
        with cR:
            line_chart('speed_kph', 'Speed', 'km/h')
            line_chart('cadence_rpm', 'Cadence', 'rpm')

    with map_tab:
        has_latlng = (
            ('lat' in df.columns)
            and ('lng' in df.columns)
            and df['lat'].notna().any()
            and df['lng'].notna().any()
        )
        if not has_latlng:
            st.info('No lat/lng stream points available.')
        else:
            st.caption(
                'Lat/Lng stream points available. Next: render pydeck track map here.'
            )
            st.dataframe(df[['lat', 'lng']].dropna().head(50), width='stretch')
