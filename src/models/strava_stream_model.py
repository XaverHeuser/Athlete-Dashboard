"""Pydantic models for Strava activity streams."""

from typing import Any, Optional

from pydantic import BaseModel, RootModel


class StravaStream(BaseModel):
    data: list[Any]
    original_size: Optional[int]
    resolution: Optional[str]


class StravaStreamsResponse(RootModel[dict[str, StravaStream]]):
    pass


class StravaActivityStreamRow(BaseModel):
    activity_id: int
    stream_type: str
    sequence_index: int
    value_float: Optional[float] = None
    value_int: Optional[int] = None
    value_bool: Optional[bool] = None
    value_lat: Optional[float] = None
    value_lng: Optional[float] = None
