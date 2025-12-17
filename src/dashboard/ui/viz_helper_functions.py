"""Helper functions for visualizing activities in the dashboard."""

import streamlit as st
import pandas as pd
import polyline
import pydeck as pdk

from dashboard.ui.constants import DEFAULT_COLOR, SPORT_COLORS

# =========================
# Helper: Map rendering
# =========================
def show_activity_map(
    map_polyline: str,
    height: int = 160,
    zoom: int = 12,
) -> None:
    """Render a small map preview for an activity using its encoded polyline."""
    try:
        coords = polyline.decode(map_polyline)

        if len(coords) < 5:
            st.caption("Route too short to display")
            return

        df = pd.DataFrame(coords, columns=["lat", "lng"])
        path = df[["lng", "lat"]].values.tolist()

        layer = pdk.Layer(
            "PathLayer",
            data=[{"path": path}],
            get_path="path",
            get_color=[255, 87, 34],
            width_scale=3,
            width_min_pixels=3,
        )

        view_state = pdk.ViewState(
            latitude=df["lat"].mean(),
            longitude=df["lng"].mean(),
            zoom=zoom,
        )

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style=None,
            ),
            height=height,
        )

    except Exception:
        st.caption("Failed to render map")


# =========================
# Helper: Sport badge
# =========================
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
