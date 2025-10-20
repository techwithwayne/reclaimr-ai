from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
import os

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

def now_utc() -> datetime:
    """
    Return current UTC time (timezone-aware).
    """
    return datetime.now(timezone.utc)

def _safe_zoneinfo(name: str):
    """
    Best-effort to return a ZoneInfo; fallback to UTC on failure or if ZoneInfo is unavailable.
    """
    if not name:
        return timezone.utc
    if ZoneInfo is None:
        return timezone.utc
    try:
        return ZoneInfo(name)
    except Exception:
        return timezone.utc

def now_local(tz_name: Optional[str] = None) -> datetime:
    """
    Return current time in the given time zone (timezone-aware).
    Priority: explicit tz_name → env TIMEZONE → UTC.
    """
    tz_env = os.getenv("TIMEZONE", "")
    zone = _safe_zoneinfo(tz_name or tz_env)
    return datetime.now(zone)

__all__ = ["now_utc", "now_local"]
