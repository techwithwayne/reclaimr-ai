#!/usr/bin/env bash
# Reclaimr: Safe Git Sync helper
# - Always fetches first
# - Reports ahead/behind vs origin/<branch>
# - Dry-run by default; use --apply to perform safe updates
# - If working tree is dirty and --apply is used, auto-stash before pull and pop after
# Usage:
#   bash tools/git_safe_sync.sh          # read-only report
#   bash tools/git_safe_sync.sh --apply  # perform safe sync (ff-only or rebase)
set -euo pipefail

echo "== Reclaimr Safe Git Sync =="

# Ensure git repo
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "[error] Not inside a git repo"; exit 1; }

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
UPSTREAM="origin/${BRANCH}"

echo "Repo root: $(git rev-parse --show-toplevel)"
echo "Current branch: ${BRANCH}"

ORIGIN_URL="$(git remote get-url origin 2>/dev/null || echo "<none>")"
if [[ "${ORIGIN_URL}" == "<none>" ]]; then
  echo "[error] No 'origin' remote configured."
  exit 2
fi
echo "Remote 'origin': ${ORIGIN_URL}"

echo "-- Fetching origin --"
git fetch origin --quiet || { echo "[warn] git fetch failed (network?)"; }

# Compute divergence (defaults if upstream missing)
AHEAD="0"; BEHIND="0"
if git rev-parse --verify "${UPSTREAM}" >/dev/null 2>&1; then
  # format: "<ahead> <behind>"
  read -r AHEAD BEHIND < <(git rev-list --left-right --count "${BRANCH}...${UPSTREAM}" | awk '{print $1" "$2}')
else
  echo "[warn] Upstream ${UPSTREAM} not found on remote."
  AHEAD="$(git rev-list --count ${BRANCH} 2>/dev/null || echo 0)"
  BEHIND="N/A"
fi

# Working tree cleanliness
if [[ -z "$(git status --porcelain)" ]]; then
  WT="clean"
else
  WT="dirty"
fi

echo "Working tree: ${WT}"
echo "Divergence (local vs ${UPSTREAM}): ahead=${AHEAD} behind=${BEHIND}"

# Recommendation
ACTION="none"
if [[ "${BEHIND}" != "N/A" ]]; then
  if (( BEHIND > 0 && AHEAD == 0 )); then
    echo "Recommendation: fast-forward pull (no local commits)."
    ACTION="ff"
  elif (( BEHIND > 0 && AHEAD > 0 )); then
    echo "Recommendation: pull with rebase (local + remote commits)."
    ACTION="rebase"
  elif (( BEHIND == 0 && AHEAD > 0 )); then
    echo "Recommendation: push local commits to origin."
    ACTION="push"
  else
    echo "Recommendation: in sync; no action needed."
    ACTION="none"
  fi
else
  echo "Recommendation: publish branch first (git push -u origin ${BRANCH})."
  ACTION="publish"
fi

# Dry-run mode by default
if [[ "${1:-}" != "--apply" ]]; then
  echo "(dry-run) To apply recommended action safely, re-run with --apply."
  echo "PASS: safe sync dry-run complete"
  exit 0
fi

# --apply mode: perform safe action(s)
AUTO_STASH=0
if [[ "${WT}" == "dirty" ]]; then
  echo "-- Working tree dirty; creating auto-stash --"
  git stash push -u -m "reclaimr:auto-stash $(date -u +%Y%m%dT%H%M%SZ)" >/dev/null || true
  AUTO_STASH=1
fi

case "${ACTION}" in
  ff)
    echo "-- Performing fast-forward pull --"
    git pull --ff-only origin "${BRANCH}"
    ;;
  rebase)
    echo "-- Performing pull --rebase --"
    git pull --rebase origin "${BRANCH}"
    ;;
  push)
    echo "-- Local ahead; pushing to origin --"
    git push origin "${BRANCH}"
    ;;
  publish)
    echo "-- Publishing branch to origin --"
    git push -u origin "${BRANCH}"
    ;;
  none)
    echo "-- No changes applied; already in sync --"
    ;;
esac

# Restore stash if created
if (( AUTO_STASH == 1 )); then
  echo "-- Restoring auto-stash --"
  # If no conflicts, this exits 0; otherwise, user will resolve manually.
  git stash pop || true
fi

echo "PASS: safe sync --apply complete"
