from __future__ import annotations

from typing import Optional, Tuple
from django.http import HttpRequest


def get_api_key(request: HttpRequest) -> Optional[str]:
    """
    Extract API key from headers. Supports both modern and WSGI META variants.
    """
    return request.headers.get("X-Account-Key") or request.META.get("HTTP_X_ACCOUNT_KEY")


def resolve_account_by_key(api_key: str) -> Tuple[object | None, str | None]:
    """
    Attempt to resolve an Account by API key.

    Returns:
      (account, None)                  if DB is available and key is valid
      (None, "invalid_api_key")        if DB is available but key is unknown
      (None, "db_unavailable:*")       if DB exists but not migrated/ready
      (None, "models_unavailable:*")   if models cannot be imported in this env
    """
    try:
        from django.db import OperationalError, ProgrammingError  # type: ignore
        from apps.accounts.models.account import Account  # type: ignore
        try:
            acct = Account.objects.filter(api_key=api_key).first()
            if acct:
                return acct, None
            return None, "invalid_api_key"
        except (OperationalError, ProgrammingError) as db_err:
            return None, f"db_unavailable:{db_err.__class__.__name__}"
    except Exception as e:
        # Models not importable in this environment (e.g., local smoke without apps wired)
        return None, f"models_unavailable:{e.__class__.__name__}"


def get_account_from_request(request: HttpRequest) -> Tuple[object | None, str | None]:
    """
    Full auth helper:
      - Missing key → (None, "auth_required")
      - Otherwise → resolve_account_by_key(key)
    Never raises; safe for DB-free smoke tests.
    """
    key = get_api_key(request)
    if not key:
        return None, "auth_required"
    return resolve_account_by_key(key)
