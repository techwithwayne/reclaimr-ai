#!/usr/bin/env bash
# Reclaimr: GitHub Credentials Setup (HTTPS)
# Dry-run by default. In --apply mode:
# - Sets: git config --global credential.helper store
# - Seeds: ~/.git-credentials with https://USERNAME:TOKEN@github.com
#   (Used for any repo under github.com via HTTPS.)
#
# Usage:
#   bash tools/git_credentials_setup.sh           # dry-run / report only
#   bash tools/git_credentials_setup.sh --apply   # configure + store creds
#
# Non-interactive support:
#   GITHUB_USER=<user> GITHUB_TOKEN=<token> bash tools/git_credentials_setup.sh --apply

set -euo pipefail

echo "== Reclaimr GitHub Credentials Setup =="

# Verify we're in a git repo (not strictly required for global config, but helpful)
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
  echo "Repo root: ${ROOT}"
  ORIGIN_URL="$(git remote get-url origin 2>/dev/null || echo '<none>')"
  BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '<unknown>')"
  echo "Remote 'origin': ${ORIGIN_URL}"
  echo "Current branch: ${BRANCH}"
else
  echo "[note] Not inside a git repo; proceeding with global credential config."
fi

# Current helper
CUR_HELPER="$(git config --global credential.helper || echo '<unset>')"
echo "Current credential.helper: ${CUR_HELPER}"

CRED_FILE="${HOME}/.git-credentials"
echo "Credential file: ${CRED_FILE}"

EXISTS_LINE=0
if [[ -f "${CRED_FILE}" ]]; then
  if grep -qE '^https://[^:@]+:[^@]+@github\.com/?$' "${CRED_FILE}"; then
    EXISTS_LINE=1
  fi
fi
echo "Has GitHub entry in credentials: $([[ ${EXISTS_LINE} -eq 1 ]] && echo 'yes' || echo 'no')"

if [[ "${1:-}" != "--apply" ]]; then
  echo "(dry-run) To apply configuration, re-run with --apply."
  echo "PASS: credentials setup dry-run complete"
  exit 0
fi

# --apply mode
echo "-- Applying credential configuration --"
git config --global credential.helper store
echo "Set: credential.helper=store (global)"

# Determine username/token (env preferred; else prompt)
USER_IN="${GITHUB_USER:-}"
TOKEN_IN="${GITHUB_TOKEN:-}"

if [[ -z "${USER_IN}" ]]; then
  read -r -p "GitHub username: " USER_IN
fi
if [[ -z "${TOKEN_IN}" ]]; then
  read -r -s -p "GitHub personal access token: " TOKEN_IN
  echo ""
fi

if [[ -z "${USER_IN}" || -z "${TOKEN_IN}" ]]; then
  echo "[error] Username or token empty; aborting."
  exit 2
fi

mkdir -p "$(dirname "${CRED_FILE}")"
LINE="https://${USER_IN}:${TOKEN_IN}@github.com"

# Remove any existing github.com lines to avoid duplicates, then append
if [[ -f "${CRED_FILE}" ]]; then
  grep -vE '^https://[^:@]+:[^@]+@github\.com/?$' "${CRED_FILE}" > "${CRED_FILE}.tmp" || true
  mv "${CRED_FILE}.tmp" "${CRED_FILE}"
fi
echo "${LINE}" >> "${CRED_FILE}"
chmod 600 "${CRED_FILE}"

echo "Wrote GitHub credential to ${CRED_FILE} (permissions set to 600)."
echo "Note: This stores your token in plain text on this server account."

# Quick verification (non-fatal)
if git ls-remote --heads 2>/dev/null | head -n 1 >/dev/null; then
  echo "Verified: git can access a remote with stored credentials."
else
  echo "[note] Could not verify remote access here (maybe not in a repo). This is non-fatal."
fi

echo "PASS: credentials stored and helper configured"
