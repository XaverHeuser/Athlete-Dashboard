"""This file contains google calendar communication functions."""

from datetime import date, datetime, time as dtime, timedelta
from typing import Any, Literal
import uuid
from zoneinfo import ZoneInfo

from googleapiclient.discovery import Resource
from ui.constants import GOOGLE_COLOR_ID_BY_SPORT, MAIN_SPORT_COLORS


# ----------------------
# Event fetcher
# ----------------------
def fetch_events(
    service: Resource, calendar_id: str, time_min: str, time_max: str
) -> list[dict[str, Any]]:
    """Fetch google calendar events from given calendar in given time-range."""
    items = []
    page_token = None
    while True:
        response = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=2500,
                pageToken=page_token,
            )
            .execute()
        )

        items.extend(response.get('items', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return items


# -----------------------
# Event converter
# -----------------------
def to_fullcalendar_events(google_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Converts a Google Calendar event into FullCalendar event."""
    events: list[dict[str, Any]] = []
    for event in google_events:
        start = event.get('start', {})
        end = event.get('end', {})

        start_val = start.get('dateTime') or start.get('date')
        end_val = end.get('dateTime') or end.get('date')

        title = event.get('summary', '(no title)')
        color = fullcalendar_color_from_title(title)

        full_calendar_event: dict[str, Any] = {
            'id': event.get('id'),
            'title': title,
            'start': start_val,
            'end': end_val,
            'allDay': 'date' in start,
        }

        # FullCalendar styling (HEX supported)
        if color:
            full_calendar_event['backgroundColor'] = color
            full_calendar_event['borderColor'] = color

        events.append(full_calendar_event)

    return events


# ---------------------
# Event creation
# ---------------------
def build_event_body(
    *,
    title: str,
    description: str,
    location: str,
    all_day: bool,
    timezone_name: str,
    start_date: date,
    end_date: date,
    start_time: dtime | None,
    end_time: dtime | None,
    visibility: str,
    transparency: str,
    attendees_raw: str,
    guests_can_invite_others: bool,
    guests_can_modify: bool,
    guests_can_see_other_guests: bool,
    reminder_overrides: list[dict[str, str | int]],
    add_meet: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (event_body, insert_kwargs_extra) for Google Calendar events.insert()."""
    body: dict[str, Any] = {
        'summary': title.strip(),
        'description': (description or '').strip(),
        'location': (location or '').strip(),
        'visibility': visibility,  # default/public/private/confidential
        'transparency': transparency,  # opaque/transparent
        'guestsCanInviteOthers': guests_can_invite_others,
        'guestsCanModify': guests_can_modify,
        'guestsCanSeeOtherGuests': guests_can_see_other_guests,
    }

    # Time handling
    if all_day:
        if end_date < start_date:
            raise ValueError('End date must be on/after start date for all-day events.')
        body['start'] = {'date': start_date.isoformat()}
        # Google all-day end date is exclusive -> +1 day so single-day works.
        body['end'] = {'date': (end_date + timedelta(days=1)).isoformat()}
    else:
        if start_time is None or end_time is None:
            raise ValueError('Start/end time required for timed events.')

        tz = ZoneInfo(timezone_name)  # keep timezone_name as str
        start_dt = datetime.combine(start_date, start_time, tzinfo=tz)
        end_dt = datetime.combine(end_date, end_time, tzinfo=tz)
        if end_dt <= start_dt:
            raise ValueError('End must be after start.')
        body['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': timezone_name}
        body['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': timezone_name}

    # Attendees in correct format
    body['attendees'] = parse_attendees(attendees_raw)

    # Reminders
    body['reminders'] = {'useDefault': False, 'overrides': reminder_overrides}

    # Set color
    body['colorId'] = set_color_id_new_events(title)

    # Insert extra information
    insert_extra = {}
    if add_meet:
        body['conferenceData'] = {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        }
        insert_extra['conferenceDataVersion'] = 1

    return clean_dict(body), insert_extra


# -------------------------
# Event creation helpers
# -------------------------
def clean_dict(d: dict[Any, Any]) -> dict[str, Any]:
    """Recursively remove empty values from a mapping."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = clean_dict(v)
        if v is None or v == '' or v == []:
            continue
        out[k] = v
    return out


def parse_attendees(raw: str) -> list[dict[str, str]]:
    """Parse attendees to a valid format."""
    emails = [e.strip() for e in (raw or '').split(',') if e.strip()]
    return [{'email': e} for e in emails]


# Helpers for colors in Calendar
Sport = Literal['Run', 'Ride', 'Swim', 'Strength']


def sport_from_title(title: str) -> Sport | None:
    """Function to extract the sport based on the event title."""
    t = title.lower()
    if 'run' in t:
        return 'Run'
    if 'ride' in t or 'bike' in t or 'cycling' in t:
        return 'Ride'
    if 'swim' in t:
        return 'Swim'
    if 'workout' in t or 'strength' in t or 'gym' in t:
        return 'Strength'
    return None


def fullcalendar_color_from_title(title: str) -> str | None:
    """Function to get color based on event title."""
    sport = sport_from_title(title)
    return MAIN_SPORT_COLORS.get(sport) if sport else None


def set_color_id_new_events(title: str) -> str | None:
    """Function to get Google color id for new events."""
    sport = sport_from_title(title)
    return GOOGLE_COLOR_ID_BY_SPORT.get(sport) if sport else None
