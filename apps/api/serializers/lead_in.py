from __future__ import annotations

from typing import Any, Dict
from rest_framework import serializers

from .contact_in import ContactIn


class LeadIn(serializers.Serializer):
    """
    Minimal Lead input:
      {
        "source": "web_form",          # required, non-empty, <= 50 chars
        "contact": { ...ContactIn }    # required
      }
    """
    source = serializers.CharField(required=True, allow_blank=False, max_length=50)
    contact = ContactIn(required=True)

    def to_internal_value(self, data: Dict[str, Any]):
        # Let DRF handle base coercion first
        ret = super().to_internal_value(data)
        # Normalize source (strip)
        ret["source"] = ret["source"].strip()
        return ret
