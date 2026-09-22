# PostgreSQL profile

Configure PostgreSQL as Laravel's primary application database.

## Management boundary

Stock CloudPanel v2 does not manage PostgreSQL. Its documented database UI and backup commands are for MySQL/MariaDB. Use one of these explicit modes:

- `external_managed` (default): a dedicated PostgreSQL database from a managed provider;
- `native_explicit`: PostgreSQL installed outside CloudPanel's database management, only with explicit authorization and a documented owner, hardening, monitoring, backup, and restore process.

Never label native PostgreSQL as CloudPanel-managed. If the user wants CloudPanel's database UI, switching to MySQL/MariaDB is a separate architecture decision.

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

- Create a dedicated database and least-privilege application user; never use provider/master credentials in Laravel.
- Collect host, port, database name, and user only at the PostgreSQL checkpoint. Treat the password as a transient secret and place it only in the protected server `.env` and approved environment secrets.
- Run `scripts/verify_postgresql.sh` and record the returned database, user, server address, version, and successful rolled-back write probe.
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
- Verify a daily schedule, at least seven recovery points, a fresh artifact/snapshot, and an isolated restore. Read `backup-policy.md`.
