---
name: setup-development-environment
description: Prepare and verify a complete native PHP 8.x/Laravel Bitrix24 application environment and GitHub Actions deployment pipeline without Docker. New applications include a server-validated Bitrix24 launch gate that blocks direct browser access. Use when the user asks to initialize a new project, standardize an existing Laravel workspace, choose PostgreSQL or Bitrix24 entity.* storage, configure GitHub branches and secrets, prepare a Linux server with Nginx and PHP-FPM, or set up automatic test and controlled production deployment. Do not use for ordinary feature development, Docker-based environments, or isolated CI fixes.
---

# Setup Development Environment

Prepare the environment end to end. Create files, run proportional checks, configure accessible external systems, and report actual results. Do not stop after generating documentation.

## Interaction contract

Ask at most one decision question unless the user already supplied the answer:

> Какое хранилище использовать: PostgreSQL или Bitrix24 `entity.*`?

Accept `postgres`, `postgresql`, `pg` as `postgresql`; accept `entity`, `entity.*`, `bitrix24` as `bitrix24_entity`.

Do not ask separate questions about Git, server, domain, or deployment. Discover values first, then request all missing infrastructure values once in one plain-language chat message. The user must be able to reply with ordinary prose or simple `Поле: значение` lines. Never require, show, or ask the user to edit JSON. Convert the answer into the internal `project-environment.json` yourself. Data collection is one consolidated request, not an interview. Do not ask follow-up questions field by field when the answer can be parsed reasonably.

Before ending the setup, run the configuration validator again. Unless the user explicitly requested local-only setup or declined deployment, do not issue the final completion response while the GitHub repository URL, enabled server connection data, site URL, or bootstrap SSH credential is missing. Pause with one consolidated request containing:

- GitHub repository URL;
- server IP/host, SSH port, SSH user, deployment path, and authentication method;
- public HTTPS site URL;
- SSH password when password authentication is selected.

When password authentication is selected, accept the password in the user's ordinary chat response as the transient `DEPLOY_BOOTSTRAP_PASSWORD`. Do not repeat it in later messages. Never place its value in JSON, generated Markdown, shell history, GitHub variables, GitHub Actions, `.env`, reports, or Git. Use it only to validate initial access and install a dedicated deploy public key, then configure autodeploy with `DEPLOY_SSH_KEY`.

If supplied data is invalid or still incomplete, create `setup-required-inputs.md` with exact missing paths and validation errors. Stop external setup while continuing every safe local step that does not depend on those values.

System approval prompts for external or privileged actions are not user-design questions and cannot be bypassed.

## Resource routing

Read only the references needed for the selected path:

- Always read `references/input-contract.md`, `references/workflow.md`, and `references/native-environment.md`.
- For a new application or a requested Bitrix24-only browser gate, read `references/bitrix24-browser-gate.md`.
- For PostgreSQL, read `references/postgresql.md`.
- For Bitrix24 `entity.*`, read `references/bitrix24-entity.md`.
- Before GitHub or server changes, read `references/autodeploy.md`.
- Before final reporting, read `references/verification.md`.

Use files under `assets/` as starting points. Adapt them to the inspected project; do not overwrite an existing working setup blindly.

## Phase 1: inspect

1. Run `scripts/preflight.sh <project-root>`.
2. Inspect Git status before editing. Preserve unrelated and user-owned changes.
3. Inspect `composer.json`, lock files, Laravel version, PHP constraints, frontend stack, environment examples, migrations, queues, tests, system-service configuration, and existing workflows.
4. Detect GitHub repository from `git remote get-url origin` and authentication from `gh auth status` when available.
5. Detect configuration from `project-environment.json` when present.
6. Never replace established compatible versions or architecture merely to match a template.

## Phase 2: select storage

Ask the single storage question only when the selection is absent from the user's request and config.

For `postgresql`:

- provision PostgreSQL as a native local service or use an existing reachable PostgreSQL instance;
- configure Laravel's PostgreSQL driver;
- create separate local and test databases;
- use Laravel migrations;
- document backup and restore commands.

For `bitrix24_entity`:

- do not configure it as a Laravel database driver;
- keep Laravel framework storage for cache/session/jobs separate when required;
- implement a dedicated application storage port and Bitrix24 `entity.*` adapter;
- scope records and credentials by portal;
- account for OAuth lifecycle, API limits, retries, idempotency, installation, and uninstall behavior;
- do not implement unconfirmed business entities.

## Phase 3: collect infrastructure data

1. Copy `assets/project-environment.example.json` to `project-environment.json` only if no config exists.
2. Fill values already discovered from the repository and environment.
3. Keep secrets out of this file.
4. Run `scripts/validate_config.py project-environment.json <storage-profile>`.
5. If required values are missing, use the validator output only as an internal checklist and translate it into one concise plain-text request. Do not expose its JSON response to the user.
6. Accept a bootstrap SSH password in the user's chat response when needed; treat it as transient sensitive input and never copy it into project files or reports. Obtain long-lived secrets from existing GitHub Environment Secrets, protected process environment variables, or an approved secure input channel. Never request that secrets be committed to a file.
7. If local setup finishes before infrastructure data is available, create `setup-required-inputs.md` and make the consolidated infrastructure request before stopping. Resume GitHub, server, and real test-deploy setup when the user responds.

Required external secrets normally include:

- `DEPLOY_SSH_KEY` and `DEPLOY_KNOWN_HOSTS` for each deployment environment;
- transient `DEPLOY_BOOTSTRAP_PASSWORD` when the server initially permits password authentication only;
- GitHub authentication with repository administration rights;
- Bitrix24 client credentials for `bitrix24_entity` when OAuth is needed.

## Phase 4: prepare local environment

1. For a missing application, create a stable Laravel version compatible with the available PHP 8.x runtime, then install the starter files from `assets/starter/bitrix24-browser-gate/`.
2. For an existing application, make the smallest environment-only changes.
3. Configure Blade/Vite by default. Preserve or configure Vue 3 when detected or specified.
4. Detect the operating system and available package manager. Install or configure PHP, required extensions, Composer, Node.js, PostgreSQL when selected, Redis when enabled, and local process controls without Docker.
5. Create or adapt `.env.example`, PHP settings, queue worker, scheduler, logs, and health endpoint. Use `php artisan serve` or an existing native web server for local HTTP verification; do not create Dockerfiles or Compose files.
6. Pin application dependencies and record installed runtime versions. Do not replace compatible existing runtimes unnecessarily.
7. Keep `.env`, keys, tokens, dumps, and runtime data outside Git.
8. Add basic application and health checks; preserve existing test conventions.
9. New applications must expose the configured Bitrix24 launch URL at `/bitrix24/launch`. A direct browser request to `/` or `/bitrix24/launch` must show exactly `Откройте приложение из Битрикс24`; only a launch POST whose OAuth token passes a server-side `app.info` call may create an application session.
10. Never treat iframe presence, `Referer`, request headers, `DOMAIN`, or `member_id` as proof of Bitrix24 access. Never return, log, flash, or store `AUTH_ID` or `REFRESH_ID` in a browser-accessible store.

## Phase 5: prepare Git and GitHub

1. Create and use exactly `main` for production and `test` for integration and test deployment.
2. After both branches exist, switch the working tree to `test`. Perform routine setup and development work in `test`, never directly in `main`.
3. Use `feature/*` and `fix/*` branches from `test`; merge them back into `test`. Use `hotfix/*` from `main` only when required.
4. Do not switch branches when that risks user changes.
5. Create the GitHub repository only when it does not exist and the user supplied or approved the target owner/name.
6. Configure branch protection when authenticated with sufficient rights:
   - Pull Request required for `main`;
   - at least one approval;
   - required CI checks;
   - resolved discussions;
   - no force-push or deletion;
   - successful CI and no force-push for `test`.
7. Never claim GitHub settings were applied without querying them afterward.

## Phase 6: prepare server and deployment

1. Read `references/autodeploy.md` fully.
2. Create CI, test deployment, and controlled production deployment workflows.
3. Copy and adapt the project scripts from `assets/project-scripts/`; copy `scripts/check_deploy_artifact.sh` into the target project's `scripts/check-deploy-artifact.sh` when using the release-archive templates.
4. Build an immutable release archive. Deploy the same archive to test and production; do not use container images.
5. Configure GitHub Environments `test` and `production`; require approval for production.
6. Prepare a least-privilege deploy user, Nginx, PHP-FPM, native PostgreSQL/Redis where required, systemd queue and scheduler units, known-host verification, release directories, shared storage, server `.env`, TLS, logs, backup, and health checks.
7. Push `test` only when the requested external mutation is authorized and local checks pass.
8. Run and verify a real test deployment when access exists.
9. Prepare production automation but do not trigger a real production deployment without explicit authorization.

## Phase 7: verify

Run `references/verification.md` checks and the bundled scripts. At minimum verify:

- required native runtime versions and PHP extensions;
- PostgreSQL, Redis, PHP-FPM, Nginx, queue, and scheduler service health when applicable;
- application HTTP response and health endpoint;
- direct-access gate, rejected forged launch, successful mocked Bitrix24 launch, session expiry, and frame policy;
- storage connection or Bitrix24 adapter contract tests;
- migrations for PostgreSQL;
- backend tests and frontend production build;
- queue and scheduler when enabled;
- no tracked secrets via `scripts/check_secrets.sh`;
- deploy artifact contents via `scripts/check_deploy_artifact.sh`;
- GitHub workflow result and deployed commit on test when accessible;
- application rollback on test when deployment was configured.

Fix in-scope failures and rerun the failed checks. Do not mark unexecuted checks as successful.

## Completion states

Use exactly one state:

- `READY`: local environment, GitHub pipeline, server setup, and real test deployment are verified.
- `LOCAL_READY`: local environment is verified; external setup is blocked by missing access or data.
- `FILES_READY_UNVERIFIED`: files were generated but runtime verification could not be completed.
- `BLOCKED`: a prerequisite prevents meaningful local progress.

Create `environment-setup-report.md` containing:

- selected storage profile;
- discovered and supplied configuration without secrets;
- files changed;
- commands and checks actually run;
- GitHub and server changes actually applied;
- workflow run URL/ID and deployed commit when available;
- completion state;
- exact remaining blockers.

For `LOCAL_READY`, include the exact consolidated GitHub/server request in both `setup-required-inputs.md` and the user-facing response. Do not merely list missing field names. Omit this request only when deployment was explicitly excluded by the user.

Do not say "автодеплой настроен" unless a real test deployment and external health check succeeded.
