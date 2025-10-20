from __future__ import annotations
from django.db import models
from django.db.models import Q

class Contact(models.Model):
    """
    A person we can message for a given Account.
    Email and/or phone may be present. Consent + unsubscribe tracked.
    """
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE, related_name="contacts")

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    name = models.CharField(max_length=120, blank=True, null=True)

    consent = models.BooleanField(default=True)       # captured consent to contact
    unsubscribed = models.BooleanField(default=False) # one-click unsubscribe flag

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "contacts"
        indexes = [
            models.Index(fields=["account", "email"]),
            models.Index(fields=["account", "phone"]),
        ]
        constraints = [
            # Unique email per account when email is not null
            models.UniqueConstraint(
                fields=["account", "email"],
                condition=Q(email__isnull=False),
                name="uniq_contact_email_per_account",
            ),
            # Unique phone per account when phone is not null
            models.UniqueConstraint(
                fields=["account", "phone"],
                condition=Q(phone__isnull=False),
                name="uniq_contact_phone_per_account",
            ),
        ]
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self) -> str:  # pragma: no cover
        ident = self.email or self.phone or "unknown"
        return f"{self.name or ''} <{ident}>".strip()
