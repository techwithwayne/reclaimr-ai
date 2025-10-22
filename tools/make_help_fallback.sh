#!/usr/bin/env bash
# Print "help" for this repo even if `make` is not installed.
# If `make` exists, run `make help` (no exec), verify success, then print PASS.
# Otherwise, parse Makefile and echo a friendly menu, then print PASS.

set -euo pipefail

MAKEFILE="${1:-Makefile}"

if command -v make >/dev/null 2>&1; then
  # Invoke (not exec) so we can emit PASS after it returns.
  if make help; then
    echo "PASS: fallback help rendered (via make help)"
    exit 0
  else
    echo "[error] \`make help\` failed; falling back to parser" >&2
    # continue into manual parsing below
  fi
fi

# No `make` on PATH or `make help` failed — parse Makefile to render a minimal menu.
if [[ ! -f "$MAKEFILE" ]]; then
  echo "[error] $MAKEFILE not found in the current directory."
  exit 2
fi

echo "Reclaimr Make targets (fallback):"
declare -a preferred=(audit sync push push-auto creds validate-apps validate-alt curl-dry curl-apply deploy-dry deploy-apply)

# Collect available targets
mapfile -t targets < <(awk -F':' '/^[a-zA-Z0-9._-]+:/{print $1}' "$MAKEFILE" | sort -u)

have() { grep -qE "^$1:" "$MAKEFILE"; }

for t in "${preferred[@]}"; do
  if have "$t"; then
    case "$t" in
      audit)         desc="repo audit (read-only)";;
      sync)          desc="safe sync (dry-run)";;
      push)          desc="push if clean; block if dirty";;
      push-auto)     desc="auto-commit dirty tree and push";;
      creds)         desc="store GitHub creds (interactive)";;
      validate-apps) desc="PA validate apps.techwithwayne.com (dry-run)";;
      validate-alt)  desc="PA validate techwithwayne.pythonanywhere.com (dry-run)";;
      curl-dry)      desc="curl health+ingest to \$(BASE_URL) (dry-run)";;
      curl-apply)    desc="curl health+ingest to \$(BASE_URL) (apply)";;
      deploy-dry)    desc="PA deploy plan (dry-run)";;
      deploy-apply)  desc="PA deploy now (apply)";;
      *)             desc="";;
    esac
    printf "  make %-13s - %s\n" "$t" "$desc"
  fi
done

BASE_URL_DEFAULT="$(grep -E '^BASE_URL\s*\?=' "$MAKEFILE" | awk '{print $3}' | head -n1)"
ALT_URL_DEFAULT="$(grep -E '^ALT_URL\s*\?=' "$MAKEFILE" | awk '{print $3}' | head -n1)"
KEY_DEFAULT="$(grep -E '^KEY\s*\?=' "$MAKEFILE" | awk '{print $3}' | head -n1)"
echo "Vars: KEY=${KEY_DEFAULT:-acc_live_test} BASE_URL=${BASE_URL_DEFAULT:-<unset>} ALT_URL=${ALT_URL_DEFAULT:-<unset>}"

echo "PASS: fallback help rendered (manual parser)"
