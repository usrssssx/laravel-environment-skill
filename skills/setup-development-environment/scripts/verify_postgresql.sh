#!/usr/bin/env bash
set -euo pipefail

for variable in PGHOST PGPORT PGDATABASE PGUSER PGPASSWORD; do
  if [[ -z "${!variable:-}" ]]; then
    echo "ERROR: $variable is required in the process environment" >&2
    exit 2
  fi
done

[[ "$PGPORT" =~ ^[0-9]{1,5}$ ]] || { echo "ERROR: invalid PGPORT" >&2; exit 2; }

psql \
  --no-psqlrc \
  --set=ON_ERROR_STOP=1 \
  --tuples-only \
  --no-align \
  --command="select current_database(), current_user, coalesce(inet_server_addr()::text, 'local-socket'), version();"

psql \
  --no-psqlrc \
  --set=ON_ERROR_STOP=1 \
  --command="begin; create temporary table codex_environment_probe(id integer primary key); insert into codex_environment_probe values (1); select count(*) from codex_environment_probe; rollback;"
