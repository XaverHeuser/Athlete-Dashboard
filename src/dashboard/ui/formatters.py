"""Formatters for displaying data in the dashboard UI."""

from typing import Any, Optional

import pandas as pd


# ------------------
# KPI formatters
# ------------------
def format_seconds_to_hhmmss(seconds: int) -> str:
    """Format seconds as H:MM:SS string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f'{h}:{m:02d}:{s:02d}'


def format_pace_min_per_km(pace_min: float) -> str:
    """Format pace in minutes per kilometer as M:SS string."""
    if pd.isna(pace_min) or pace_min <= 0:
        return '-:-'
    total_seconds = int(round(pace_min * 60))
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f'{minutes}:{seconds:02d}'


def format_speed_kph(speed_kph: float) -> str:
    """Format speed in kilometers per hour with two decimal places."""
    if pd.isna(speed_kph) or speed_kph <= 0:
        return '-.-'
    return f'{speed_kph:.2f}'


def fmt_hours_hhmm(
    hours: Optional[float], *, signed: bool = False, empty: str = '-'
) -> str:
    """Convert decimal hours (e.g. 2.5) to hh:mmh (e.g. 2:30h)."""
    if hours is None or pd.isna(hours):
        return empty

    h_val = float(hours)
    sign = ''
    if signed:
        sign = '+' if h_val > 0 else '-' if h_val < 0 else ''

    minutes_total = int(round(abs(h_val) * 60))
    hh, mm = divmod(minutes_total, 60)
    return f'{sign}{hh}:{mm:02d}h'


def hours_to_hhmm_series(hours: pd.Series, *, empty: str = '-') -> pd.Series:
    s = pd.to_numeric(hours, errors='coerce')  # ensures NaN for invalid
    mins = (s.abs() * 60).round().astype('Int64')  # nullable int
    hh = (mins // 60).astype('Int64')
    mm = (mins % 60).astype('Int64')

    out = hh.astype(str) + ':' + mm.astype(str).str.zfill(2) + 'h'
    out = out.where(s.notna(), empty)

    return out


# ------------------------
# Profile helpers
# ------------------------
def fmt_date(x: Any) -> str:
    try:
        return str(pd.to_datetime(x).date().isoformat())
    except Exception:
        return '—'


def fmt_dt(x: Any) -> str:
    try:
        return str(pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S'))
    except Exception:
        return '—'


def fmt_str(x: str) -> str:
    if x is None:
        return '—'
    s = str(x).strip()
    return s if s and s.lower() != 'nan' else '—'


def fmt_weight(x: Any) -> str:
    if x is None or pd.isna(x):
        return '-'
    return f'{float(x):.1f} kg'
