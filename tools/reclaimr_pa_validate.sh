#!/usr/bin/env bash
# Reclaimr — PythonAnywhere validator wrapper
# Targets PA domains instead of 127.0.0.1 and invokes the universal curl helper.
#
# Usage:
#   bash tools/reclaimr_pa_validate.sh                    # dry-run to apps.techwithwayne.com
#   bash tools/reclaimr_pa_validate.sh --apply            # actually hit live endpoints
#   bash tools/reclaimr_pa_validate.sh --site alt         # techwithwayne.pythonanywhere.com
#   bash tools/reclaimr_pa_validate.sh --url https://custom.domain
#   bash tools/reclaimr_pa_validate.sh --key acc_live_test --apply
#
# Defaults:
#   SITE=apps  → https://apps.techwithwayne.com
#   SITE=alt   → https://techwithwayne.pythonanywhere.com
#   KEY defaults to acc_live_test unless overridden via --key

set -euo pipefail

SITE="${1:-}"
APPLY=0
BASE_URL=""
KEY="${KEY:-acc_live_test}"  # allow env override
EMAIL="${EMAIL:-user@example.com}"
NAME="${NAME:-PA User}"
SOURCE="${SOURCE:-web_form}"

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --site)  SITE="${2:-apps}"; shift 2 ;;
    --url)   BASE_URL="${2:-}"; shift 2 ;;
    --key)   KEY="${2:-$KEY}"; shift 2 ;;
    --email) EMAIL="${2:-$EMAIL}"; shift 2 ;;
    --name)  NAME="${2:-$NAME}"; shift 2 ;;
    --source) SOURCE="${2:-$SOURCE}"; shift 2 ;;
    *) echo "[error] unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Decide base URL
if [[ -z "$BASE_URL" ]]; then
  case "$SITE" in
    ""|apps) BASE_URL="https://apps.techwithwayne.com" ;;
    alt)     BASE_URL="https://techwithwayne.pythonanywhere.com" ;;
    *) echo "[error] unknown --site value: $SITE (use 'apps' or 'alt', or pass --url)"; exit 2 ;;
  esac
fi

# Ensure the universal curl helper exists
if [[ ! -x tools/reclaimr_curl.sh ]]; then
  echo "[error] tools/reclaimr_curl.sh not found or not executable."
  echo "        Create it first, then re-run this script."
  exit 3
fi

MODE=$([[ $APPLY -eq 1 ]] && echo "--apply" || echo "")
echo "== Reclaimr PA Validate =="
echo "Base URL: ${BASE_URL}"
echo "Key: ${KEY:-<none>}"
echo "Mode: $([[ $APPLY -eq 1 ]] && echo apply || echo dry-run)"

# Delegate to the universal helper
bash tools/reclaimr_curl.sh --url "$BASE_URL" --key "$KEY" --email "$EMAIL" --name "$NAME" --source "$SOURCE" ${MODE}
