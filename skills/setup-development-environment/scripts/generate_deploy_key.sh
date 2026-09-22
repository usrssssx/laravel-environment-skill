#!/usr/bin/env bash
set -euo pipefail

key_path="${1:-}"
comment="${2:-codex-deploy}"

if [[ -z "$key_path" || "$key_path" != /* ]]; then
  echo "Usage: generate_deploy_key.sh /absolute/private-key-path [comment]" >&2
  exit 2
fi
if [[ -e "$key_path" || -e "$key_path.pub" ]]; then
  echo "ERROR: refusing to overwrite an existing key: $key_path" >&2
  exit 2
fi
if [[ ! "$comment" =~ ^[A-Za-z0-9._@-]{1,128}$ ]]; then
  echo "ERROR: invalid key comment" >&2
  exit 2
fi

install -m 700 -d "$(dirname "$key_path")"
umask 077
ssh-keygen -q -t ed25519 -a 100 -N '' -C "$comment" -f "$key_path"
chmod 600 "$key_path"
chmod 644 "$key_path.pub"

echo "Public key (add this to the CloudPanel deploy user):"
cat "$key_path.pub"
echo "Private key created at $key_path and was not printed."
