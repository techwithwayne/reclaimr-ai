from __future__ import annotations
import os
from django.views.decorators.http import require_GET
from apps.core.http.responses import ok

@require_GET
def health(request):
    """
    Lightweight health endpoint. No DB, no cache: always fast.
    """
    return ok({
        "status": "ok",
        "service": "reclaimr",
        "version": os.getenv("RECLAIMR_VERSION", "0.1.0"),
        "env": os.getenv("ENV", "local"),
    })

__all__ = ["health"]
