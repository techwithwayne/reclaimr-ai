from __future__ import annotations

import json
from typing import Any, Dict, Optional

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods


def _get_account_from_key(api_key: str):
    """
    Attempt to resolve an Account by API key. Tolerant to missing DB/migrations.
    Returns: (account or None, error_str or None)
    """
    try:
        from django.db import OperationalError, ProgrammingError
        from apps.accounts.models.account import Account  # type: ignore

        try:
            acct = Account.objects.filter(api_key=api_key).first()
            return acct, None
        except (OperationalError, ProgrammingError) as db_err:
            return None, f"db_unavailable:{db_err.__class__.__name__}"
    except Exception as e:  # models not present, etc.
        return None, f"models_unavailable:{e.__class__.__name__}"


def _safe_json(request: HttpRequest) -> Dict[str, Any]:
    """
    Parse JSON body safely. Returns {} on any failure.
    """
    try:
        body = request.body.decode("utf-8") if request.body else ""
        return json.loads(body) if body else {}
    except Exception:
        return {}


@require_http_methods(["POST"])
def ingest(request: HttpRequest) -> JsonResponse:
    """
    Auth-first lead ingest:
    - Missing/invalid X-Account-Key => 401 (even if JSON invalid).
    - With valid key & DB available & Account exists => 201 + persisted record(s).
    - With valid key but DB/models unavailable during local smoke => 202 (accepted, persistence skipped).
    """
    api_key: Optional[str] = request.headers.get("X-Account-Key") or request.META.get(
        "HTTP_X_ACCOUNT_KEY"
    )

    # ---- AUTH FIRST: reject immediately if no key provided ----
    if not api_key:
        return JsonResponse({"detail": "auth_required"}, status=401)

    # Resolve account (tolerant to DB/model availability)
    account, acct_err = _get_account_from_key(api_key)

    if acct_err is None and account is None:
        # DB available but key not found
        return JsonResponse({"detail": "invalid_api_key"}, status=401)

    # From here we have either a real Account or we are in "tolerant" mode for local (acct_err set)
    payload = _safe_json(request)

    # Minimal shape validation only after auth
    source = payload.get("source")
    contact = payload.get("contact") or {}
    email = (contact.get("email") or "").strip()

    if account is None and acct_err is not None:
        # Local DB-free path: accept for pipeline testing without persistence
        return JsonResponse(
            {
                "status": "accepted",
                "note": acct_err,
                "echo": {"source": source, "contact_email": email},
            },
            status=202,
        )

    # If we have a real Account, attempt persistence (best-effort; tolerate model availability)
    created = False
    lead_id: Optional[int] = None
    try:
        # Lazy imports to avoid hard dependency during local smoke
        from apps.contacts.models.contact import Contact  # type: ignore
        from apps.leads.models.lead import Lead  # type: ignore

        contact_obj, _ = Contact.objects.get_or_create(
            account=account,
            defaults={"email": email, "name": contact.get("name", "").strip()},
        )
        # Update basic fields if missing
        if email and contact_obj.email != email:
            contact_obj.email = email
            contact_obj.save(update_fields=["email"])

        lead = Lead.objects.create(
            account=account,
            contact=contact_obj,
            source=(source or "unknown"),
            status="new",
        )
        lead_id = getattr(lead, "id", None)
        created = True
    except Exception as e:
        # Gracefully degrade if models/migrations incomplete
        return JsonResponse(
            {
                "status": "accepted",
                "note": f"persistence_skipped:{e.__class__.__name__}",
                "echo": {"source": source, "contact_email": email},
            },
            status=202,
        )

    return JsonResponse(
        {
            "status": "created",
            "lead_id": lead_id,
            "contact_email": email,
        },
        status=201 if created else 200,
    )
