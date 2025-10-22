from __future__ import annotations

import json
from typing import Any, Dict, Optional

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods

# Centralized, DB-tolerant auth helper
from apps.accounts.services.api_key_auth import (
    get_api_key,
    resolve_account_by_key,
)


def _safe_json(request: HttpRequest) -> Dict[str, Any]:
    """Parse JSON body safely. Returns {} on any failure."""
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
    api_key: Optional[str] = get_api_key(request)

    # ---- AUTH FIRST: reject immediately if no key provided ----
    if not api_key:
        return JsonResponse({"detail": "auth_required"}, status=401)

    # Resolve account (tolerant to DB/model availability)
    account, err = resolve_account_by_key(api_key)

    if err is None and account is None:
        # DB available but key not found
        return JsonResponse({"detail": "invalid_api_key"}, status=401)

    # Parse JSON only after auth step
    payload = _safe_json(request)
    source = payload.get("source")
    contact = payload.get("contact") or {}
    email = (contact.get("email") or "").strip()
    name = (contact.get("name") or "").strip()

    # Local DB-free path or models not ready: accept without persistence
    if account is None and err is not None:
        return JsonResponse(
            {
                "status": "accepted",
                "note": err,
                "echo": {"source": source, "contact_email": email},
            },
            status=202,
        )

    # Persistence path when models/DB are available
    try:
        from apps.contacts.models.contact import Contact  # type: ignore
        from apps.leads.models.lead import Lead  # type: ignore

        contact_obj, created = Contact.objects.get_or_create(
            account=account,
            defaults={"email": email, "name": name},
        )

        # Update email/name if provided and changed
        updates = {}
        if email and contact_obj.email != email:
            updates["email"] = email
        if name and getattr(contact_obj, "name", "") != name:
            updates["name"] = name
        if updates:
            for k, v in updates.items():
                setattr(contact_obj, k, v)
            contact_obj.save(update_fields=list(updates.keys()))

        lead = Lead.objects.create(
            account=account,
            contact=contact_obj,
            source=(source or "unknown"),
            status="new",
        )
        return JsonResponse(
            {
                "status": "created",
                "lead_id": getattr(lead, "id", None),
                "contact_email": email,
            },
            status=201,
        )
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
