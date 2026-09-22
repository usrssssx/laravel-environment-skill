# GitHub and autodeploy

## Pipeline

- Pull Requests to `test` and `main`: run CI only.
- Push to `test`: build once, then automatically deploy the exact artifact to the test environment.
- Keep `test` as the active branch for routine development; update `main` only through Pull Requests.
- Tag or release from `main`: promote the same artifact to `production` after GitHub Environment approval.
- Never deploy arbitrary Pull Request code to production.

## Workflows

Create or adapt:

- `.github/workflows/ci.yml`
- `.github/workflows/deploy-test.yml`
- `.github/workflows/deploy-production.yml`

Use pinned major actions or immutable SHAs according to repository policy. Set minimal `permissions`, job timeouts, concurrency groups, and explicit environments.

GitHub registers a `workflow_run` listener only when that workflow file exists on the default branch. In a new repository, bootstrap the deploy workflow through a Pull Request from `test` to `main`, wait for all required checks, and obtain the required independent approval before merging. Do not use administrator bypass merely to make the first deployment start. Once the workflow is present on `main`, push a new revision to `test` and verify that CI completion triggers the deploy workflow automatically.

CI must install locked dependencies, migrate a clean test database when MySQL is selected, run backend tests, run frontend production build, and validate the deploy artifact.

## Secrets and variables

Use GitHub Environment Secrets for:

- `DEPLOY_SSH_KEY`
- application/integration secrets required only by that environment

Use environment or repository variables for:

- `DEPLOY_HOST`
- `DEPLOY_PORT`
- `DEPLOY_USER`
- `DEPLOY_PATH`
- `APP_URL`

Store `DEPLOY_KNOWN_HOSTS` as a secret or protected variable according to repository policy. Never disable host verification.

If the server initially exposes only password authentication, accept `DEPLOY_BOOTSTRAP_PASSWORD` only as a transient local setup secret. Verify the server host key out of band, connect once, install a dedicated least-privilege deploy public key, verify key-only login, then discard the password from the process environment. Never use password authentication from GitHub Actions.

For CloudPanel, the user creates the deploy identity and installs the generated public key manually. Use `generate_deploy_key.sh` and `verify_ssh_access.sh`. Configure GitHub only after key-only login succeeds. Verify that `DEPLOY_PATH` is the actual site path and not the deploy user's unrelated home directory.

## Server deployment

- Use a dedicated least-privilege deploy user.
- Use versioned immutable release archives; do not build or deploy container images.
- Install application dependencies and build frontend assets in CI before packaging.
- Run Nginx, PHP-FPM, MySQL/Redis, queue workers, and the scheduler as native server services.
- Keep runtime `.env`, persistent storage, and backups outside the release directory.
- Perform preflight checks, backup when required, migrations, cache refresh, queue restart, health checks, and log inspection.
- Write the deployed commit to a release-local `REVISION` file. The HTTP health response must expose that value, and CI must compare it with the expected workflow SHA; a generic HTTP 200 is not deployment proof.
- Keep the previous successful release available.
- Automatically revert application code when health checks fail and database compatibility permits.
- Never automatically roll back production migrations.

## Proof

Query GitHub after configuring environments, secrets metadata, workflows, and branch protection. Trigger a real test deployment, record the run ID/URL, compare both the `current` symlink and HTTP health revision with the workflow commit, run external HTTPS checks, and test application rollback on test.

Prepare production deployment but require explicit authorization before triggering it.
