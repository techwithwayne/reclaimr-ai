from typing import NamedTuple, Optional, Tuple
from django.db import OperationalError, ProgrammingError
from django.core.exceptions import ImproperlyConfigured
from rest_framework.request import Request

try:
    from apps.accounts.models.account import Account  # type: ignore
except Exception:
    # Import-time tolerance; actual DB lookup guarded below.
    Account = None  # type: ignore


HEADER_NAME = "HTTP_X_ACCOUNT_KEY"


class AuthResult(NamedTuple):
    ok: bool
    status: int
    reason: str
    account: Optional["Account"]


def _safe_get_account_by_key(api_key: str) -> Tuple[Optional["Account"], Optional[str]]:
    """
    DB-safe lookup that won't crash if migrations/tables aren't ready.
    Returns (Account|None, error_reason|None)
    """
    if Account is None:
        return None, "import_failed"

    try:
        return Account.objects.get(api_key=api_key), None
    except (OperationalError, ProgrammingError, ImproperlyConfigured):
        # DB not ready / table missing locally. Treat as service unavailable, not 500.
        return None, "db_unavailable"
    except Account.DoesNotExist:  # type: ignore[attr-defined]
        return None, "invalid_key"


def authenticate(request: Request) -> AuthResult:
    """
    Auth via 'X-Account-Key' header.
    - Missing header -> 401 / missing_key
    - DB unavailable (no tables) -> 503 / db_unavailable
    - Invalid key -> 401 / invalid_key
    - Valid key -> 200 / ok
    """
    api_key = request.META.get(HEADER_NAME)  # 'HTTP_X_ACCOUNT_KEY'
    if not api_key:
        return AuthResult(False, 401, "missing_key", None)

    account, err = _safe_get_account_by_key(api_key)
    if err == "db_unavailable" or err == "import_failed":
        return AuthResult(False, 503, "db_unavailable", None)
    if account is None:
        return AuthResult(False, 401, "invalid_key", None)
    return AuthResult(True, 200, "ok", account)
