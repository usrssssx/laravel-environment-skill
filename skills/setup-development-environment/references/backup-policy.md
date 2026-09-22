# Backup and restore policy

Backups are mandatory for readiness.

## Minimum standard

- Run at least daily during a low-traffic window.
- Retain daily recovery points for no more than five days. Use five days by default; values from one through five are valid.
- Keep backups outside versioned release directories and outside the primary database storage.
- Separate projects/portals sufficiently that one recovery can be performed without restoring every customer.
- Encrypt off-site backups and restrict provider credentials to the required bucket/path.
- Monitor backup failures and storage capacity.

Do not ask the user to configure MySQL backups manually in CloudPanel. After key-only SSH and database access are verified, configure the backup directly with the native server tools. CloudPanel may have a longer default retention than this project permits, so the skill-owned backup job must independently enforce this policy. For external managed MySQL, prefer the provider API or CLI when available and verify the configured recovery target.

## Automatic MySQL setup

1. Verify `mysqldump`, `gzip`, `flock`, and `crontab` over key-only SSH, plus a writable backup location outside versioned releases.
2. Adapt and install `assets/server/mysql-backup.sh.tpl` under the deploy user's private `bin` directory.
3. Write the database password from transient input to a dedicated MySQL client option file outside the repository and release tree. Set its directory to mode `700` and file to mode `600`. Never put the password in a command argument, cron line, report, or generated project file.
4. Install the tagged cron entry from `assets/server/mysql-backup.cron.tpl` idempotently. Preserve unrelated cron entries and use `flock` to prevent overlapping runs.
5. Run the job immediately. Verify exit status, nonzero size, gzip integrity, timestamp, and that the dump belongs to the intended database.
6. Delete artifacts older than five days and independently cap the directory at five dump files. A project may choose a shorter retention from one through five days.
7. Restore the fresh dump into an isolated temporary database and run schema plus representative-read checks. Drop only that temporary database after recording evidence. If the application user cannot create databases, use a separate local MySQL instance or have an administrator create a temporary restore target; never restore over the source database.

Only request user or administrator action when technical verification proves that the deploy account lacks a required tool, scheduler, writable location, or safe restore target. Do not present routine backup setup as a CloudPanel manual checkpoint.

For Bitrix24 `entity.*`, define a per-portal export/restore procedure for every application-owned entity. The portal is the recovery boundary. Verify that one portal can be exported and restored without overwriting another portal's data. Platform availability alone is not an application-level backup.

## Verification

1. Record implementation, schedule, retention, database/project scope, and last successful run.
2. Verify a recent nonempty artifact. Use `scripts/verify_backup_artifact.py` when accessible through the filesystem.
3. Restore into a new isolated test database or temporary test location, never over the source.
4. Run schema checks and a representative read after restore.
5. Delete the temporary restored target only after evidence is recorded.

Do not mark `restore_drill_verified` from a backup creation message alone. A restore command or provider restore operation must actually complete.
