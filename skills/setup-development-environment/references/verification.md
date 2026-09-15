# Verification checklist

Record commands and outcomes in `environment-setup-report.md`.

## Local

- Git status inspected before and after changes.
- Runtime and dependency versions match lock/config files.
- Required native tools and PHP extensions are installed at compatible versions.
- PostgreSQL, Redis, PHP-FPM, Nginx, queue, and scheduler are healthy when applicable.
- Application and health endpoint respond over HTTP.
- Selected storage profile passes its checks.
- Backend tests pass.
- Frontend production build passes.
- Queue and scheduler work when enabled.
- Logs contain no new critical failures or exposed secrets.
- `scripts/check_secrets.sh` passes.

## Artifact

- Release archive is tied to a commit SHA and checksum.
- `.git`, `.env`, keys, dumps, backups, internal specifications, and test exports are absent.
- `scripts/check_deploy_artifact.sh` passes for release archives/directories.
- Test and production workflows reference the same immutable build.

## GitHub

- CI workflow has a successful real run.
- Test environment exists.
- Production environment exists and requires approval when supported.
- Required checks and branch protection are queried after mutation.
- Workflow permissions and concurrency are explicit.
- No unresolved template markers matching `__[A-Z0-9_]+__` remain in generated project files.

## Test server

- Test workflow completed successfully.
- External HTTPS health check passed.
- Deployed revision equals the expected commit/digest.
- Storage, Redis, queue, scheduler, and logs were checked.
- Application rollback was tested without destructive database rollback.

## Reporting rule

Use `READY` only when all applicable external checks passed. Otherwise use the most accurate partial state from `SKILL.md` and enumerate blockers.
