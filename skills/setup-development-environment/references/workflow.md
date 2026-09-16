# Environment workflow

## Order

1. Inspect current state and preserve user changes.
2. Resolve the storage profile using the single permitted decision question.
3. Discover Git and project values.
4. Validate `project-environment.json` and collect missing infrastructure data once.
5. Prepare Laravel and native local runtime services.
6. Configure the selected storage profile.
7. Add tests, logs, queue, scheduler, and health checks.
8. Run all local checks.
9. Prepare GitHub Actions and repository settings.
10. Prepare the test server.
11. Configure GitHub Secrets and Environments through authenticated tooling.
12. Run a real test deployment and verify it.
13. Prepare controlled production deployment without triggering it.
14. Revalidate the GitHub URL, enabled server data, site URL, and bootstrap credential. If any are missing and deployment was not excluded, request them in one block and pause.
15. Produce the final report only after external setup is completed or the user explicitly limits the task to local setup.

## Existing-project rule

Prefer existing compatible conventions. Do not upgrade major framework/runtime versions, replace a working deployment model, or reorganize application modules unless required to make the environment reproducible.

## New-project baseline

- PHP 8.x compatible with the selected stable Laravel release
- Laravel + Blade/Vite, or Vue 3 when requested
- native PHP, Composer, and Node.js toolchain
- Nginx + PHP-FPM
- Redis for cache/queue when enabled
- native PostgreSQL when selected
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
