"""Defines the Pydantic model for Strava athlete information."""

from typing import Optional

from pydantic import BaseModel


class StravaAthleteInfo(BaseModel):
    """Pydantic model for Strava athlete information returned by the Strava API."""

    id: int
    username: Optional[str] = None
    resource_state: int
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    sex: Optional[str] = None
    premium: bool
    summit: bool
    created_at: str
    updated_at: str
    badge_type_id: Optional[int] = None
    weight: Optional[float] = None
    profile_medium: Optional[str] = None
    profile: Optional[str] = None
    friend: Optional[str] = None
    follower: Optional[str] = None
