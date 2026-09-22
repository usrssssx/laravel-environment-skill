#!/usr/bin/env bash
set -euo pipefail

deploy_path="${1:-}"
revision="${2:-}"
archive="${3:-}"
health_url="${4:-}"

[[ "$deploy_path" =~ ^/[A-Za-z0-9._/-]+$ ]] || { echo "ERROR: invalid deploy path" >&2; exit 2; }
[[ "$revision" =~ ^[A-Za-z0-9._-]{7,64}$ ]] || { echo "ERROR: invalid revision" >&2; exit 2; }
[[ "$archive" =~ ^/tmp/release-[A-Za-z0-9._-]+\.tar\.gz$ ]] || { echo "ERROR: invalid archive path" >&2; exit 2; }
[[ "$health_url" =~ ^https://[A-Za-z0-9._:/-]+$ ]] || { echo "ERROR: invalid health URL" >&2; exit 2; }

mkdir -p "$deploy_path/releases" "$deploy_path/shared/storage" "$deploy_path/shared/backups"
exec 9>"$deploy_path/deploy.lock"
flock -n 9 || { echo "ERROR: another deployment is running" >&2; exit 1; }

release="$deploy_path/releases/$revision"
previous=""
if [[ -L "$deploy_path/current" ]]; then
  previous="$(readlink -f "$deploy_path/current")"
fi

if [[ -e "$release" ]]; then
  echo "ERROR: release already exists: $release" >&2
  exit 1
fi

mkdir "$release"
tar -xzf "$archive" -C "$release"
printf '%s\n' "$revision" > "$release/REVISION"

if [[ ! -f "$deploy_path/shared/.env" ]]; then
  echo "ERROR: server environment file is missing: $deploy_path/shared/.env" >&2
  exit 1
fi

ln -s "$deploy_path/shared/.env" "$release/.env"
rm -rf "$release/storage"
ln -s "$deploy_path/shared/storage" "$release/storage"

cd "$release"

if [[ -x "$deploy_path/shared/pre-deploy.sh" ]]; then
  "$deploy_path/shared/pre-deploy.sh" "$revision"
fi

php artisan migrate --force
php artisan config:cache
php artisan route:cache
php artisan view:cache

ln -s "$release" "$deploy_path/current.next"
mv -Tf "$deploy_path/current.next" "$deploy_path/current"

rollback_application() {
  if [[ -n "$previous" && -d "$previous" ]]; then
    ln -s "$previous" "$deploy_path/current.rollback"
    mv -Tf "$deploy_path/current.rollback" "$deploy_path/current"
    cd "$previous"
    php artisan queue:restart || true
  fi
}

trap rollback_application ERR

php artisan queue:restart
curl --fail --show-error --silent --retry 5 --retry-delay 2 "$health_url/health" >/dev/null

trap - ERR
rm -f "$archive" "$0"
echo "DEPLOYED_REVISION=$revision"
