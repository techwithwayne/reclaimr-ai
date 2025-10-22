from __future__ import annotations

from rest_framework import serializers


class ContactIn(serializers.Serializer):
    """
    Minimal contact input:
      {
        "email": "user@example.com",   # required, valid email
        "name": "User Name"            # optional, max 200 chars
      }
    """
    email = serializers.EmailField(required=True, allow_blank=False)
    name = serializers.CharField(required=False, allow_blank=True, max_length=200)

    def validate_name(self, value: str) -> str:
        # Normalize whitespace; keep empty allowed
        return value.strip() if isinstance(value, str) else value
