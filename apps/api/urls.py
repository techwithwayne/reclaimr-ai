from django.urls import path

# Always-available health view (DB-free)
from apps.api.views.health import health

urlpatterns = [
    path("health/", health, name="health"),
]

# Optional: ingest endpoint (auth-first). Added only if import succeeds.
try:
    from apps.api.views.ingest_lead import ingest  # type: ignore
except Exception:
    ingest = None

if ingest:
    urlpatterns.append(path("ingest/", ingest, name="ingest"))
