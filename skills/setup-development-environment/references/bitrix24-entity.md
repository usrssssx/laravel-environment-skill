# Bitrix24 entity.* profile

Use Bitrix24 application storage through REST methods in the `entity.*` family. Do not present this as a SQL database or Laravel database driver.

## Architecture

- Define an application-level storage interface independent of Bitrix24 REST details.
- Implement a Bitrix24 entity adapter behind that interface.
- Keep OAuth installations and portal identity in a separate secure bootstrap registry. The application cannot fetch a token from `entity.*` when that same token is required to call `entity.*`.
- Scope every entity/list and record operation by portal.
- Centralize REST calls, retries, timeouts, rate-limit handling, redacted logging, and error translation.
- Keep cache, sessions, queues, locks, and failed jobs in infrastructure suited to those purposes; do not force them into `entity.*`.

For a single-server baseline, keep the bootstrap registry encrypted under the Laravel `APP_KEY` in persistent private shared storage outside release directories, with restrictive filesystem permissions and backups. For multiple application instances, use a shared secret store or another approved durable credential registry. Never expose OAuth tokens through public files, logs, frontend variables, or Bitrix24 business entities.

## Lifecycle

- Define installation behavior and idempotent entity creation.
- Store stable mappings between application concepts and Bitrix24 entity identifiers.
- Handle repeated installation calls safely.
- Define token refresh and invalid-token recovery.
- Define uninstall behavior explicitly: retain, anonymize, or remove application data according to the approved policy.
- Handle unavailable portals and temporary REST failures without corrupting state.

## Data modeling constraints

- Avoid assumptions about joins, relational constraints, transactions, or unrestricted queries.
- Keep records small and query patterns explicit.
- Design indexes/search keys only where supported by the actual Bitrix24 methods in use.
- Treat bulk operations, pagination, ordering, and concurrent writes as integration concerns requiring tests.
- Do not create business entities not defined by the technical specification.

## Verification

- Use contract tests against a fake adapter for normal CI.
- Run opt-in integration tests against a dedicated test portal when credentials are available.
- Verify installation, create/read/update/delete, pagination, retry behavior, portal isolation, duplicate webhook handling, token refresh, and uninstall policy.
- Never run destructive integration tests against a production portal.
