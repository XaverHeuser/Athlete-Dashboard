"""Strava Gear Model Definition."""

from typing import Optional

from pydantic import BaseModel


class StravaGear(BaseModel):
    id: str

    primary: Optional[bool] = None

    name: Optional[str] = None
    nickname: Optional[str] = None

    resource_state: Optional[int] = None
    retired: Optional[bool] = None

    distance: Optional[int] = None
    converted_distance: Optional[float] = None

    brand_name: Optional[str] = None
    model_name: Optional[str] = None

    frame_type: Optional[float] = None
    description: Optional[str] = None

    weight: Optional[float] = None
    notification_distance: Optional[float] = None
