# CloudPanel workflow

CloudPanel actions are manual checkpoints. Do not control the panel through browser automation. Give the user one action, wait, then verify the observable result.

Official documentation:

- Add a PHP site: `https://www.cloudpanel.io/docs/v2/frontend-area/add-site/`
- Site user and SSH keys: `https://www.cloudpanel.io/docs/v2/frontend-area/settings/`
- Additional restricted panel users: `https://www.cloudpanel.io/docs/v2/admin-area/users/`
- TLS certificates: `https://www.cloudpanel.io/docs/v2/frontend-area/tls/`
- Databases and built-in backups: `https://www.cloudpanel.io/docs/v2/frontend-area/databases/`
- Remote backups: `https://www.cloudpanel.io/docs/v2/admin-area/backups/`

## Site checkpoint

Ask the user to create a PHP site with the test domain and compatible PHP version. Record the generated primary site user and actual site directory. CloudPanel stores site files under the site user's home; never invent `/var/www/...` when the panel reports another path.

Verify over SSH:

- the site directory exists;
- the primary site user owns the expected site tree;
- the document root can resolve to the release symlink's `public` directory;
- PHP CLI/FPM versions are compatible;
- the project is not accidentally placed in another user's home.

## Deploy-user checkpoint

The primary site user and deploy identity are distinct responsibilities. Ask the user to create a dedicated SSH/FTP deploy user assigned only to the intended site. Propose a predictable name such as `deploy-<short-project-name>` when CloudPanel permits it.

Generate an ED25519 key outside the repository. Show only the `.pub` content and ask the user to add it under the deploy user's SSH keys. After confirmation, verify key-only login, the remote identity, the resolved site path, and narrowly scoped write access. Never add the private key to CloudPanel or show it in chat.

If CloudPanel cannot grant the additional user safe access to the existing site directory, stop. Do not silently deploy under the user's separate home directory. Resolve ownership/ACL policy with the server administrator or use the existing site user as an explicitly approved exception.

## PostgreSQL compatibility boundary

Stock CloudPanel v2 documents MySQL and MariaDB management; its database UI, `clpctl db:*`, phpMyAdmin, and built-in database backup process are not PostgreSQL management tools. Therefore:

- do not tell the user to create PostgreSQL in the CloudPanel Databases screen unless their installed/custom edition demonstrably supports it;
- prefer an external managed PostgreSQL service and record `database.management=external_managed`;
- permit native PostgreSQL on the server only after explicit user authorization and record `database.management=native_explicit`;
- never report PostgreSQL as "CloudPanel-managed" without a verified provider capability.

If the project is allowed to switch to MySQL/MariaDB, that is a new architecture decision and requires explicit user approval; this skill must not make the switch silently.

## TLS checkpoint

CloudPanel creates a self-signed certificate by default. That is not readiness. Ask the user to open the site's SSL/TLS page and create/install a Let's Encrypt certificate after DNS points to the server, or install another trusted certificate. Verify it independently with `scripts/verify_tls.py`.
