from __future__ import annotations
from django.db import models
from django.db.models import Q
from .account import Account

class SenderProfile(models.Model):
    """
    Optional per-account sender identity overrides.
    Useful when a tenant has multiple brands or departments.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sender_profiles")

    label = models.CharField(max_length=120)  # e.g., "Main", "Support", "Sales - EU"
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=120, default="Support")
    reply_to = models.EmailField(blank=True, null=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        constraints = [
            # Only one default sender per account (Postgres required for partial unique)
            models.UniqueConstraint(
                fields=["account"],
                condition=Q(is_default=True),
                name="unique_default_sender_per_account",
            ),
        ]
        indexes = [
            models.Index(fields=["account", "label"]),
        ]
        verbose_name = "Sender Profile"
        verbose_name_plural = "Sender Profiles"

    def __str__(self) -> str:  # pragma: no cover
        tag = " (default)" if self.is_default else ""
        return f"{self.label}{tag} <{self.sender_email}>"
