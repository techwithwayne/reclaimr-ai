#!/usr/bin/env bash
# Reclaimr Repo Sync Audit (safe, read-only). Run from anywhere inside the repo.
# Usage: bash tools/repo_sync_audit.sh [--fetch]
set -euo pipefail

echo "== Reclaimr Repo Sync Audit =="

# Ensure we're inside a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[error] Not inside a git repository."
  exit 1
fi

# Repo root
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "<unknown>")"
echo "Repo root: $ROOT"

# Remote URL (origin)
ORIGIN_URL="$(git remote get-url origin 2>/dev/null || echo "<none>")"
echo "Remote 'origin': $ORIGIN_URL"

# Branch / HEAD
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "<detached>")"
echo "Current branch: $BRANCH"

# Working tree status (clean/dirty) + summary
if [[ -z "$(git status --porcelain)" ]]; then
  echo "Working tree: clean"
else
  echo "Working tree: dirty"
  echo "--- Uncommitted changes (git status --porcelain) ---"
  git status --porcelain
  echo "----------------------------------------------------"
fi

# Untracked files (compact)
UNTRACKED="$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')"
echo "Untracked files: $UNTRACKED"

# Optionally fetch to compute ahead/behind
AHEAD="?"
BEHIND="?"
if [[ "${1:-}" == "--fetch" ]]; then
  # Network may be unavailable; don't fail the script if fetch fails.
  if git fetch origin --quiet 2>/dev/null; then
    UPSTREAM="origin/${BRANCH}"
    if git rev-parse --verify "$UPSTREAM" >/dev/null 2>&1; then
      AHEAD="$(git rev-list --left-right --count ${BRANCH}...${UPSTREAM} | awk '{print $1}')"
      BEHIND="$(git rev-list --left-right --count ${BRANCH}...${UPSTREAM} | awk '{print $2}')"
    else
      AHEAD="N/A"
      BEHIND="N/A"
    fi
  else
    AHEAD="N/A"
    BEHIND="N/A"
  fi
  echo "Divergence (local vs origin/${BRANCH}): ahead=${AHEAD} behind=${BEHIND}"
else
  echo "Divergence (local vs origin/${BRANCH}): (skip fetch; run with --fetch)"
fi

# Helpful next commands (suggestions only)
echo ""
echo "Suggested next steps:"
if [[ "$ORIGIN_URL" == "<none>" ]]; then
  echo "  - Add remote: git remote add origin <YOUR_GITHUB_REPO_URL>"
fi
echo "  - To see a clean diff summary:   git status -sb"
echo "  - To compare with origin:        git fetch origin && git log --oneline --graph --decorate --all | head -n 30"
echo "  - To create a scan archive:      tar -a -c -f \"reclaimr_scan_$(date +%Y%m%d_%H%M).zip\" \\"
echo "                                    apps config manage.py requirements.txt pyproject.toml README.md \\"
echo "                                    --exclude='venv/*' --exclude='.git/*' --exclude='*/__pycache__/*' \\"
echo "                                    --exclude='*/migrations/*' --exclude='*.pyc' --exclude='*.log' \\"
echo "                                    --exclude='.DS_Store' --exclude='*.sqlite3' --exclude='.env' --exclude='.env.*' \\"
echo "                                    --exclude='node_modules/*'"
echo ""
echo "PASS: audit complete (read-only)"
