# Security Policy

## Reporting

Do not publish credentials, private keys, access tokens, server addresses tied to private infrastructure, or exploitable deployment details in a public issue.

Use GitHub private vulnerability reporting when it is enabled for this repository. Otherwise, contact the repository owner privately through the contact method listed on the GitHub profile.

## Scope

Security reports are especially relevant for:

- secret exposure in generated files, logs, or deployment artifacts;
- unsafe SSH host verification or key handling;
- unintended production deployment;
- command injection through configuration values;
- excessive GitHub or server permissions;
- destructive database or release operations.

Use only dedicated test infrastructure when reproducing a report.
