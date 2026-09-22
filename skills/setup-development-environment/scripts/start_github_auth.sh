#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) is required." >&2
  exit 2
fi

if gh auth status --hostname github.com >/dev/null 2>&1; then
  echo "GitHub CLI is already authenticated."
  exit 0
fi

echo "Starting GitHub browser authentication. Complete the confirmation in the browser."
gh auth login \
  --hostname github.com \
  --git-protocol https \
  --web

if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  echo "ERROR: GitHub authentication did not complete successfully." >&2
  exit 1
fi

echo "GitHub CLI authentication verified."
