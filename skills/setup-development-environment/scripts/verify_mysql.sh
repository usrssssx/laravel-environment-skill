#!/usr/bin/env bash
set -euo pipefail

for variable in MYSQL_HOST MYSQL_TCP_PORT MYSQL_DATABASE MYSQL_USER MYSQL_PWD; do
  if [[ -z "${!variable:-}" ]]; then
    echo "ERROR: $variable is required in the process environment" >&2
    exit 2
  fi
done

[[ "$MYSQL_TCP_PORT" =~ ^[0-9]{1,5}$ ]] || { echo "ERROR: invalid MYSQL_TCP_PORT" >&2; exit 2; }

mysql \
  --protocol=TCP \
  --host="$MYSQL_HOST" \
  --port="$MYSQL_TCP_PORT" \
  --user="$MYSQL_USER" \
  --database="$MYSQL_DATABASE" \
  --batch \
  --skip-column-names \
  --execute="select database(), current_user(), version(), @@character_set_database, @@collation_database;"

mysql \
  --protocol=TCP \
  --host="$MYSQL_HOST" \
  --port="$MYSQL_TCP_PORT" \
  --user="$MYSQL_USER" \
  --database="$MYSQL_DATABASE" \
  --batch \
  --execute="start transaction; create temporary table codex_environment_probe(id integer primary key); insert into codex_environment_probe values (1); select count(*) from codex_environment_probe; rollback;"
