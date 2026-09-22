# Laravel Environment Skill

A reusable Codex skill that guides a beginner through a verified native PHP/Laravel Bitrix24 application, manual CloudPanel checkpoints, and GitHub Actions deployment without Docker.

## Capabilities

- creates a compatible stable Laravel application when the project is empty;
- creates a minimal empty application shell available only after a server-validated launch from the Bitrix24 interface;
- shows `Откройте приложение из Битрикс24` when its URL is opened directly;
- preserves compatible Laravel projects and existing architecture;
- supports MySQL or Bitrix24 `entity.*` application storage;
- configures native PHP, Composer, Node.js, Redis, Nginx, PHP-FPM, queue workers, and scheduler services;
- uses `main` for production and `test` for integration and test deployment;
- prepares GitHub Actions, immutable release archives, test deployment, health checks, and application rollback;
- starts GitHub CLI browser authorization itself when the local session is missing or expired;
- guides CloudPanel site, deploy-user, ED25519 key, and trusted TLS setup one step at a time;
- requires daily backups and a real isolated restore drill;
- requires a verified CloudPanel/external MySQL target or a live Bitrix24 `entity.*` test-portal contract;
- prevents secrets from entering Git or deployment artifacts;
- never starts a production deployment without explicit authorization.

## Install with Codex

Ask Codex to install the skill from this repository:

```text
Use $skill-installer to install the setup-development-environment skill
from https://github.com/usrssssx/laravel-environment-skill/tree/main/skills/setup-development-environment
```

Repository: <https://github.com/usrssssx/laravel-environment-skill>

After installation, restart Codex if the skill is not visible, then invoke it explicitly:

```text
Use $setup-development-environment to prepare the current project,
GitHub repository, and test deployment. Do not deploy to production.
```

The skill intentionally uses explicit invocation. It first asks for MySQL or Bitrix24 `entity.*`, prepares the local project, and then requests one manual checkpoint at a time. The user never has to provide JSON. CloudPanel browser actions remain manual; Codex verifies each result and automates GitHub and deployment only after ED25519 key access works.

For the MySQL profile, the skill asks the user to create a database in CloudPanel, accepts the generated database name, username, and password in ordinary chat, and configures Laravel with the `mysql` driver. The password is never written to project metadata, reports, or Git.

## Requirements

- Codex with local filesystem and terminal access;
- macOS or Linux with an available package manager;
- Git and SSH;
- GitHub CLI installed; the skill starts browser authentication when repository administration requires it;
- a dedicated test server and domain for real deployment verification.

External changes remain subject to Codex approvals and the permissions of the authenticated GitHub and SSH accounts.

## Repository layout

```text
skills/setup-development-environment/
|-- SKILL.md
|-- agents/openai.yaml
|-- assets/
|-- references/
`-- scripts/
```

## Safety

Test the skill with non-production infrastructure first. The generated launch gate verifies `AUTH_ID` through Bitrix24 `app.info`; iframe state, referrer headers, and launch fields alone never authorize access. Do not commit private keys, tokens, passwords, runtime `.env` files, database dumps, or production data. Report security issues according to [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
