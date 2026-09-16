# Input contract

Use `project-environment.json` for non-secret project and infrastructure data. Start from `../assets/project-environment.example.json`.

## Rules

- Discover `git.repository` and `git.repository_url` from the existing `origin` remote when possible.
- Require `git.main_branch` to be `main` and `git.test_branch` to be `test`; normalize older `dev` configurations to `test`.
- Require `deployment.delivery` to be `release_archive`; Docker-based delivery is outside this skill.
- Never store private keys, passwords, tokens, OAuth client secrets, webhook secrets, or full server `.env` contents in the JSON file.
- Treat empty strings as missing values.
- Validate with `scripts/validate_config.py`.
- Request all missing values in one consolidated JSON block.
- Do not ask the user to repeat values already detected.
- Never put a server password in the JSON block. Request only its secret name and secure delivery method.

## Required common fields

- `project.name`
- `project.frontend`: `blade` or `vue3`
- either `git.repository_url`: `https://github.com/owner/repository` or `git.repository`: `owner/repository`
- `git.main_branch`
- `git.test_branch`
- `server.test.host`, `port`, `user`, `path`, `auth_method`
- `site.test_url`
- `deployment.test_on_push`
- `deployment.production_trigger`
- `deployment.production_approval`
- `deployment.delivery`: `release_archive`

Production server and URL fields are required when production deployment is enabled.

`auth_method` is `password` or `ssh_key`. Password authentication is only for initial server bootstrap. Convert it to a dedicated deploy key before configuring GitHub Actions.

For `bitrix24_entity`, also require non-secret Bitrix24 application metadata: application code, redirect URL, requested scope, and whether uninstall removes application data. Obtain client secrets outside the file.

## Secret locations

Prefer GitHub Environment Secrets for deploy keys and environment-specific credentials. Use protected local environment variables only during setup. Keep the application runtime `.env` on the server with restrictive permissions.

When `auth_method` is `password`, request `DEPLOY_BOOTSTRAP_PASSWORD` separately through an approved secure input channel. Use it transiently to connect, verify the host key, and install the deploy public key. Do not save it as a GitHub secret because recurring deployments must use the dedicated SSH key.

## Missing-data behavior

When validation fails, write `setup-required-inputs.md` with:

1. selected storage profile;
2. missing JSON paths;
3. invalid values and accepted formats;
4. a minimal JSON subtree to complete;
5. required secret names without values;
6. safe local work already completed.

Before pausing, show the user a directly fillable block shaped like this, omitting values already discovered and disabled environments:

```json
{
  "git": {
    "repository_url": "https://github.com/owner/repository"
  },
  "server": {
    "test": {
      "host": "203.0.113.10",
      "port": 22,
      "user": "deploy",
      "path": "/var/www/application",
      "auth_method": "password"
    }
  },
  "site": {
    "test_url": "https://test.example.com"
  }
}
```

After the JSON block, request the transient `DEPLOY_BOOTSTRAP_PASSWORD` separately when `auth_method` is `password`. Never show a password field inside the JSON example.
