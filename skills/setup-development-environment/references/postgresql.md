# PostgreSQL profile

Configure PostgreSQL as Laravel's primary application database.

## Local environment

- Install PostgreSQL as a native local service or use an existing reachable instance.
- Record and verify the installed major version instead of silently upgrading it.
- Use `127.0.0.1` as `DB_HOST` for a local service unless the inspected environment requires another host.
- Bind the database to loopback by default and do not expose it publicly.
- Verify readiness with `pg_isready` before migrations and tests.
- Create separate application and test databases.

## Laravel

- Set `DB_CONNECTION=pgsql`.
- Keep credentials outside Git.
- Use Laravel migrations as the authoritative schema history.
- Check migration status and migrate a clean test database in CI.
- Use transactions in tests where compatible.
- Configure UTF-8, UTC storage, indexes, foreign keys, unique constraints, and explicit numeric precision.

## Deployment

- Back up production before potentially destructive changes.
- Prefer expand/contract migrations across releases.
- Analyze locks and runtime for large table changes.
- Roll back application code independently from database changes.
- Never automate `migrate:rollback` in production without a proven data-safe plan.

## Verification

- Confirm PDO PostgreSQL extension availability.
- Confirm Laravel can connect.
- Run migrations on clean local and test databases.
- Run a safe read/write transaction.
- Verify backup creation and a restore drill on test before claiming readiness.
