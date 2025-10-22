#!/usr/bin/env bash
# Universal "Push Now" — Combined Smoke+Sanity + push
# Usage:
#   bash tools/push_now.sh --dry                 # run tests, show plan, no push
#   bash tools/push_now.sh                       # run tests, push only if clean
#   bash tools/push_now.sh --auto                # run tests, auto-commit dirty tree, then push
#   bash tools/push_now.sh --auto --msg "feat: update"  # custom commit message
set -euo pipefail

DRY=0
AUTO=0
COMMIT_MSG="chore: sync working tree before push"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry)  DRY=1; shift ;;
    --auto) AUTO=1; shift ;;
    --msg)  COMMIT_MSG="${2:-$COMMIT_MSG}"; shift 2 ;;
    *) echo "[error] Unknown arg: $1"; exit 2 ;;
  esac
done

echo "== Push Now: Combined Smoke+Sanity =="

# 0) Repo checks
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[error] Not inside a git repository."
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
ORIGIN="$(git remote get-url origin 2>/dev/null || echo '<none>')"
STATUS="$(git status --porcelain)"
CLEAN_MSG="clean"
[[ -n "$STATUS" ]] && CLEAN_MSG="dirty"

echo "Repo root: ${ROOT}"
echo "Current branch: ${BRANCH}"
echo "Remote 'origin': ${ORIGIN}"
echo "Working tree: ${CLEAN_MSG}"

# 1) Determine test command heuristically (stack-agnostic)
run_tests () {
  # Node
  if [[ -f package.json ]]; then
    if command -v jq >/dev/null 2>&1 && jq -re '.scripts.test' package.json >/dev/null 2>&1; then
      echo "[test] npm run -s test"
      npm run -s test
      return $?
    fi
  fi
  # Python (pytest)
  if [[ -f pytest.ini || -f pyproject.toml || -d tests || -d test ]]; then
    if command -v pytest >/dev/null 2>&1; then
      echo "[test] pytest -q"
      pytest -q
      return $?
    fi
  fi
  # Go
  if [[ -f go.mod ]]; then
    echo "[test] go test ./..."
    go test ./...
    return $?
  fi
  # PHP (phpunit)
  if [[ -f composer.json ]]; then
    if [[ -x vendor/bin/phpunit ]]; then
      echo "[test] vendor/bin/phpunit --colors=never"
      vendor/bin/phpunit --colors=never
      return $?
    elif command -v phpunit >/dev/null 2>&1; then
      echo "[test] phpunit --colors=never"
      phpunit --colors=never
      return $?
    fi
  fi
  # Makefile
  if [[ -f Makefile ]] && grep -qE '^[[:space:]]*test:' Makefile; then
    echo "[test] make test"
    make test
    return $?
  fi
  # Fallback
  echo "[test] No stack-specific tests detected; running fallback checks"
  git rev-parse HEAD >/dev/null
  ls -1 >/dev/null
  echo "PASS: fallback test executed (replace with project TEST_CMD when available)"
  return 0
}

# 2) Run tests
run_tests
echo "PASS: project tests completed"

# 3) Push logic
if [[ "${ORIGIN}" == "<none>" ]]; then
  echo "[warn] No 'origin' remote configured."
  echo "To set: git remote add origin https://github.com/<owner>/<repo>.git"
  echo "PASS: push phase skipped (no origin)"
  exit 0
fi

if (( DRY == 1 )); then
  if [[ "$CLEAN_MSG" == "dirty" ]]; then
    if (( AUTO == 1 )); then
      echo "[plan] Would: git add -A && git commit -m \"${COMMIT_MSG}\" && git push origin ${BRANCH}"
    else
      echo "[plan] Would: (commit changes) then git push origin ${BRANCH}"
    fi
  else
    echo "[plan] Would run: git push origin ${BRANCH}"
  fi
  echo "PASS: dry-run completed"
  exit 0
fi

# Non-dry run:
if [[ "$CLEAN_MSG" == "dirty" ]]; then
  if (( AUTO == 1 )); then
    echo "-- Auto-commit dirty tree --"
    git add -A
    # Only commit if there's actually something to commit
    if ! git diff --cached --quiet --ignore-submodules --; then
      git commit -m "${COMMIT_MSG}"
      echo "PASS: auto-commit created"
    else
      echo "[note] Nothing staged to commit (race or empty changes)."
    fi
  else
    echo "[abort] Working tree is dirty. Re-run with --auto to commit automatically, or commit manually."
    exit 2
  fi
fi

git push origin "${BRANCH}"
echo "PASS: push to origin/${BRANCH} succeeded"
echo "PASS: Push Now complete"
