from __future__ import annotations

from typing import Any, Mapping, Optional
from django.http import JsonResponse


def _json(data: Mapping[str, Any] | None, status: int) -> JsonResponse:
    return JsonResponse(data or {}, status=status, safe=False)

# 2xx
def ok(data: Optional[Mapping[str, Any]] = None) -> JsonResponse:
    return _json(data or {"status": "ok"}, 200)

def created(data: Optional[Mapping[str, Any]] = None) -> JsonResponse:
    return _json(data or {"status": "created"}, 201)

def accepted(data: Optional[Mapping[str, Any]] = None) -> JsonResponse:
    return _json(data or {"status": "accepted"}, 202)

# 4xx
def bad_request(errors: Optional[Mapping[str, Any]] = None) -> JsonResponse:
    payload = {"status": "invalid"}
    if errors:
        payload.update(errors)
    return _json(payload, 400)

def unauthorized(detail: str = "auth_required") -> JsonResponse:
    return _json({"detail": detail}, 401)

def forbidden(detail: str = "forbidden") -> JsonResponse:
    return _json({"detail": detail}, 403)

def not_found(detail: str = "not_found") -> JsonResponse:
    return _json({"detail": detail}, 404)

__all__ = [
    "ok",
    "created",
    "accepted",
    "bad_request",
    "unauthorized",
    "forbidden",
    "not_found",
]
