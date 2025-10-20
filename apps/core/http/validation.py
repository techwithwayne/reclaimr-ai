from typing import Iterable, Mapping, Any

class ValidationError(Exception):
    """Lightweight validation error for request bodies."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

def require_fields(obj: Mapping[str, Any], fields: Iterable[str]) -> None:
    """
    Ensure all required top-level fields exist (non-empty).
    Raises ValidationError on first missing field.
    """
    for f in fields:
        if f not in obj or obj[f] in (None, "", []):
            raise ValidationError(f"Missing or empty field: {f}")

def ensure_type(value: Any, expected_type: type, field_name: str) -> None:
    """
    Ensure a value is of expected type.
    """
    if not isinstance(value, expected_type):
        raise ValidationError(f"Field '{field_name}' must be {expected_type.__name__}")
