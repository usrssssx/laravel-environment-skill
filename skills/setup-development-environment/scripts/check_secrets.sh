#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"
cd "$root"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: secret check requires a Git repository" >&2
  exit 2
fi

failed=0

while IFS= read -r path; do
  case "$path" in
    .env|*/.env|*.pem|*.key|*.p12|*.pfx|id_rsa|*/id_rsa|id_ed25519|*/id_ed25519)
      echo "FORBIDDEN_TRACKED_FILE: $path"
      failed=1
      ;;
  esac
done < <(git ls-files)

patterns=(
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'github_pat_[A-Za-z0-9_]{20,}'
  'ghp_[A-Za-z0-9]{20,}'
  'AKIA[0-9A-Z]{16}'
  'xox[baprs]-[A-Za-z0-9-]{20,}'
)

for pattern in "${patterns[@]}"; do
  if matches="$(git grep -n -I -E -e "$pattern" -- . ':(exclude).agents/skills/setup-development-environment/scripts/check_secrets.sh')"; then
    if [[ -n "$matches" ]]; then
      echo "$matches"
      failed=1
    fi
  else
    status=$?
    if [[ "$status" -ne 1 ]]; then
      echo "ERROR: git grep failed while checking a secret pattern" >&2
      exit 2
    fi
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "Secret check failed. Inspect findings without printing secret values further." >&2
  exit 1
fi

echo "Secret check passed. No tracked private-key files or known token patterns found."
