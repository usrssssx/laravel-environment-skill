#!/usr/bin/env bash
set -euo pipefail

host="${1:-}"
port="${2:-}"
user="${3:-}"
key_path="${4:-}"
known_hosts="${5:-}"
site_path="${6:-}"

if [[ -z "$host" || -z "$port" || -z "$user" || -z "$key_path" || -z "$known_hosts" || -z "$site_path" ]]; then
  echo "Usage: verify_ssh_access.sh host port user private-key known-hosts site-path" >&2
  exit 2
fi
[[ "$host" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "ERROR: invalid host" >&2; exit 2; }
[[ "$port" =~ ^[0-9]{1,5}$ ]] && (( port >= 1 && port <= 65535 )) || { echo "ERROR: invalid port" >&2; exit 2; }
[[ "$user" =~ ^[A-Za-z_][A-Za-z0-9_-]*$ ]] || { echo "ERROR: invalid user" >&2; exit 2; }
[[ "$site_path" =~ ^/[A-Za-z0-9._/-]+$ ]] || { echo "ERROR: invalid site path" >&2; exit 2; }
[[ -f "$key_path" ]] || { echo "ERROR: private key not found" >&2; exit 2; }
[[ -s "$known_hosts" ]] || { echo "ERROR: known_hosts is missing or empty" >&2; exit 2; }

remote_command="set -eu; test \"\$(id -un)\" = '$user'; test -d '$site_path'; test -w '$site_path'; printf 'user=%s\\npath=%s\\nwritable=yes\\n' \"\$(id -un)\" \"\$(realpath '$site_path')\""

ssh \
  -i "$key_path" \
  -p "$port" \
  -o BatchMode=yes \
  -o IdentitiesOnly=yes \
  -o PasswordAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile="$known_hosts" \
  "$user@$host" \
  "$remote_command"
