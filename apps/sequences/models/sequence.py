from __future__ import annotations
from django.db import models

class Sequence(models.Model):
    """
    A cadence definition for an Account.
    Each step is a dict: {"t": "+2h", "channel": "email", "template": "revive1"}
    """
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="sequences")
    name = models.CharField(max_length=120, default="Default Revival")
    steps = models.JSONField(default=list)  # e.g., [{"t":"+2h","channel":"email","template":"revive1"}]
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "sequences"
        indexes = [
            models.Index(fields=["account", "active"]),
            models.Index(fields=["account", "name"]),
        ]
        verbose_name = "Sequence"
        verbose_name_plural = "Sequences"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({'active' if self.active else 'inactive'})"
