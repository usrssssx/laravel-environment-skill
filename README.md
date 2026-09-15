# Laravel Environment Skill

A reusable Codex skill that prepares and verifies a native PHP/Laravel development environment and GitHub Actions deployment pipeline without Docker.

## Capabilities

- creates a compatible stable Laravel application when the project is empty;
- preserves compatible Laravel projects and existing architecture;
- supports PostgreSQL or Bitrix24 `entity.*` application storage;
- configures native PHP, Composer, Node.js, Redis, Nginx, PHP-FPM, queue workers, and scheduler services;
- uses `main` for production and `test` for integration and test deployment;
- prepares GitHub Actions, immutable release archives, test deployment, health checks, and application rollback;
- prevents secrets from entering Git or deployment artifacts;
- never starts a production deployment without explicit authorization.

## Install with Codex

Ask Codex to install the skill from this repository:

```text
Use $skill-installer to install the setup-development-environment skill
from this GitHub repository.
```

After installation, restart Codex if the skill is not visible, then invoke it explicitly:

```text
Use $setup-development-environment to prepare the current project,
GitHub repository, and test deployment. Do not deploy to production.
```

The skill intentionally uses explicit invocation. It will first inspect the project and ask at most one architecture question: PostgreSQL or Bitrix24 `entity.*`. Missing non-secret infrastructure values are requested once as a single JSON block.

## Requirements

- Codex with local filesystem and terminal access;
- macOS or Linux with an available package manager;
- Git and SSH;
- GitHub CLI authentication for repository administration;
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

Test the skill with non-production infrastructure first. Do not commit private keys, tokens, passwords, runtime `.env` files, database dumps, or production data. Report security issues according to [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
