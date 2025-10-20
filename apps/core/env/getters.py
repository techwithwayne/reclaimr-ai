from typing import List, Optional
import os

def get_str(key: str, default: str = "") -> str:
    """
    Return env var as string, or default if unset.
    """
    v = os.getenv(key)
    return v if v is not None else default

def get_bool(key: str, default: bool = False) -> bool:
    """
    Convert common truthy strings to bool:
    1/true/yes/y/on => True (case-insensitive). Otherwise False.
    """
    v = os.getenv(key)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}

def get_csv(key: str, default_csv: str = "") -> List[str]:
    """
    Split a comma-separated env var into a trimmed list.
    Empty or missing entries are discarded.
    """
    raw = os.getenv(key, default_csv)
    return [x.strip() for x in raw.split(",") if x.strip()]
