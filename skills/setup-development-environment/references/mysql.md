# MySQL profile

Configure MySQL as Laravel's primary application database. A CloudPanel-provided compatible MariaDB server uses the same Laravel `mysql` driver.

## Local environment

- Reuse an existing compatible MySQL/MariaDB service or install one natively with the operating system package manager.
- Record and verify the server version instead of silently upgrading it.
- Use `127.0.0.1` and port `3306` for a local service unless the inspected environment requires another target.
- Bind the database to loopback by default and do not expose it publicly.
- Create separate application and test databases.

## Laravel

- Set `DB_CONNECTION=mysql`.
- Require PDO MySQL and keep credentials outside Git.
- Use Laravel migrations as the authoritative schema history.
- Use `utf8mb4` and a compatible collation; verify the actual server and connection values.
- Use transactions in tests where compatible, and define indexes, foreign keys, unique constraints, and numeric precision explicitly.

## CloudPanel and deployment

- Ask the user to create the test database in CloudPanel and provide only its generated database name, username, and password.
- Set `database.management=cloudpanel`, host `127.0.0.1`, and port `3306` internally unless an explicit external host was supplied.
- Treat the password as transient input. Place it only in the protected server `.env` and an approved secret store when genuinely needed; never save or repeat it in project metadata, reports, Git, or later chat messages.
- Use a dedicated least-privilege application user. Never use a server-wide administrative account in Laravel.
- Run `scripts/verify_mysql.sh` when the MySQL CLI exists. Otherwise perform the same connection metadata and rolled-back write probe through PHP PDO/Laravel.
- Prefer expand/contract migrations and never automate destructive production rollback.

## Verification

- Confirm PDO MySQL availability.
- Confirm Laravel can connect with the supplied account.
- Verify current database, current user, server version, `utf8mb4`, and collation.
- Run migrations on clean local and test databases.
- Run a safe write transaction and roll it back.
- Verify a daily backup, at least seven recovery points, a fresh artifact, and an isolated restore drill as defined in `backup-policy.md`.
