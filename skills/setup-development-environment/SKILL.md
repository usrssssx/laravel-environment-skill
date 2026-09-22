---
name: setup-development-environment
description: Guide a beginner through a verified native PHP/Laravel Bitrix24 environment, manual CloudPanel checkpoints, and GitHub Actions deployment without Docker. New applications include a server-validated Bitrix24 launch gate. Use to initialize a project, choose MySQL or Bitrix24 entity.* storage, configure CloudPanel site access, deploy keys, TLS, backups, GitHub branches, and automatic test deployment. Do not use for ordinary feature development, Docker environments, or isolated CI fixes.
---

# Setup Development Environment

Prepare the environment end to end. Create files, run proportional checks, configure accessible external systems, and report actual results. Do not stop after generating documentation.

## Interaction contract

Start with the storage decision unless the user already supplied it:

> Какое хранилище использовать: MySQL или Bitrix24 `entity.*`?

Accept `mysql`, `mariadb`, `sql` as `mysql`; accept `entity`, `entity.*`, `bitrix24` as `bitrix24_entity`.

After local preparation, work as a guided wizard. Run `scripts/validate_config.py`, inspect `next_step`, and ask for only that step. Give one short manual CloudPanel action, wait for the user's confirmation or values, verify the result technically, record the checkpoint internally, then continue. Do not front-load all infrastructure questions.

When `next_step.id` is `deploy_user`, do not ask for a password first. Derive a predictable username such as `deploy-<short-project-name>`, generate a dedicated ED25519 key outside the repository with `scripts/generate_deploy_key.sh`, and show only the public key. Ask the user to create that CloudPanel user for the test site and add the displayed key in the same action. Use password bootstrap only as an explicit fallback when CloudPanel cannot install the key directly.

The user may answer with ordinary prose or `Поле: значение` lines. Never require, show, or ask the user to edit JSON. Convert answers into the internal `project-environment.json` yourself. Do not repeat a question when the answer can be parsed reasonably.

Do not automate CloudPanel through browser UI. Manual control-panel actions are intentionally user-owned because UI access and layouts vary. Link the relevant official instruction, describe the exact expected result, and perform command-line or HTTPS verification afterward.

When direct public-key installation is unavailable and password authentication is explicitly selected as a fallback, accept the password in the user's ordinary chat response as the transient `DEPLOY_BOOTSTRAP_PASSWORD`. Do not repeat it in later messages. Never place its value in JSON, generated Markdown, shell history, GitHub variables, GitHub Actions, `.env`, reports, or Git. Use it only to validate initial access and install a dedicated deploy public key, then configure autodeploy with `DEPLOY_SSH_KEY`.

If supplied data is invalid or still incomplete, create `setup-required-inputs.md` with exact missing paths and validation errors. Stop external setup while continuing every safe local step that does not depend on those values.

System approval prompts for external or privileged actions are not user-design questions and cannot be bypassed.

## Resource routing

Read only the references needed for the selected path:

- Always read `references/input-contract.md`, `references/workflow.md`, and `references/native-environment.md`.
- Before any CloudPanel or server step, read `references/cloudpanel.md` and `references/manual-checkpoints.md`.
- Before backup setup or final readiness, read `references/backup-policy.md`.
- For a new application or a requested Bitrix24-only browser gate, read `references/bitrix24-browser-gate.md`.
- For MySQL, read `references/mysql.md`.
- For Bitrix24 `entity.*`, read `references/bitrix24-entity.md`.
- Before GitHub or server changes, read `references/autodeploy.md`.
- Before final reporting, read `references/verification.md`.

Use files under `assets/` as starting points. Adapt them to the inspected project; do not overwrite an existing working setup blindly.

## Phase 1: inspect

1. Run `scripts/preflight.sh <project-root>`.
2. Inspect Git status before editing. Preserve unrelated and user-owned changes.
3. Inspect `composer.json`, lock files, Laravel version, PHP constraints, frontend stack, environment examples, migrations, queues, tests, system-service configuration, and existing workflows.
4. Detect GitHub repository from `git remote get-url origin` and authentication from `gh auth status` when available. When `gh` is installed but authentication is missing or invalid, start `scripts/start_github_auth.sh` yourself in a TTY and wait for browser confirmation; do not tell the user to run `gh auth login` manually.
5. Detect configuration from `project-environment.json` when present.
6. Never replace established compatible versions or architecture merely to match a template.

## Phase 2: select storage

Ask the single storage question only when the selection is absent from the user's request and config.

For `mysql`:

- use CloudPanel's database screen for the test-server database by default and record `database.management=cloudpanel`;
- infer server-local MySQL at `127.0.0.1:3306` when CloudPanel supplies only the database name, username, and password; do not ask the user for host or port;
- use an external managed MySQL-compatible host only when the user explicitly supplies or selects one;
- configure Laravel's `mysql` driver and PDO MySQL extension;
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
2. Before adding infrastructure values, ensure `project-environment.json`, `environment-setup-report.md`, and `setup-required-inputs.md` are ignored by Git and are not tracked. If a fresh project accidentally tracked empty template versions, remove only those paths from the index while preserving the local files before recording hostnames, IPs, users, paths, or URLs.
3. Fill values already discovered from the repository and environment.
   For a CloudPanel MySQL database, fill `database.management=cloudpanel`, `database.host=127.0.0.1`, and `database.port=3306` yourself. Ask the user only for the database name, username, and password; never store the password in JSON.
4. Keep secrets out of this file. Treat server hostnames, IP addresses, usernames, paths, and operational checkpoint evidence as local infrastructure metadata even though they are not passwords.
5. Run `scripts/validate_config.py project-environment.json <storage-profile>` after every completed checkpoint.
6. Translate only `next_step` into a concise plain-text instruction or question. Do not expose validator JSON.
7. Accept a bootstrap SSH password in the user's chat response when needed; treat it as transient sensitive input and never copy it into project files or reports. Obtain long-lived secrets from existing GitHub Environment Secrets, protected process environment variables, or an approved secure input channel. Never request that secrets be committed to a file.
8. When a manual checkpoint is needed, explain the action, expected result, and how it will be verified. Pause there. Resume from the saved checkpoint when the user responds.

Required external secrets normally include:

- `DEPLOY_SSH_KEY` and `DEPLOY_KNOWN_HOSTS` for each deployment environment;
- transient `DEPLOY_BOOTSTRAP_PASSWORD` when the server initially permits password authentication only;
- GitHub authentication with repository administration rights;
- Bitrix24 client credentials for `bitrix24_entity` when OAuth is needed.

## Phase 4: prepare local environment

1. For a missing application, create a stable Laravel version compatible with the available PHP 8.x runtime, then install the starter files from `assets/starter/bitrix24-browser-gate/`.
2. For an existing application, make the smallest environment-only changes.
3. Configure Blade/Vite by default. Preserve or configure Vue 3 when detected or specified.
4. Detect the operating system and available package manager. Install or configure PHP, required extensions, Composer, Node.js, MySQL when selected, Redis when enabled, and local process controls without Docker.
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
6. Before repository administration, run `gh auth status --hostname github.com`. If it fails, run `scripts/start_github_auth.sh` in an interactive terminal with TTY enabled. Tell the user only to confirm the authorization in the browser, keep the terminal session alive until it completes, and verify `gh auth status` afterward. Never request or expose a GitHub token in chat.
7. Configure branch protection when authenticated with sufficient rights:
   - Pull Request required for `main`;
   - at least one approval;
   - required CI checks;
   - resolved discussions;
   - no force-push or deletion;
   - successful CI and no force-push for `test`.
8. Never claim GitHub settings were applied without querying them afterward.

## Phase 6: prepare server and deployment

1. Read `references/cloudpanel.md`, `references/manual-checkpoints.md`, `references/backup-policy.md`, and `references/autodeploy.md` fully.
2. Ask the user to create or confirm the CloudPanel PHP site and provide only the server host, primary site user, and test URL. Do not ask the user for the absolute site path.
3. Before asking the user to create a deploy identity, choose and state a predictable name such as `deploy-<short-project-name>`. Generate a dedicated ED25519 key outside the repository with `scripts/generate_deploy_key.sh`, show only the public key, and ask the user to create that least-privilege CloudPanel user for only the intended site and add the key during the same checkpoint. After confirmation, set `auth_method=ssh_key`, verify key-only login, determine the absolute site path with `scripts/discover_cloudpanel_site_path.sh`, record it internally, and verify access and path permissions with `scripts/verify_ssh_access.sh`.
4. Do not deploy into the deploy user's home by assumption. Confirm the actual CloudPanel site path and ownership. Stop if the deploy user cannot safely write release directories under that site path.
5. Create CI, test deployment, and controlled production deployment workflows.
6. Copy and adapt the project scripts from `assets/project-scripts/`; copy `scripts/check_deploy_artifact.sh` into the target project's `scripts/check-deploy-artifact.sh` when using the release-archive templates.
7. Build an immutable release archive. Deploy the same archive to test and production; do not use container images.
8. Configure GitHub Environments and populate secrets/variables only after key-only SSH succeeds. Require approval for production.
9. Ask the user to issue a trusted certificate in CloudPanel. Verify hostname, chain, remaining validity, and HTTP-to-HTTPS redirect with `scripts/verify_tls.py`; a self-signed certificate does not pass.
10. Verify a daily backup, retention from one to five days, an accessible nonempty backup artifact, and a restore drill into an isolated test target. The retention period must never exceed five days. Use `scripts/verify_backup_artifact.py` when the artifact is filesystem-accessible.
11. Push `test` only when the requested external mutation is authorized and local checks pass. Run a real test deployment, external health check, revision comparison, and rollback test.
12. Prepare production automation but do not trigger a production deployment without explicit authorization.

## Phase 7: verify

Run `references/verification.md` checks and the bundled scripts. At minimum verify:

- required native runtime versions and PHP extensions;
- MySQL, Redis, PHP-FPM, Nginx, queue, and scheduler service health when applicable;
- application HTTP response and health endpoint;
- direct-access gate, rejected forged launch, successful mocked Bitrix24 launch, session expiry, and frame policy;
- CloudPanel or explicitly managed MySQL target and real connection, or a real Bitrix24 test-portal installation plus live `entity.*` CRUD contract;
- migrations for MySQL;
- backend tests and frontend production build;
- queue and scheduler when enabled;
- no tracked secrets via `scripts/check_secrets.sh`;
- deploy artifact contents via `scripts/check_deploy_artifact.sh`;
- GitHub workflow result and deployed commit on test when accessible;
- application rollback on test when deployment was configured;
- CloudPanel site path, separate deploy user, installed ED25519 public key, key-only login, and least-privilege write access;
- trusted TLS certificate and HTTP-to-HTTPS redirect;
- daily backup, retention, fresh artifact, and isolated restore drill.

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

For `LOCAL_READY`, include only the next required manual checkpoint in `setup-required-inputs.md` and the user-facing response. Do not overwhelm the user with all later steps. Omit it only when deployment was explicitly excluded.

Do not say "автодеплой настроен" unless a real test deployment and external health check succeeded.
