"""
Idempotent .env loader.
- Safe to call multiple times.
- Looks for .env at repo root (two levels above this file).
"""

from pathlib import Path
from typing import Optional
import os

try:
    # python-dotenv is in requirements
    from dotenv import load_dotenv
except Exception:  # pragma: no cover (import guard)
    load_dotenv = None  # type: ignore

# Resolve repo root: .../reclaimr-ai/.env
_REPO_ROOT = Path(__file__).resolve().parents[3]

def _env_loaded_marker() -> str:
    """Internal: env loaded marker variable name."""
    return "RECLAIMR_ENV_LOADED"

def init_env(dotenv_path: Optional[Path] = None) -> bool:
    """
    Load .env once. Returns True if we performed a load in this call, False if already loaded or unavailable.
    """
    # If already marked, skip
    if os.getenv(_env_loaded_marker()) == "1":
        return False

    # If dotenv module missing, just mark and continue (project may load env elsewhere)
    if load_dotenv is None:
        os.environ[_env_loaded_marker()] = "1"
        return False

    # Use provided path or default to repo-root .env
    path = dotenv_path or (_REPO_ROOT / ".env")

    # load_dotenv returns True if at least one value is set, False otherwise
    load_dotenv(dotenv_path=path, override=False)

    # Mark as loaded to avoid duplicate work
    os.environ[_env_loaded_marker()] = "1"
    return True
