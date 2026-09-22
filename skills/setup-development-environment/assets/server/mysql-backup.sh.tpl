#!/usr/bin/env bash
set -euo pipefail

umask 077

database="${MYSQL_BACKUP_DATABASE:-__DATABASE__}"
config="${MYSQL_BACKUP_CONFIG:-$HOME/.config/__PROJECT_SLUG__/mysql-backup.cnf}"
backup_dir="${MYSQL_BACKUP_DIR:-$HOME/backups/mysql/$database}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$backup_dir/$database-$timestamp.sql.gz"
temporary="$backup_dir/.$database-$timestamp.sql.gz.tmp"

mkdir -p "$backup_dir"
trap 'rm -f "$temporary"' EXIT

mysqldump \
  --defaults-extra-file="$config" \
  --single-transaction \
  --quick \
  --triggers \
  --hex-blob \
  --no-tablespaces \
  --set-gtid-purged=OFF \
  "$database" | gzip -9 > "$temporary"

test -s "$temporary"
gzip -t "$temporary"
mv "$temporary" "$target"

find "$backup_dir" -maxdepth 1 -type f -name "$database-*.sql.gz" -mtime +4 -delete
mapfile -t backups < <(find "$backup_dir" -maxdepth 1 -type f -name "$database-*.sql.gz" -printf '%T@ %p\n' | sort -nr | cut -d' ' -f2-)
if (( ${#backups[@]} > 5 )); then
  printf '%s\0' "${backups[@]:5}" | xargs -0 --no-run-if-empty rm --
fi

printf 'backup=%s\n' "$target"
