from __future__ import annotations
from typing import Any, Dict
import re
from rest_framework import serializers

_PHONE_RE = re.compile(r"^[0-9+\-\s().]{6,32}$")

class ContactIn(serializers.Serializer):
    name  = serializers.CharField(required=False, allow_blank=True, max_length=120)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        name = (attrs.get("name") or "").strip()
        email = (attrs.get("email") or "").strip().lower()
        phone = (attrs.get("phone") or "").strip()

        # Require at least one of email or phone
        if not email and not phone:
            raise serializers.ValidationError("Provide at least one of: email or phone.")

        # Basic phone format (if provided)
        if phone and not _PHONE_RE.match(phone):
            raise serializers.ValidationError("Invalid phone format.")

        attrs["name"] = name
        attrs["email"] = email or None
        attrs["phone"] = phone or None
        return attrs
