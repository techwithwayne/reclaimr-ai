"""
Standard HTTP header names used across the project.
Keeping these in one place avoids typos and makes changes safe.
"""

# Tenant / auth
ACCOUNT_KEY = "X-Account-Key"          # per-account API key header

# Webhooks — Shopify
SHOPIFY_HMAC = "X-Shopify-Hmac-SHA256" # HMAC signature header
SHOPIFY_SHOP_DOMAIN = "X-Shopify-Shop-Domain"

# Webhooks — Twilio
TWILIO_SIGNATURE = "X-Twilio-Signature"

# Observability
REQUEST_ID = "X-Request-ID"            # for correlation across services

# Generics
CONTENT_TYPE = "Content-Type"

__all__ = [
    "ACCOUNT_KEY",
    "SHOPIFY_HMAC",
    "SHOPIFY_SHOP_DOMAIN",
    "TWILIO_SIGNATURE",
    "REQUEST_ID",
    "CONTENT_TYPE",
]
