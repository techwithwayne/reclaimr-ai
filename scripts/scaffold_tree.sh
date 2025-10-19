#!/usr/bin/env bash
set -euo pipefail

echo "[scaffold] starting in: $(pwd)"

# 1) Directories to ensure exist
DIRS=(
  config
  config/settings
  apps
  apps/core
  apps/core/constants
  apps/core/env
  apps/core/logging
  apps/core/time
  apps/core/crypto
  apps/core/http
  apps/core/rate_limit
  apps/core/tests
  apps/accounts
  apps/accounts/models
  apps/accounts/admin
  apps/accounts/repositories
  apps/accounts/services
  apps/accounts/tests
  apps/contacts
  apps/contacts/models
  apps/contacts/repositories
  apps/contacts/services
  apps/contacts/tests
  apps/leads
  apps/leads/models
  apps/leads/repositories
  apps/leads/services
  apps/leads/tests
  apps/sequences
  apps/sequences/models
  apps/sequences/repositories
  apps/sequences/services
  apps/sequences/scheduler
  apps/sequences/tests
  apps/messaging
  apps/messaging/models
  apps/messaging/providers
  apps/messaging/composer
  apps/messaging/tasks
  apps/messaging/services
  apps/messaging/tests
  apps/webhooks
  apps/webhooks/verify
  apps/webhooks/views
  apps/webhooks/tests
  apps/api
  apps/api/serializers
  apps/api/views
  apps/api/tests
  apps/widget
  apps/widget/static/widget
  apps/widget/views
  scripts
)

for d in "${DIRS[@]}"; do
  mkdir -p "$d"
done
echo "[scaffold] ensured directories"

# 2) Add __init__.py to python packages
PKG_DIRS=(
  config
  config/settings
  apps
  apps/core
  apps/core/constants
  apps/core/env
  apps/core/logging
  apps/core/time
  apps/core/crypto
  apps/core/http
  apps/core/rate_limit
  apps/accounts
  apps/accounts/models
  apps/accounts/admin
  apps/accounts/repositories
  apps/accounts/services
  apps/contacts
  apps/contacts/models
  apps/contacts/repositories
  apps/contacts/services
  apps/leads
  apps/leads/models
  apps/leads/repositories
  apps/leads/services
  apps/sequences
  apps/sequences/models
  apps/sequences/repositories
  apps/sequences/services
  apps/sequences/scheduler
  apps/messaging
  apps/messaging/models
  apps/messaging/providers
  apps/messaging/composer
  apps/messaging/tasks
  apps/messaging/services
  apps/webhooks
  apps/webhooks/verify
  apps/webhooks/views
  apps/api
  apps/api/serializers
  apps/api/views
  apps/widget
  apps/widget/views
)

for d in "${PKG_DIRS[@]}"; do
  if [ ! -f "$d/__init__.py" ]; then
    : > "$d/__init__.py"
    echo "[scaffold] created $d/__init__.py"
  fi
done

# 3) Files to create iff missing (never overwrite)
FILES=(
  config/urls.py
  config/settings/base.py
  config/settings/dev.py
  config/settings/prod.py
  config/settings/celery.py

  apps/core/constants/channels.py
  apps/core/constants/statuses.py
  apps/core/constants/headers.py
  apps/core/env/loader.py
  apps/core/env/getters.py
  apps/core/logging/json_logger.py
  apps/core/logging/request_id.py
  apps/core/time/now.py
  apps/core/time/parse.py
  apps/core/crypto/hmac_sha256.py
  apps/core/crypto/timing_safe_eq.py
  apps/core/http/responses.py
  apps/core/http/validation.py
  apps/core/rate_limit/limiter.py
  apps/core/rate_limit/keys.py

  apps/accounts/models/account.py
  apps/accounts/models/sender_profile.py
  apps/accounts/admin/account_admin.py
  apps/accounts/repositories/accounts_repo.py
  apps/accounts/repositories/senders_repo.py
  apps/accounts/services/api_key_auth.py

  apps/contacts/models/contact.py
  apps/contacts/repositories/contacts_repo.py
  apps/contacts/services/upsert_contact.py
  apps/contacts/services/unsubscribe_contact.py

  apps/leads/models/lead.py
  apps/leads/repositories/leads_repo.py
  apps/leads/services/create_lead.py
  apps/leads/services/close_lead.py
  apps/leads/services/mark_replied.py

  apps/sequences/models/sequence.py
  apps/sequences/repositories/sequences_repo.py
  apps/sequences/services/expand_steps.py
  apps/sequences/services/pick_active_sequence.py
  apps/sequences/scheduler/enqueue_step.py
  apps/sequences/scheduler/stop_rules.py

  apps/messaging/models/message.py
  apps/messaging/providers/sendgrid_send.py
  apps/messaging/providers/twilio_send.py
  apps/messaging/composer/email_subject.py
  apps/messaging/composer/email_body.py
  apps/messaging/composer/sms_body.py
  apps/messaging/tasks/send_email.py
  apps/messaging/tasks/send_sms.py
  apps/messaging/services/queue_email.py
  apps/messaging/services/queue_sms.py

  apps/webhooks/urls.py
  apps/webhooks/verify/shopify_hmac.py
  apps/webhooks/verify/twilio_sig.py
  apps/webhooks/views/shopify_abandoned.py
  apps/webhooks/views/shopify_order_created.py
  apps/webhooks/views/inbound_email.py
  apps/webhooks/views/inbound_sms.py

  apps/api/urls.py
  apps/api/serializers/contact_in.py
  apps/api/serializers/lead_in.py
  apps/api/serializers/lead_out.py
  apps/api/views/health.py
  apps/api/views/ingest_lead.py

  apps/widget/static/widget/lead-capture.js
  apps/widget/versions.json
  apps/widget/views/serve_widget.py

  scripts/smoke.sh
  scripts/run_celery.sh
  scripts/setup_pa.sh
)

for f in "${FILES[@]}"; do
  if [ ! -f "$f" ]; then
    mkdir -p "$(dirname "$f")"
    # special case: versions.json should be {}
    if [[ "$f" == "apps/widget/versions.json" ]]; then
      printf "{}" > "$f"
    else
      : > "$f"
    fi
    echo "[scaffold] created $f"
  fi
done

echo "[scaffold] done."
