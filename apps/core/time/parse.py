from __future__ import annotations
from datetime import timedelta
import re

# Matches things like +1d2h30m45s or +15m, +2h, +3d, +90s
_PATTERN = re.compile(r"^\+(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?$")

def parse_offset(spec: str) -> timedelta:
    """
    Parse a simple relative offset string into a timedelta.
    Supported units: d (days), h (hours), m (minutes), s (seconds)
    Format: '+<Nd><Nh><Nm><Ns>' where any piece is optional but at least one must be present.
    Examples:
      '+2h' -> 2 hours
      '+15m' -> 15 minutes
      '+1d2h30m' -> 1 day, 2 hours, 30 minutes
      '+90s' -> 90 seconds
    Raises:
      ValueError on invalid format or zero duration.
    """
    if not isinstance(spec, str):
        raise ValueError("Offset must be a string like '+2h' or '+15m'.")

    m = _PATTERN.match(spec.strip())
    if not m:
        raise ValueError(f"Invalid offset format: {spec!r}")

    days = int(m.group("days") or 0)
    hours = int(m.group("hours") or 0)
    minutes = int(m.group("minutes") or 0)
    seconds = int(m.group("seconds") or 0)

    td = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if td.total_seconds() <= 0:
        raise ValueError("Offset must be greater than zero.")
    return td

__all__ = ["parse_offset"]
