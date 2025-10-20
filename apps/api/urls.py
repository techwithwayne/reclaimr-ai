from django.urls import path
from .views.health import health

urlpatterns = [
    path("health/", health, name="reclaimr-health"),
    # Next: path("ingest/", ingest_lead, name="reclaimr-ingest"),
]
