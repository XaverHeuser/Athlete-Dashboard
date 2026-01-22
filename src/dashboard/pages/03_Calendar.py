from datetime import datetime, time as dtime, timedelta, timezone
import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import streamlit as st
from streamlit_calendar import calendar
from utilities.google_api import get_service, load_creds, make_flow
from utilities.google_calendar import (
    build_event_body,
    fetch_events,
    to_fullcalendar_events,
)


# ----------------
# Config
# ----------------
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = os.environ['GOOGLE_CLIENT_SECRET_FILE']
TOKEN_FILE = os.environ['GOOGLE_TOKEN_FILE']
CALENDAR_ID = os.environ['ATHLETE_CALENDER_ID']

st.set_page_config(page_title='Calendar', page_icon='📅', layout='wide')
st.title('Calendar')

if not CALENDAR_ID:
    st.error('No calendar available.')
    st.stop()

# ----------------------------
# Google Auth Flow (OAuth)
# ----------------------------
creds = load_creds(TOKEN_FILE, SCOPES)
if not creds or not creds.valid:
    flow = make_flow(CLIENT_SECRET_FILE, SCOPES)
    auth_url, _ = flow.authorization_url(
        access_type='offline', include_granted_scopes='true', prompt='consent'
    )
    st.link_button('Connect Google Calendar', auth_url)

    qp = st.query_params
    if 'code' in qp:
        flow.fetch_token(code=qp['code'])
        creds = flow.credentials
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

        st.success('Connected.')
        st.query_params.clear()
        st.rerun()

# Get Google Service
service = get_service(creds)

# ----------------------------
# Set calendar timespan
# ----------------------------
today = datetime.now().date()

st.markdown('Set datespan in which calendar items should be loaded')

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input('From', today - timedelta(days=30))
with col2:
    end_date = st.date_input('To', today + timedelta(days=90))
if end_date < start_date:
    st.error('End date must be after start date.')
    st.stop()

time_min = datetime.combine(
    start_date, datetime.min.time(), tzinfo=timezone.utc
).isoformat()
time_max = datetime.combine(
    end_date, datetime.max.time(), tzinfo=timezone.utc
).isoformat()

# ------------------------
# Load calendar events
# ------------------------
with st.spinner('Loading events...'):
    google_events = fetch_events(service, CALENDAR_ID, time_min, time_max)

fc_events = to_fullcalendar_events(google_events)
st.caption(f'Loaded {len(fc_events)} events.')

# -------------------
# Show calendar
# -------------------
options = {
    'initialView': 'dayGridMonth',
    'headerToolbar': {
        'left': 'prev,next today',
        'center': 'title',
        'right': 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
    },
    'height': 'auto',
    'nowIndicator': True,
    'selectable': True,
}
state = calendar(events=fc_events, options=options)

if state.get('eventClick'):
    ev = state['eventClick']['event']
    st.subheader('Selected event')
    st.json(ev)

# ----------------------------
# Create new event (clean form)
# ----------------------------
with st.expander('Create new event', expanded=False):
    with st.form('create_event_form'):
        main_column, date_column = st.columns([1, 1])

        # ------------------------
        # Main information
        # ------------------------
        with main_column:
            st.markdown('### Main information')

            title = st.text_input('Title *', placeholder='e.g., Easy Run / Swim / Ride')
            description = st.text_area('Description', height=100)
            location = st.text_input('Location', placeholder='e.g., Track / Gym')

        # -----------------
        # Date & Time
        # -----------------
        with date_column:
            st.markdown('### Date & time')

            timezone_name = st.selectbox('Time zone', ['Europe/Berlin', 'UTC'], index=0)
            all_day = st.toggle('All-day', value=True)

            local_today = datetime.now(ZoneInfo(timezone_name)).date()

            start_date_col, end_date_col = st.columns([1, 1])
            with start_date_col:
                start_date = st.date_input(
                    'Start date *', value=local_today, key='start_date'
                )
                start_time = st.time_input(
                    'Start time', value=dtime(9, 0), key='start_time'
                )
            with end_date_col:
                end_date = st.date_input(
                    'End date *', value=local_today, key='end_date'
                )
                end_time = st.time_input('End time', value=dtime(10, 0), key='end_time')

        # --------------------
        # Display options
        # --------------------
        st.markdown('### Display options')

        visibility = st.selectbox(
            'Visibility', ['default', 'public', 'private', 'confidential'], index=0
        )
        transparency_ui = st.selectbox('Transparency', ['Busy', 'Free'], index=0)
        transparency_val = 'opaque' if transparency_ui == 'Busy' else 'transparent'

        # -------------------------
        # Guests & Invitations
        # -------------------------
        st.markdown('### Guests / invitations')

        attendees_raw = st.text_input(
            'Invite guests (comma-separated emails)', placeholder='example@mail.com'
        )
        guests_can_invite_others = st.checkbox('Guests can invite others', value=True)
        guests_can_see_other_guests = st.checkbox(
            'Guests can see other guests', value=True
        )
        guests_can_modify = st.checkbox('Guests can modify event', value=False)

        # -------------------
        # Notifications
        # -------------------
        st.markdown('### Notifications / reminders')

        note_col1, note_col2, note_col3 = st.columns(3)
        with note_col1:
            reminder_value = st.number_input(
                'Reminder before event', min_value=0, value=6, step=1
            )
        with note_col2:
            reminder_unit = st.selectbox(
                'Unit',
                ['minutes', 'hours', 'days'],
                index=1,  # default: hours
            )
        with note_col3:
            method = st.selectbox('Method', ['popup', 'email'], index=0)

        UNIT_TO_MINUTES = {'minutes': 1, 'hours': 60, 'days': 1440}
        reminder_minutes = reminder_value * UNIT_TO_MINUTES[reminder_unit]
        reminder_overrides = [{'method': method, 'minutes': int(reminder_minutes)}]

        # ---------------------
        # Delivery Options
        # ---------------------
        st.markdown('### API delivery options')

        supports_attachments = st.checkbox('supportsAttachments', value=True)
        add_meet = st.checkbox('Add Google Meet link', value=False)

        send_updates_ui = st.selectbox(
            'Send notifications',
            options=[
                ('Do not send', 'none'),
                ('Notify all guests', 'all'),
                ('Notify external guests only', 'externalOnly'),
            ],
            format_func=lambda x: x[0],
        )
        send_updates = send_updates_ui[1]

        # ----------------
        # Submit form
        # ----------------
        submitted = st.form_submit_button('Create event')
        if submitted:
            # Title is required
            if not title.strip():
                st.error('Title is required.')
                st.stop()

            try:
                body, insert_extra = build_event_body(
                    title=title,
                    description=description,
                    location=location,
                    all_day=all_day,
                    timezone_name=timezone_name,
                    start_date=start_date,
                    end_date=end_date,
                    start_time=start_time,
                    end_time=end_time,
                    visibility=visibility,
                    transparency=transparency_val,
                    attendees_raw=attendees_raw,
                    guests_can_invite_others=guests_can_invite_others,
                    guests_can_modify=guests_can_modify,
                    guests_can_see_other_guests=guests_can_see_other_guests,
                    reminder_overrides=reminder_overrides,
                    add_meet=add_meet,
                )
            except ValueError as e:
                st.error(str(e))
                st.stop()

            created = (
                service
                .events()
                .insert(
                    calendarId=CALENDAR_ID,
                    body=body,
                    sendUpdates=send_updates,
                    supportsAttachments=supports_attachments,
                    **insert_extra,
                )
                .execute()
            )

            st.success('Event created.')
            if created.get('htmlLink'):
                st.markdown(f'[Open in Google Calendar]({created["htmlLink"]})')

            st.rerun()
