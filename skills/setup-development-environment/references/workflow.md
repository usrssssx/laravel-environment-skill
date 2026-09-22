# Environment workflow

## Order

1. Inspect current state and preserve user changes.
2. Resolve the storage profile using the single permitted decision question.
3. Discover Git and project values.
4. Validate `project-environment.json` and use only its `next_step`.
5. Prepare Laravel and native local runtime services.
6. Configure the selected storage profile.
7. Add tests, logs, queue, scheduler, and health checks.
8. Run all local checks.
9. Guide the user through CloudPanel site creation and verify it.
10. Generate the ED25519 deploy key first, propose the deploy username, ask the user to create that CloudPanel user with the displayed public key, then verify key-only access and site-path permissions.
11. Configure and verify PostgreSQL, or deploy and verify the Bitrix24 test-portal installation and live `entity.*` contract.
12. Guide trusted-certificate issuance and verify TLS.
13. If GitHub CLI authentication is missing or expired, start the bundled browser-auth helper in a TTY, wait for the user's browser confirmation, and verify the resulting session. Then configure GitHub Actions, secrets, environments, and repository settings.
14. Run and verify real test deployment and rollback.
15. Verify daily backup and an isolated restore drill.
16. Prepare controlled production deployment without triggering it.
17. Revalidate all checkpoints and produce the final report.

## Existing-project rule

Prefer existing compatible conventions. Do not upgrade major framework/runtime versions, replace a working deployment model, or reorganize application modules unless required to make the environment reproducible.

## New-project baseline

- PHP 8.x compatible with the selected stable Laravel release
- Laravel + Blade/Vite, or Vue 3 when requested
- native PHP, Composer, and Node.js toolchain
- Nginx + PHP-FPM
- Redis for cache/queue when enabled
- native PostgreSQL for local development when selected; server PostgreSQL is managed externally by default or explicitly administered outside CloudPanel
- systemd-managed queue and scheduler processes on Linux servers
- GitHub Actions CI
- `main` and `test` branches, with `test` active for routine development
- automatic `test` branch deployment to the test environment
- tag/release-based production workflow with environment approval

## Safe mutation rules

- Use patches for manual edits.
- Avoid destructive Git and database commands.
- Never expose database or Redis ports publicly without a documented need.
- Never generate or rotate live secrets without authorization.
- Do not run production deployment as part of setup.
- External changes require accessible credentials and may trigger platform approval.
- Start GitHub browser authentication yourself when needed. Do not hand the user a `gh auth login` command and stop; pause only for the browser confirmation that GitHub requires.
- CloudPanel browser actions remain manual. Give one action at a time and verify it before continuing.
