# Native environment

Set up local and server runtimes without Docker, Compose, or container images.

## Local runtime

- Detect the operating system, architecture, shell, package manager, and already installed compatible tools before changing anything.
- Preserve compatible PHP, Composer, Node.js, PostgreSQL, Redis, and Nginx installations. Do not perform major upgrades merely to match a template.
- On macOS, prefer the available Homebrew packages and `brew services`. On Linux, use the distribution package manager and service manager. Request system approval when package installation or service mutation requires it.
- Install PHP extensions required by Laravel and the selected profile. Common extensions include bcmath, ctype, curl, dom/xml, fileinfo, intl, mbstring, openssl, pcntl, tokenizer, and zip; PostgreSQL additionally requires PDO PostgreSQL.
- Use the repository lock files for Composer and frontend dependencies.
- Use `php artisan serve` for the default local HTTP check. Reuse a working native local Nginx/PHP-FPM setup when one already exists or the user explicitly requires it.
- Bind PostgreSQL and Redis to loopback unless remote access is explicitly required and secured.
- Create separate application and test databases. Never reuse a production database for local tests.

## Linux server and CloudPanel

- When CloudPanel is present, preserve its Nginx, PHP-FPM, site users, paths, and certificate management. Do not replace panel-managed services with generic templates blindly.
- Install missing PHP extensions and Redis only after checking compatibility with the panel-managed runtime. PostgreSQL is not a stock CloudPanel-managed database.
- Do not install Node.js or Composer on the server when the release archive already contains built frontend assets and `vendor/`.
- Keep Nginx and PHP-FPM under systemd. Use the templates in `assets/server/` for the site, queue worker, scheduler service, and timer; resolve every placeholder against the inspected server.
- Use a dedicated deploy user. Grant only the narrowly scoped permissions needed for release directories and approved service reloads.
- Keep `shared/.env`, `shared/storage`, and backups outside versioned releases. Point Nginx at `<deploy-path>/current/public`.
- Validate Nginx configuration before reload. Enable and verify PHP-FPM, Nginx, queue, and scheduler units.
- Configure TLS using the server's established certificate process. Do not expose PostgreSQL or Redis publicly.
- Require the user to perform CloudPanel UI mutations manually, then verify them through SSH and external checks.

## Verification

- Record exact runtime and extension versions.
- Check PostgreSQL with `pg_isready` and a Laravel read/write transaction when selected.
- Check Redis with `redis-cli ping` and Laravel cache/queue operations when enabled.
- Run backend tests, frontend production build, queue and scheduler checks, and local HTTP health checks.
- On the test server, query systemd unit status, inspect recent logs, verify HTTPS health, confirm the deployed revision, and exercise application rollback.
