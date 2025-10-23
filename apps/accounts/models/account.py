from django.db import models


class Account(models.Model):
    """
    Represents a tenant/account that owns an API key used to authenticate
    inbound requests to Reclaimr endpoints.
    """
    api_key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    sender_email = models.EmailField(max_length=254)

    # Bookkeeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.api_key})"
