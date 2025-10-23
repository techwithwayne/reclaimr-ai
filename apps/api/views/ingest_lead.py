from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError, ProgrammingError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.services.api_key_auth import authenticate
from apps.api.serializers.lead_in import LeadInSerializer


@api_view(["POST"])
def ingest(request):
    """
    Auth-first lead ingestion endpoint.

    Flow:
      1) Authenticate via X-Account-Key (missing/invalid => 401; DB unavailable => 503).
      2) Validate payload via LeadInSerializer (400 on invalid).
      3) If DB available: upsert Contact, create Lead => 201.
         If DB unavailable: return 202 Accepted (validated, but not persisted).
    """
    # 1) Auth-first
    auth = authenticate(request)
    if not auth.ok:
        if auth.reason == "missing_key":
            return Response({"detail": "missing_key"}, status=status.HTTP_401_UNAUTHORIZED)
        if auth.reason == "invalid_key":
            return Response({"detail": "invalid_key"}, status=status.HTTP_401_UNAUTHORIZED)
        # DB not ready / imports failed
        return Response({"detail": "db_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    account = auth.account

    # 2) Validate inbound payload
    serializer = LeadInSerializer(data=request.data)
    if not serializer.is_valid():
        # NOTE: Even if body is invalid, auth-first must have already passed above.
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    source = data["source"]
    contact_in = data["contact"]
    metadata = data.get("metadata") or {}

    # 3) Persist when DB is available; otherwise degrade gracefully
    try:
        from apps.contacts.models.contact import Contact
        from apps.leads.models.lead import Lead

        # Upsert contact (natural key on email)
        defaults = {
            "name": contact_in.get("name", ""),
            "phone": contact_in.get("phone", ""),
            "account": account,
        }
        contact, _ = Contact.objects.update_or_create(
            email=contact_in["email"], defaults=defaults
        )

        lead = Lead.objects.create(
            account=account,
            contact=contact,
            source=source,
            status="new",
            metadata=metadata,
        )
        return Response(
            {"id": lead.pk, "status": "created", "source": source},
            status=status.HTTP_201_CREATED,
        )

    except (OperationalError, ProgrammingError, ImproperlyConfigured):
        # Database not migrated/ready locally; accept the payload but signal deferred persistence.
        return Response(
            {
                "status": "accepted",
                "reason": "db_unavailable_but_validated",
                "source": source,
            },
            status=status.HTTP_202_ACCEPTED,
        )
