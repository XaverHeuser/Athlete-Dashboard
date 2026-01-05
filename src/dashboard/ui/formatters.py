"""Formatters for displaying data in the dashboard UI."""

import pandas as pd


def format_seconds_to_hhmmss(seconds: int) -> str:
    """Format seconds as H:MM:SS string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f'{h}:{m:02d}:{s:02d}'


def format_pace_min_per_km(pace_min: float) -> str:
    """Format pace in minutes per kilometer as M:SS string."""
    if pd.isna(pace_min) or pace_min <= 0:
        return '–:–'
    total_seconds = int(round(pace_min * 60))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f'{minutes}:{seconds:02d}'


def format_speed_kph(speed_kph: float) -> str:
    """Format speed in kilometers per hour with two decimal places."""
    if pd.isna(speed_kph) or speed_kph <= 0:
        return '–.–'
    return f'{speed_kph:.2f}'
