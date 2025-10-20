"""
Canonical status constants for leads and messages.
Keeping these centralized avoids drift across services and tasks.
"""

# Lead lifecycle
LEAD_OPEN   = "open"     # new lead, sequence active
LEAD_REPLY  = "reply"    # customer replied; pause/stop sequence
LEAD_WON    = "won"      # converted (e.g., order placed)
LEAD_LOST   = "lost"     # closed without conversion
LEAD_PAUSED = "paused"   # temporarily halted (manual or rule)

# Message lifecycle
MSG_QUEUED = "queued"    # created but not sent yet
MSG_SENT   = "sent"      # successfully sent
MSG_FAILED = "failed"    # provider error or validation failure

__all__ = [
    # Lead
    "LEAD_OPEN", "LEAD_REPLY", "LEAD_WON", "LEAD_LOST", "LEAD_PAUSED",
    # Message
    "MSG_QUEUED", "MSG_SENT", "MSG_FAILED",
]
