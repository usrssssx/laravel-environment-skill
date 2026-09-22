#!/usr/bin/env bash
set -euo pipefail

root="${1:-.}"

if [[ ! -d "$root" ]]; then
  echo "ERROR: project root does not exist: $root" >&2
  exit 2
fi

cd "$root"

command_state() {
  local command_name="$1"
  if command -v "$command_name" >/dev/null 2>&1; then
    printf '%s=available\n' "$command_name"
  else
    printf '%s=missing\n' "$command_name"
  fi
}

file_state() {
  local path="$1"
  if [[ -e "$path" ]]; then
    printf '%s=present\n' "$path"
  else
    printf '%s=absent\n' "$path"
  fi
}

redact_remote() {
  sed -E 's#(https?://)[^/@]+@#\1***@#'
}

echo "[project]"
printf 'root=%s\n' "$(pwd)"
file_state composer.json
file_state composer.lock
file_state artisan
file_state package.json
file_state package-lock.json
file_state pnpm-lock.yaml
file_state yarn.lock
file_state .env.example
file_state project-environment.json

echo "[tools]"
for tool in git php php-fpm composer node npm mysql mysqladmin redis-cli nginx systemctl brew apt-get gh ssh curl; do
  command_state "$tool"
done

echo "[versions]"
command -v php >/dev/null 2>&1 && php -r 'printf("php=%s\n", PHP_VERSION);' || true
command -v composer >/dev/null 2>&1 && composer --version --no-ansi 2>/dev/null | head -n 1 || true
command -v node >/dev/null 2>&1 && printf 'node=%s\n' "$(node --version)" || true
command -v mysql >/dev/null 2>&1 && mysql --version 2>/dev/null || true
command -v redis-cli >/dev/null 2>&1 && redis-cli --version 2>/dev/null || true
command -v nginx >/dev/null 2>&1 && nginx -v 2>&1 || true

echo "[git]"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'repository=yes\n'
  printf 'branch=%s\n' "$(git branch --show-current 2>/dev/null || true)"
  printf 'head=%s\n' "$(git rev-parse --short HEAD 2>/dev/null || true)"
  remote="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -n "$remote" ]]; then
    printf 'origin=%s\n' "$(printf '%s' "$remote" | redact_remote)"
  else
    printf 'origin=missing\n'
  fi
  printf 'changed_files=%s\n' "$(git status --short | wc -l | tr -d ' ')"
else
  printf 'repository=no\n'
fi

echo "[github]"
if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    printf 'authenticated=yes\n'
  else
    printf 'authenticated=no\n'
  fi
else
  printf 'authenticated=tool-missing\n'
fi

echo "[framework]"
if [[ -f artisan ]] && command -v php >/dev/null 2>&1; then
  php artisan --version --no-ansi 2>/dev/null || true
fi
