from __future__ import annotations
from django.db import models

class Account(models.Model):
    """
    Tenant/account for Reclaimr.
    - api_key: per-tenant key used by script/widget and server-to-server calls
    - sender_*: default outbound identity (email + display name)
    - timezone: default TZ for scheduling
    """
    name = models.CharField(max_length=120)
    api_key = models.CharField(max_length=64, unique=True, db_index=True)

    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=120, default="Support")

    timezone = models.CharField(max_length=64, default="America/Chicago")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        indexes = [
            models.Index(fields=["api_key"]),
        ]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"
