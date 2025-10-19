# Reclaimr AI — Lead Revival & Follow-Up Agent

Reclaimr is a Django-based, embeddable AI follow-up engine that revives ghosted leads and abandoned checkouts.
It works for any website via a `<script>` widget and integrates natively with Shopify (abandoned checkout / order webhooks).

## Core
- Django 5.2 LTS + DRF
- Celery 5.5 (Upstash Redis broker/result)
- Postgres (PythonAnywhere in production)
- SendGrid (email) → v1
- Twilio (SMS) → v2

## Features (MVP)
- Ingest leads from script-tag form or Shopify webhooks
- Smart 3-step cadence (Email → SMS → Email) with reply/stop logic
- Per-account API keys; tenant-aware rate limits
- One-click unsubscribe & basic compliance
- Minimal dashboard for activity and logs

## Deploy Targets
- Dev: local (Windows + Git Bash)
- Prod: PythonAnywhere (web app + Always-On task for Celery); Upstash Redis

## Repo Layout (planned)
- /reclaimr/           # Django app (models, views, tasks, webhooks)
- /config/             # Django project (settings, urls, celery)
- /static/widget/      # script-tag capture widget
- /scripts/            # helper scripts (smoke tests, PA setup)

## License
MIT
