from django.db import models


class Contact(models.Model):
    """
    Represents a person we may message as part of Reclaimr outreach.
    Email acts as a natural key to avoid duplicates.
    """
    # Optional owner link for multi-tenant scenarios (can be null for MVP)
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="contacts",
        null=True,
        blank=True,
    )

    email = models.EmailField(max_length=254, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="")

    # Bookkeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "contacts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return self.email
