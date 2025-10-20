from __future__ import annotations
from django.db import models
from apps.core.constants.channels import EMAIL, SMS
from apps.core.constants.statuses import MSG_QUEUED, MSG_SENT, MSG_FAILED

CHANNEL_CHOICES = [
    (EMAIL, "Email"),
    (SMS, "SMS"),
]

DIRECTION_OUT = "out"
DIRECTION_IN  = "in"
DIRECTION_CHOICES = [
    (DIRECTION_OUT, "Outbound"),
    (DIRECTION_IN,  "Inbound"),
]

STATUS_CHOICES = [
    (MSG_QUEUED, "Queued"),
    (MSG_SENT,   "Sent"),
    (MSG_FAILED, "Failed"),
]

class Message(models.Model):
    """
    A single message unit (email or SMS), inbound or outbound.
    Links to Account and optionally to a Contact and Lead.
    """
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="messages")
    contact = models.ForeignKey("contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")
    lead    = models.ForeignKey("leads.Lead", on_delete=models.SET_NULL, null=True, blank=True, related_name="messages")

    channel   = models.CharField(max_length=8, choices=CHANNEL_CHOICES)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES, default=DIRECTION_OUT)

    # Email-specific
    subject = models.CharField(max_length=240, blank=True, null=True)
    body    = models.TextField(blank=True, null=True)

    # SMS-specific can also use 'body'

    # Provider plumbing
    provider = models.CharField(max_length=32, blank=True, null=True)  # "sendgrid" | "twilio"
    provider_message_id = models.CharField(max_length=120, blank=True, null=True)

    # Delivery state
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=MSG_QUEUED)
    error  = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "messaging"
        indexes = [
            models.Index(fields=["account", "channel"]),
            models.Index(fields=["account", "status"]),
            models.Index(fields=["account", "direction"]),
            models.Index(fields=["provider", "provider_message_id"]),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self) -> str:  # pragma: no cover
        who = getattr(self.contact, "email", None) or getattr(self.contact, "phone", None) or "unknown"
        return f"[{self.channel}/{self.direction}] {who} -> {self.status}"
