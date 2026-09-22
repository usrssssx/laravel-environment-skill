# Verification checklist

Record commands and outcomes in `environment-setup-report.md`.

## Local

- Git status inspected before and after changes.
- Runtime and dependency versions match lock/config files.
- Required native tools and PHP extensions are installed at compatible versions.
- PostgreSQL, Redis, PHP-FPM, Nginx, queue, and scheduler are healthy when applicable.
- Application and health endpoint respond over HTTP.
- Direct browser access shows `Откройте приложение из Битрикс24`.
- Forged launch data is rejected and a mocked valid `app.info` launch opens the empty application shell.
- The launch gate does not expose OAuth tokens and its CSP permits only the verified portal to frame an authorized response.
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

- CloudPanel PHP site exists with the expected primary site user and actual site path.
- Dedicated deploy user is restricted to the target site.
- ED25519 public key is installed; key-only SSH and scoped write access pass.
- Test workflow completed successfully.
- External HTTPS health check passed.
- Trusted TLS certificate matches the hostname, has acceptable remaining validity, and HTTP redirects to HTTPS.
- Deployed revision equals the expected commit/digest.
- Storage, Redis, queue, scheduler, and logs were checked.
- Application rollback was tested without destructive database rollback.
- A fresh daily backup exists with at least seven-day retention.
- Restore into an isolated test target completed and representative data/schema checks passed.
- For PostgreSQL, the approved target, least-privilege user, and write probe were verified.
- For `entity.*`, the app was installed on a dedicated test portal and live CRUD plus portal isolation passed.

## Reporting rule

Use `READY` only when all applicable external checks passed. Otherwise use the most accurate partial state from `SKILL.md` and enumerate blockers.
