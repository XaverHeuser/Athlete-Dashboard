"""Defines model for Strava athlete statistics."""

from pydantic import BaseModel

class StravaAthleteStatsRecentTotals(BaseModel):
    count: int
    distance: float
    moving_time: int
    elapsed_time: int
    elevation_gain: float
    achievement_count: int

class StravaAthleteStatsAllTotals(BaseModel):
    count: int
    distance: float
    moving_time: int
    elapsed_time: int
    elevation_gain: float

class StravaAthleteStatsYearToDateTotals(BaseModel):
    count: int
    distance: float
    moving_time: float
    elapsed_time: float
    elevation_gain: float

class StravaAthleteStats(BaseModel):
    biggest_ride_distance: float
    biggest_climb_elevation_gain: float

    # Recent totals
    recent_ride_totals: StravaAthleteStatsRecentTotals
    recent_run_totals: StravaAthleteStatsRecentTotals
    recent_swim_totals: StravaAthleteStatsRecentTotals

    # All-time totals
    all_ride_totals: StravaAthleteStatsAllTotals
    all_run_totals: StravaAthleteStatsAllTotals
    all_swim_totals: StravaAthleteStatsAllTotals

    # Year-to-date totals
    ytd_ride_totals: StravaAthleteStatsYearToDateTotals
    ytd_run_totals: StravaAthleteStatsYearToDateTotals
    ytd_swim_totals: StravaAthleteStatsYearToDateTotals
    