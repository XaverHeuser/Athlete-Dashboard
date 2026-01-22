from queries import load_athlete_data
import streamlit as st
from ui.formatters import fmt_date, fmt_dt, fmt_str, fmt_weight


# -------------------------
# Page configuration
# -------------------------
st.set_page_config(page_title='Athlete Profile', page_icon='👤', layout='wide')


# -------------------------
# Light CSS (optional, but helps a lot)
# -------------------------
st.markdown(
    """
<style>
/* tighten overall top spacing */
.block-container { padding-top: 1.5rem; }

/* simple “card” look */
.card {
  border: 1px solid rgba(49, 51, 63, 0.15);
  border-radius: 16px;
  padding: 18px 18px;
  background: rgba(255, 255, 255, 0.02);
}

/* badge */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid rgba(49, 51, 63, 0.18);
  margin-left: 8px;
  vertical-align: middle;
}

.badge-premium { background: rgba(0, 200, 120, 0.10); }
.badge-free    { background: rgba(255, 90, 90, 0.10); }

.muted { opacity: 0.75; }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------
# Load athlete information
# -------------------------
try:
    df_athlete = load_athlete_data()
    if df_athlete.empty:
        st.warning('No athlete data found.')
        st.stop()
    athlete = df_athlete.iloc[0].to_dict()
except Exception as e:
    st.error(f'Failed to load athlete data: {e}')
    st.stop()

# -------------------------
# Header section (image + identity)
# -------------------------
left, right = st.columns([1, 2], vertical_alignment='center')

with left:
    img_url = athlete.get('profile_img_url')
    if fmt_str(img_url) != '—':
        st.image(img_url, width=220)
    else:
        st.info('No profile image available.')

with right:
    firstname = fmt_str(athlete.get('firstname'))
    lastname = fmt_str(athlete.get('lastname'))
    username = fmt_str(athlete.get('username'))
    bio = fmt_str(athlete.get('bio'))

    premium = bool(athlete.get('is_premium_user'))
    badge_class = 'badge-premium' if premium else 'badge-free'
    badge_text = 'Premium' if premium else 'Free'

    st.markdown(
        f"""
<div class="card">
  <div style="font-size: 2.0rem; font-weight: 700; line-height: 1.15;">
    {firstname} {lastname}
    <span class="badge {badge_class}">{badge_text}</span>
  </div>
  <div class="muted" style="margin-top: 6px;">
    @{username} • Athlete ID: {fmt_str(athlete.get('athlete_id'))}
  </div>
  <div style="margin-top: 12px; font-size: 1.02rem;">
    {bio}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.write('')  # spacing

# -------------------------
# KPI row (clean + scannable)
# -------------------------
c1, c2, c3, c4, c5 = st.columns(5)

location = (
    ', '.join([
        p
        for p in [
            fmt_str(athlete.get('city')),
            fmt_str(athlete.get('state')),
            fmt_str(athlete.get('country')),
        ]
        if p != '—'
    ])
    or '—'
)

with c1:
    st.metric('Total activities', int(athlete.get('total_activities') or 0))
with c2:
    st.metric('Last activity', fmt_date(athlete.get('last_activity_date')))
with c3:
    st.metric('First activity', fmt_date(athlete.get('first_activity_date')))
with c4:
    st.metric('Weight', fmt_weight(athlete.get('weight_kg')))
with c5:
    st.metric('Location', location)

st.divider()

# -------------------------
# Details section (tabs + columns)
# -------------------------
tab_profile, tab_account = st.tabs(['Profile', 'Account'])

with tab_profile:
    colA, colB = st.columns(2)

    with colA:
        st.subheader('Personal')
        st.write(f'**Gender:** {fmt_str(athlete.get("sex"))}')
        st.write(f'**Location:** {location}')

    with colB:
        st.subheader('Membership')
        st.write(f'**Plan:** {"Premium" if premium else "Free"}')
        st.write(f'**Username:** @{username}')

with tab_account:
    colA, colB = st.columns(2)

    with colA:
        st.subheader('Timeline')
        st.write(f'**Account created:** {fmt_date(athlete.get("created_at"))}')
        st.write(f'**First activity:** {fmt_date(athlete.get("first_activity_date"))}')
        st.write(f'**Last activity:** {fmt_date(athlete.get("last_activity_date"))}')

    with colB:
        st.subheader('Identifiers')
        st.write(f'**Athlete ID:** {fmt_str(athlete.get("athlete_id"))}')
        st.write(f'**Username:** @{username}')

st.divider()
st.caption(f'Data last loaded at: {fmt_dt(athlete.get("mart_loaded_at"))}')
