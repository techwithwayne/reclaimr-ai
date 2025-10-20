from __future__ import annotations
from django.db import models
from apps.core.constants.statuses import (
    LEAD_OPEN, LEAD_REPLY, LEAD_WON, LEAD_LOST, LEAD_PAUSED,
)

LEAD_STATUS_CHOICES = [
    (LEAD_OPEN, "Open"),
    (LEAD_REPLY, "Replied"),
    (LEAD_WON, "Won"),
    (LEAD_LOST, "Lost"),
    (LEAD_PAUSED, "Paused"),
]

class Lead(models.Model):
    """
    Marketing/sales lead tied to an Account and a Contact.
    - source: origin, e.g., 'web_form', 'shopify_abandoned'
    - context: JSON payload with arbitrary details (cart items, page url, etc.)
    - status: lifecycle state
    - last_event_at: updates on meaningful changes (auto_now on save for simplicity)
    """
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="leads")
    contact = models.ForeignKey("contacts.Contact", on_delete=models.CASCADE, related_name="leads")

    source = models.CharField(max_length=64)      # 'shopify_abandoned', 'web_form', etc.
    context = models.JSONField(default=dict)      # arbitrary metadata

    status = models.CharField(max_length=16, choices=LEAD_STATUS_CHOICES, default=LEAD_OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_event_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "leads"
        indexes = [
            models.Index(fields=["account", "status"]),
            models.Index(fields=["account", "source"]),
        ]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self) -> str:  # pragma: no cover
        ident = (getattr(self.contact, "email", None) or getattr(self.contact, "phone", None) or "unknown")
        return f"[{self.source}] {ident} - {self.status}"
