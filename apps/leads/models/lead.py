from django.db import models


class Lead(models.Model):
    """
    Represents an inbound lead captured by Reclaimr.
    Links to a Contact and (optionally) an Account for multi-tenant use.
    """
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="leads",
        null=True,
        blank=True,
    )
    contact = models.ForeignKey(
        "contacts.Contact",
        on_delete=models.CASCADE,
        related_name="leads",
    )

    # Where did this lead originate? e.g., "web_form", "abandoned_cart", "manual"
    source = models.CharField(max_length=64, db_index=True)

    # Simple lifecycle; extend later (e.g., "new", "messaged", "replied", "converted")
    status = models.CharField(max_length=32, default="new", db_index=True)

    # Flexible blob for extra attributes (UTM params, cart items, custom fields)
    metadata = models.JSONField(blank=True, null=True, default=dict)

    # Bookkeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"Lead<{self.pk}>:{self.source}:{self.status}"
