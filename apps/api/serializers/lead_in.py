from typing import Any, Dict
from rest_framework import serializers
from .contact_in import ContactInSerializer


class LeadInSerializer(serializers.Serializer):
    """
    Minimal inbound lead serializer for /ingest/.
    Fields:
      - source: short string like 'web_form', 'abandoned_cart', 'manual' (required)
      - contact: nested ContactInSerializer (required; must include a valid email)
      - metadata: arbitrary JSON/dict (optional)
    """
    source = serializers.CharField(required=True, allow_blank=False, max_length=64)
    contact = ContactInSerializer(required=True)
    metadata = serializers.JSONField(required=False, allow_null=True)

    def validate_source(self, v: str) -> str:
        v = v.strip()
        if not v:
            raise serializers.ValidationError("source is required")
        return v

    def validate_metadata(self, v: Any) -> Dict[str, Any]:
        # Normalize None to {} for convenience downstream
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise serializers.ValidationError("metadata must be an object/dict")
        return v
