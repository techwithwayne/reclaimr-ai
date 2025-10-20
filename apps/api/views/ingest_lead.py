from __future__ import annotations
import json
from typing import Any, Dict, Optional
from django.views.decorators.http import require_POST
from django.http import HttpRequest
from apps.core.http.responses import ok, created, bad_request, unauthorized, server_error
from apps.accounts.services.api_key_auth import require_account, InvalidApiKey
from apps.api.serializers.lead_in import LeadIn

# Optional imports for production upsert (no-ops in sanity since DB may be absent)
try:
    from apps.contacts.models.contact import Contact
    from apps.leads.models.lead import Lead
except Exception:  # pragma: no cover
    Contact = None  # type: ignore
    Lead = None     # type: ignore

def _json_body(request: HttpRequest) -> Dict[str, Any]:
    """
    Load JSON body safely. Returns {} on empty body.
    """
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        raise ValueError("Invalid JSON")

def _upsert_contact(account, contact_data) -> Optional[Any]:
    """
    Upsert Contact by email or phone for the given account.
    Returns Contact instance (or None if models unavailable).
    """
    if Contact is None:
        return None
    email = contact_data.get("email")
    phone = contact_data.get("phone")
    q = {"account": account}
    if email:
        q["email"] = email
    elif phone:
        q["phone"] = phone

    obj, _ = Contact.objects.get_or_create(**q, defaults={
        "name": contact_data.get("name") or "",
        "consent": True,
        "unsubscribed": False,
    })
    # Update name if provided
    name = contact_data.get("name")
    if name is not None and name != obj.name:
        obj.name = name
        obj.save(update_fields=["name"])
    return obj

@require_POST
def ingest_lead(request: HttpRequest):
    """
    Ingest a lead:
    - Auth via X-Account-Key
    - Validate payload with LeadIn
    - Upsert Contact, create Lead (in production where DB is ready)
    """
    # 1) Auth
    try:
        account = require_account(request)
    except InvalidApiKey:
        return unauthorized("API key missing/invalid")

    # 2) Payload
    try:
        payload = _json_body(request)
    except ValueError as e:
        return bad_request(str(e))

    s = LeadIn(data=payload)
    if not s.is_valid():
        return bad_request(str(s.errors))

    data = s.validated_data

    # 3) Persist (if models available)
    try:
        contact = _upsert_contact(account, data["contact"])
        if Lead is None:
            # DB not ready in dev sanity runs
            return created({"status": "accepted", "db": "not_ready"})
        lead = Lead.objects.create(
            account=account,
            contact=contact,
            source=data["source"],
            context=data.get("context", {}),
            status="open",
        )
        return created({"id": lead.id, "status": "created"})
    except Exception as e:
        # Don’t leak internals
        return server_error("Failed to ingest lead")
