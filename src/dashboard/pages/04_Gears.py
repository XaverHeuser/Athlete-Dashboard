"""
Overview of athlete's gears from Strava API
Structured by gear type, KPI-driven, minimal charts.
"""

import streamlit as st
import pandas as pd
from queries import load_gear_details

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title='👟Gear Overview',
    layout='wide',
)

st.title('Gear Overview')
st.caption('Complete overview of all bikes, shoes and other gear')

# -------------------------------------------------
# Load data
# -------------------------------------------------
df = load_gear_details()

if df.empty:
    st.warning('No gear data available.')
    st.stop()

# -------------------------------------------------
# Normalization
# -------------------------------------------------
df = df.copy()

df['name'] = df['name'].fillna('(no name)')
df['brand_name'] = df['brand_name'].fillna('')
df['model_name'] = df['model_name'].fillna('')
df['frame_type'] = df['frame_type'].fillna('')
df['weight_kg'] = df['weight_kg'].round(2)

df['status'] = df['is_retired'].map(
    {True: 'Retired', False: 'Active'}
)

# -------------------------------------------------
# Global KPIs
# -------------------------------------------------
st.subheader('Overall')

c1, c2, c3, c4 = st.columns(4)

c1.metric('Total Gears', len(df))
c2.metric('Total Distance (km)', f"{df['total_distance_km'].sum():,.1f}")
c3.metric('Active Gears', int((~df['is_retired']).sum()))
c4.metric('Retired Gears', int(df['is_retired'].sum()))

st.divider()

# -------------------------------------------------
# Section per Gear Type
# -------------------------------------------------
GEAR_TYPE_ORDER = ['Shoes', 'Bike', 'Other']

for gear_type in GEAR_TYPE_ORDER:
    subset = df[df['gear_type'] == gear_type].copy()
    if subset.empty:
        continue

    st.subheader(gear_type)

    # -----------------------------
    # Section KPIs
    # -----------------------------
    k1, k2, k3, k4 = st.columns(4)

    k1.metric('Count', len(subset))
    k2.metric(
        'Total Distance (km)',
        f"{subset['total_distance_km'].sum():,.1f}",
    )
    k3.metric(
        'Avg Distance (km)',
        f"{subset['total_distance_km'].mean():,.0f}",
    )
    k4.metric(
        'Active',
        int((~subset['is_retired']).sum()),
    )

    # -----------------------------
    # Table
    # -----------------------------
    display_cols = [
        'name',
        'total_distance_km',
        'brand_name',
        'model_name',
        'frame_type',
        'status',
        'weight_kg',
    ]

    table_df = (
        subset[display_cols]
        .sort_values('total_distance_km', ascending=False)
        .rename(
            columns={
                'name': 'Name',
                'total_distance_km': 'Distance (km)',
                'brand_name': 'Brand',
                'model_name': 'Model',
                'frame_type': 'Frame',
                'status': 'Status',
                'weight_kg': 'Weight (kg)',
            }
        )
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------
    # Optional minimal chart
    # -----------------------------
    import altair as alt

    with st.expander('Distance distribution'):
        chart_df = (
            subset[['name', 'total_distance_km']]
            .sort_values('total_distance_km', ascending=False)
        )

        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    'name:N',
                    sort='-y',
                    title='Gear',
                    axis=alt.Axis(labelAngle=0)
                ),
                y=alt.Y(
                    'total_distance_km:Q',
                    title='Distance (km)',
                    axis=alt.Axis(format=',.0f')
                ),
                tooltip=[
                    alt.Tooltip('name:N', title='Gear'),
                    alt.Tooltip('total_distance_km:Q', title='Distance (km)', format=',.1f'),
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart, use_container_width=True)

    st.divider()
