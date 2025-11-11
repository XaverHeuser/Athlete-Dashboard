"""Defines the Pydantic model for Strava activities."""

from typing import Any, Optional

from pydantic import BaseModel


class StravaAthlete(BaseModel):
    id: Optional[int] = None
    resource_state: Optional[int] = None


class StravaMap(BaseModel):
    id: Optional[str] = None
    summary_polyline: Optional[str] = None
    resource_state: Optional[int] = None


class StravaActivity(BaseModel):
    """Pydantic model for a Strava activity returned by the Strava API."""

    # General metadata
    resource_state: Optional[int] = None
    name: Optional[str] = None
    distance: Optional[float] = None
    moving_time: Optional[int] = None
    elapsed_time: Optional[int] = None
    total_elevation_gain: Optional[float] = None
    type: Optional[str] = None  # 'Deprecated. Prefer to use sport_type'
    sport_type: Optional[str] = None
    workout_type: Optional[float] = None
    id: int

    # Time info
    start_date: Optional[str] = None
    start_date_local: Optional[str] = None
    timezone: Optional[str] = None
    utc_offset: Optional[float] = None

    # Location
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    location_country: Optional[str] = None

    # Social/Engagement stats
    achievement_count: Optional[int] = None
    kudos_count: Optional[int] = None
    comment_count: Optional[int] = None
    athlete_count: Optional[int] = None
    photo_count: Optional[int] = None

    # Boolean flags
    trainer: Optional[bool] = None
    commute: Optional[bool] = None
    manual: Optional[bool] = None
    private: Optional[bool] = None
    flagged: Optional[bool] = None
    has_kudoed: Optional[bool] = None
    from_accepted_tag: Optional[bool] = None
    visibility: Optional[str] = None

    # Equipment & mapping
    gear_id: Optional[str] = None
    start_latlng: Optional[Any] = None
    end_latlng: Optional[Any] = None

    # Nested objects
    athlete: Optional[StravaAthlete] = None
    map: Optional[StravaMap] = None

    # Performance metrics
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None
    has_heartrate: Optional[bool] = None
    heartrate_opt_out: Optional[bool] = None
    display_hide_heartrate_option: Optional[bool] = None
    average_cadence: Optional[float] = None
    average_temp: Optional[float] = None
    average_watts: Optional[float] = None
    max_watts: Optional[float] = None
    weighted_average_watts: Optional[float] = None
    device_watts: Optional[Any] = None
    kilojoules: Optional[float] = None
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    elev_high: Optional[float] = None
    elev_low: Optional[float] = None

    # Upload info
    upload_id: Optional[int] = None
    upload_id_str: Optional[str] = None
    external_id: Optional[str] = None
    pr_count: Optional[int] = None
    total_photo_count: Optional[int] = None

    class Config:
        extra = 'ignore'  # Ignore unexpected fields (Strava adds new ones often)
        populate_by_name = True  # Allow alias mapping to nested fields
