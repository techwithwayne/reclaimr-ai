#!/usr/bin/env bash
# Convert 'origin' from SSH to HTTPS for GitHub. Safe by default (no changes).
# Usage:
#   bash tools/git_origin_httpsify.sh            # show what would change
#   bash tools/git_origin_httpsify.sh --apply    # APPLY the remote change

set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[error] Not inside a git repository."
  exit 1
fi

CURR="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "${CURR}" ]]; then
  echo "[error] No 'origin' remote is set."
  exit 2
fi

echo "Current origin: ${CURR}"

HTTPS=""
# Pattern: git@github.com:owner/repo.git  -> https://github.com/owner/repo.git
if [[ "${CURR}" =~ ^git@github\.com:(.+)\.git$ ]]; then
  HTTPS="https://github.com/${BASH_REMATCH[1]}.git"
fi

# Already HTTPS?
if [[ -z "${HTTPS}" && "${CURR}" =~ ^https://github\.com/.+\.git$ ]]; then
  echo "Origin already uses HTTPS. No changes needed."
  echo "PASS: remote check complete (HTTPS already configured)"
  exit 0
fi

if [[ -z "${HTTPS}" ]]; then
  echo "[warn] Origin is neither SSH for GitHub nor recognized HTTPS. No change computed."
  echo "PASS: remote check complete (no-op)"
  exit 0
fi

echo "Proposed new origin: ${HTTPS}"

if [[ "${1:-}" == "--apply" ]]; then
  git remote set-url origin "${HTTPS}"
  echo "Applied. New origin:"
  git remote get-url origin
  echo "PASS: origin switched to HTTPS"
else
  echo "(dry-run) To apply:"
  echo "  git remote set-url origin \"${HTTPS}\""
  echo "PASS: dry-run complete (no changes made)"
fi
