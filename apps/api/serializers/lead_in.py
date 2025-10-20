from __future__ import annotations
from typing import Any, Dict
import re
from rest_framework import serializers
from .contact_in import ContactIn

_SAFE_SOURCE = re.compile(r"^[a-z0-9_\-:]{2,64}$")

class LeadIn(serializers.Serializer):
    source  = serializers.CharField(max_length=64)
    context = serializers.DictField(child=serializers.JSONField(), required=False, default=dict)
    contact = ContactIn()

    def validate_source(self, v: str) -> str:
        v = (v or "").strip().lower()
        if not _SAFE_SOURCE.match(v):
            raise serializers.ValidationError(
                "Invalid source. Use 2-64 chars: lowercase letters, digits, '_', '-', ':'."
            )
        return v

    def validate_context(self, v: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure dict (DRF already enforces DictField). Could trim huge payloads here if needed.
        return v or {}

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # All heavy lifting is per-field and nested ContactIn.
        return attrs
