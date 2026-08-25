"""
Market Conventions, Day-Count Fractions, and Timezone Utilities.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Union

import pandas as pd


class DayCountConvention(str, Enum):
    ACT_365 = "ACT/365"
    ACT_360 = "ACT/360"
    THIRTY_360 = "30/360"
    ACT_ACT = "ACT/ACT"


def to_utc_datetime(dt: Union[str, datetime, date, pd.Timestamp]) -> datetime:
    """
    Normalize any date/timestamp into a timezone-aware UTC datetime.
    """
    if isinstance(dt, str):
        ts = pd.to_datetime(dt)
    elif isinstance(dt, date) and not isinstance(dt, datetime):
        ts = datetime.combine(dt, datetime.min.time(), tzinfo=timezone.utc)
        return ts
    else:
        ts = dt

    if isinstance(ts, pd.Timestamp):
        if ts.tz is None:
            ts = ts.tz_localize("UTC")
        else:
            ts = ts.tz_convert("UTC")
        return ts.to_pydatetime()

    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)

    raise ValueError(f"Cannot convert {type(dt)} to UTC datetime: {dt}")


def year_fraction(
    start_date: Union[str, datetime, date],
    end_date: Union[str, datetime, date],
    convention: Union[str, DayCountConvention] = DayCountConvention.ACT_365,
) -> float:
    """
    Calculate the year fraction between two dates according to the chosen day count convention.
    """
    d1 = to_utc_datetime(start_date)
    d2 = to_utc_datetime(end_date)

    if d2 < d1:
        return 0.0

    conv = DayCountConvention(convention) if isinstance(convention, str) else convention

    if conv == DayCountConvention.ACT_365:
        return (d2 - d1).total_seconds() / (365.0 * 86400.0)
    elif conv == DayCountConvention.ACT_360:
        return (d2 - d1).total_seconds() / (360.0 * 86400.0)
    elif conv == DayCountConvention.THIRTY_360:
        d1_day = min(d1.day, 30)
        d2_day = min(d2.day, 30) if d1_day == 30 else d2.day
        days = 360 * (d2.year - d1.year) + 30 * (d2.month - d1.month) + (d2_day - d1_day)
        return days / 360.0
    elif conv == DayCountConvention.ACT_ACT:
        # Simple ACT/ACT
        days = (d2.date() - d1.date()).days
        days_in_year = 366.0 if (d1.year % 4 == 0 and (d1.year % 100 != 0 or d1.year % 400 == 0)) else 365.0
        return (d2 - d1).total_seconds() / (days_in_year * 86400.0)
    else:
        return (d2 - d1).total_seconds() / (365.0 * 86400.0)
