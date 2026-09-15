#!/usr/bin/env bash
set -euo pipefail

revision="${1:-}"
output="${2:-}"

[[ "$revision" =~ ^[A-Za-z0-9._-]{7,64}$ ]] || { echo "ERROR: invalid revision" >&2; exit 2; }
[[ -n "$output" ]] || { echo "Usage: package-release.sh <revision> <output.tar.gz>" >&2; exit 2; }
[[ -f deploy.ignore ]] || { echo "ERROR: deploy.ignore is missing" >&2; exit 1; }

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

rsync -a --exclude-from=deploy.ignore --exclude=.deploy/ ./ "$stage/"

if [[ -x scripts/check-deploy-artifact.sh ]]; then
  scripts/check-deploy-artifact.sh "$stage"
fi

mkdir -p "$(dirname "$output")"
tar -C "$stage" -czf "$output" .
sha256sum "$output" > "$output.sha256"

