from typing import Any, Mapping
from django.http import JsonResponse

JSONDict = Mapping[str, Any]

def _json_response(data: Any, status: int = 200) -> JsonResponse:
    """
    Return a JsonResponse with correct 'safe' flag based on payload type.
    - dict => safe=True
    - non-dict (list/str/number) => safe=False
    """
    is_dict = isinstance(data, dict)
    return JsonResponse(data, status=status, safe=is_dict, json_dumps_params={"ensure_ascii": False})

# --- Success helpers ---
def ok(data: Any | None = None) -> JsonResponse:
    return _json_response({} if data is None else data, status=200)

def created(data: Any | None = None) -> JsonResponse:
    return _json_response({} if data is None else data, status=201)

# --- Error helpers (standardized error envelope) ---
def _err(code: str, message: str, status: int) -> JsonResponse:
    payload: JSONDict = {"error": {"code": code, "message": message}}
    return _json_response(payload, status=status)

def bad_request(message: str = "Bad request") -> JsonResponse:
    return _err("bad_request", message, 400)

def unauthorized(message: str = "Unauthorized") -> JsonResponse:
    return _err("unauthorized", message, 401)

def forbidden(message: str = "Forbidden") -> JsonResponse:
    return _err("forbidden", message, 403)

def not_found(message: str = "Not found") -> JsonResponse:
    return _err("not_found", message, 404)

def server_error(message: str = "Server error") -> JsonResponse:
    return _err("server_error", message, 500)

__all__ = [
    "ok", "created",
    "bad_request", "unauthorized", "forbidden", "not_found", "server_error",
]
