"""
Overview of athlete's gears from Strava API
Structured by gear type, KPI-driven, minimal charts.
"""

from queries import load_gear_details, viewer_email
import streamlit as st
from ui.constants import GEAR_TYPE_ORDER
from utilities.auth import logout_button, require_login


# -----------------
# Page config
# -----------------
st.set_page_config(page_title='Gear Overview', page_icon='👟', layout='wide')
# require_login()
logout_button('sidebar')

st.title('Gear Overview')
st.caption('Complete overview of all bikes, shoes and other gear')

# -----------------
# Load data
# -----------------
df_gear_details = load_gear_details(viewer_email())

if df_gear_details.empty:
    st.warning('No gear data available.')
    st.stop()

# -----------------
# Normalization
# -----------------
df_copy = df_gear_details.copy()

df_copy['name'] = df_copy['name'].fillna('(no name)')
df_copy['brand_name'] = df_copy['brand_name'].fillna('')
df_copy['model_name'] = df_copy['model_name'].fillna('')
df_copy['frame_type'] = df_copy['frame_type'].fillna('')
df_copy['weight_kg'] = df_copy['weight_kg'].round(2)

df_copy['status'] = df_copy['is_retired'].map({True: 'Retired', False: 'Active'})

# -------------------------------------------------
# Global KPIs
# -------------------------------------------------
st.subheader('Overall')

c1, c2, c3, c4 = st.columns(4)

c1.metric('Total Gears', len(df_copy))
c2.metric('Total Distance (km)', f'{df_copy["total_distance_km"].sum():,.1f}')
c3.metric('Active Gears', int((~df_copy['is_retired']).sum()))
c4.metric('Retired Gears', int(df_copy['is_retired'].sum()))

st.divider()

# -------------------------------------------------
# Section per Gear Type
# -------------------------------------------------
for gear_type in GEAR_TYPE_ORDER:
    subset = df_copy[df_copy['gear_type'] == gear_type].copy()
    if subset.empty:
        continue

    st.subheader(gear_type)

    # -----------------------------
    # Section KPIs
    # -----------------------------
    k1, k2, k3, k4 = st.columns(4)

    k1.metric('Count', len(subset))
    k2.metric('Total Distance (km)', f'{subset["total_distance_km"].sum():,.1f}')
    k3.metric('Avg Distance (km)', f'{subset["total_distance_km"].mean():,.0f}')
    k4.metric('Active', int((~subset['is_retired']).sum()))

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

    st.dataframe(table_df, width='stretch', hide_index=True)
    st.divider()
