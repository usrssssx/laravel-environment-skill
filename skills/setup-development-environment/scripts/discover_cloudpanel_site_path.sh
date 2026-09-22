#!/usr/bin/env bash
set -euo pipefail

host="${1:-}"
port="${2:-}"
ssh_user="${3:-}"
site_user="${4:-}"
domain="${5:-}"
key_path="${6:-}"
known_hosts="${7:-}"

if [[ -z "$host" || -z "$port" || -z "$ssh_user" || -z "$site_user" || -z "$domain" || -z "$key_path" || -z "$known_hosts" ]]; then
  echo "Usage: discover_cloudpanel_site_path.sh host port ssh-user site-user domain private-key known-hosts" >&2
  exit 2
fi

[[ "$host" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "ERROR: invalid host" >&2; exit 2; }
[[ "$port" =~ ^[0-9]{1,5}$ ]] && (( port >= 1 && port <= 65535 )) || { echo "ERROR: invalid port" >&2; exit 2; }
[[ "$ssh_user" =~ ^[A-Za-z_][A-Za-z0-9_-]*$ ]] || { echo "ERROR: invalid SSH user" >&2; exit 2; }
[[ "$site_user" =~ ^[A-Za-z_][A-Za-z0-9_-]*$ ]] || { echo "ERROR: invalid site user" >&2; exit 2; }
[[ "$domain" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]] || { echo "ERROR: invalid domain" >&2; exit 2; }
[[ -f "$key_path" ]] || { echo "ERROR: private key not found" >&2; exit 2; }
[[ -s "$known_hosts" ]] || { echo "ERROR: known_hosts is missing or empty" >&2; exit 2; }

remote_command="set -eu; for candidate in '/home/$site_user/htdocs/$domain' \"\$HOME/htdocs/$domain\" '/home/$ssh_user/htdocs/$domain'; do if test -d \"\$candidate\"; then printf 'path=%s\\n' \"\$(realpath \"\$candidate\")\"; exit 0; fi; done; echo 'ERROR: CloudPanel site directory was not found for $domain' >&2; exit 1"

ssh \
  -i "$key_path" \
  -p "$port" \
  -o BatchMode=yes \
  -o IdentitiesOnly=yes \
  -o PasswordAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile="$known_hosts" \
  "$ssh_user@$host" \
  "$remote_command"
