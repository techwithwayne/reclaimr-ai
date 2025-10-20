from __future__ import annotations
from typing import Optional
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, OperationalError, ProgrammingError
from django.conf import settings

from apps.core.constants.headers import ACCOUNT_KEY as HDR_ACCOUNT_KEY
from apps.accounts.models.account import Account

class InvalidApiKey(PermissionDenied):
    """Raised when API key is missing or invalid."""
    pass

def _db_is_ready() -> bool:
    """
    True if a real DB engine is configured (not dummy, not missing).
    """
    try:
        db = settings.DATABASES.get("default", {})
        engine = db.get("ENGINE", "")
        return bool(engine) and engine != "django.db.backends.dummy"
    except Exception:
        return False

def get_api_key_from_headers(request: HttpRequest) -> Optional[str]:
    """
    Extract API key from request header.
    Handles both request.headers[...] and WSGI META fallback.
    """
    key = None
    if getattr(request, "headers", None):
        key = request.headers.get(HDR_ACCOUNT_KEY)
    if not key and getattr(request, "META", None):
        meta_key = f"HTTP_{HDR_ACCOUNT_KEY.replace('-', '_').upper()}"
        key = request.META.get(meta_key)
    return key.strip() if key else None

def get_account_by_key(api_key: str) -> Optional[Account]:
    """
    Return active Account by api_key, or None if not found/inactive.
    Returns None if the DB is not ready (e.g., before migrations or no ENGINE).
    """
    if not _db_is_ready():
        return None
    try:
        acc = Account.objects.get(api_key=api_key)
        if not acc.is_active:
            return None
        return acc
    except Account.DoesNotExist:
        return None
    except (DatabaseError, OperationalError, ProgrammingError):
        # Missing tables or DB not ready during early dev or tests
        return None

def require_account(request: HttpRequest) -> Account:
    """
    Resolve and return the Account or raise InvalidApiKey.
    """
    api_key = get_api_key_from_headers(request)
    if not api_key:
        raise InvalidApiKey("Missing API key header")
    acc = get_account_by_key(api_key)
    if not acc:
        raise InvalidApiKey("Invalid or inactive API key")
    return acc
