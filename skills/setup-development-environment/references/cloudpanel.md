# CloudPanel workflow

CloudPanel actions are manual checkpoints. Do not control the panel through browser automation. Give the user one action, wait, then verify the observable result.

Always show this user-provided instruction link first when asking the user to create or configure a CloudPanel site:

- `https://delovayasreda.bitrix24.ru/mobile/marketplace/?id=277&base_id=15&scope=internal&node=419`

The page may require the user's existing Bitrix24 authorization. Do not attempt to reproduce or guess its private contents. Keep the official CloudPanel links below as secondary technical references.

Official documentation:

- Add a PHP site: `https://www.cloudpanel.io/docs/v2/frontend-area/add-site/`
- Site user and SSH keys: `https://www.cloudpanel.io/docs/v2/frontend-area/settings/`
- Additional restricted panel users: `https://www.cloudpanel.io/docs/v2/admin-area/users/`
- TLS certificates: `https://www.cloudpanel.io/docs/v2/frontend-area/tls/`
- Databases and built-in backups: `https://www.cloudpanel.io/docs/v2/frontend-area/databases/`
- Remote backups: `https://www.cloudpanel.io/docs/v2/admin-area/backups/`

## Site checkpoint

Show the user-provided Bitrix24 instruction link above, then ask the user to create a PHP site with the test domain and compatible PHP version. Ask only for the server host, generated primary site user, and test URL. Do not ask the user to find or type the site directory.

After the deploy public key is installed, derive the domain from the verified test URL and run `scripts/discover_cloudpanel_site_path.sh`. Store its verified result as `server.test.path`; never invent `/var/www/...` or assume the deploy user's home. Then verify over SSH:

- the site directory exists;
- the primary site user owns the expected site tree;
- the document root can resolve to the release symlink's `public` directory;
- PHP CLI/FPM versions are compatible;
- the project is not accidentally placed in another user's home.

## Deploy-user checkpoint

The primary site user and deploy identity are distinct responsibilities. Before asking the user to act, propose a predictable name such as `deploy-<short-project-name>` and generate a dedicated ED25519 pair outside the repository. Show only the public key. Then ask the user, in one action, to create that SSH deploy user assigned only to the intended site and add the displayed public key.

Do not ask for a password by default. Use temporary password bootstrap only when the user explicitly reports that CloudPanel cannot add the public key directly. After confirmation, verify key-only login, discover the actual site path with the bundled helper, then verify the remote identity and narrowly scoped write access. Never add the private key to CloudPanel or show it in chat.

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
