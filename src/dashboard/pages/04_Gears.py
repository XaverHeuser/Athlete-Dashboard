"""Overview of athlete's gears from Strava API (no filters, show everything)."""

from queries import load_gear_details
import streamlit as st

# TODO: Beautify with charts, filters, etc.
# Ideas:
# - NO overall information
# - Show information from top to bottom per sport type
# - Show numbers instead of charts or beautify charts
# - Show pictures of gears?

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title='Strava Gear Dashboard',
    layout='wide',
)

st.title('Strava Gear Overview')

# -------------------------------------------------
# Load data
# -------------------------------------------------
df = load_gear_details()

if df.empty:
    st.warning('No gear data available.')
    st.stop()

# -------------------------------------------------
# Normalize / safety
# -------------------------------------------------
# Ensure expected columns exist
required_cols = {
    'gear_id',
    'gear_type',
    'name',
    'brand_name',
    'model_name',
    'frame_type',
    'is_retired',
    'total_distance_km',
}
missing = required_cols - set(df.columns)
if missing:
    st.error(f'Missing columns in dataset: {sorted(missing)}')
    st.stop()

# Fill NaNs for display safety
df['name'] = df['name'].fillna('(no name)')
df['brand_name'] = df['brand_name'].fillna('')
df['model_name'] = df['model_name'].fillna('')
df['frame_type'] = df['frame_type'].fillna('Other')

# -------------------------------------------------
# KPIs (always use total_distance_km)
# -------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric('Total Gears', len(df))
kpi2.metric('Total Distance (km)', round(df['total_distance_km'].sum(), 1))
kpi3.metric('Active Gears', int((not df['is_retired']).sum()))
kpi4.metric('Retired Gears', int((df['is_retired']).sum()))

st.divider()

# -------------------------------------------------
# Charts (ONLY within same gear type -> separate chart per type)
# -------------------------------------------------
st.subheader('Distance per Gear (by Sport)')

gear_types = ['Bike', 'Shoes', 'Other']
for gt in gear_types:
    subset = df[df['gear_type'] == gt].copy()
    if subset.empty:
        continue

    st.markdown(f'### {gt}')

    chart_df = subset.sort_values('total_distance_km', ascending=False).set_index(
        'name'
    )

    st.bar_chart(chart_df['total_distance_km'])
