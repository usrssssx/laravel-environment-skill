# Backup and restore policy

Backups are mandatory for readiness.

## Minimum standard

- Run at least daily during a low-traffic window.
- Retain at least seven daily recovery points unless the project standard requires more.
- Keep backups outside versioned release directories and outside the primary database storage.
- Separate projects/portals sufficiently that one recovery can be performed without restoring every customer.
- Encrypt off-site backups and restrict provider credentials to the required bucket/path.
- Monitor backup failures and storage capacity.

CloudPanel documents nightly backups for its supported MySQL/MariaDB databases at 03:15 with seven-day retention and remote backups through Rclone-compatible providers. Verify that the selected database is included, confirm the actual retention and last successful run, and perform an isolated restore drill. For external managed MySQL, verify the provider schedule and recovery target.

For Bitrix24 `entity.*`, define a per-portal export/restore procedure for every application-owned entity. The portal is the recovery boundary. Verify that one portal can be exported and restored without overwriting another portal's data. Platform availability alone is not an application-level backup.

## Verification

1. Record provider, schedule, retention, database/project scope, and last successful run.
2. Verify a recent nonempty artifact. Use `scripts/verify_backup_artifact.py` when accessible through the filesystem.
3. Restore into a new isolated test database or temporary test location, never over the source.
4. Run schema checks and a representative read after restore.
5. Delete the temporary restored target only after evidence is recorded.

Do not mark `restore_drill_verified` from a backup creation message alone. A restore command or provider restore operation must actually complete.
