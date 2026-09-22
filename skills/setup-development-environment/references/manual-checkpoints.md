# Manual checkpoint protocol

Use this protocol for every CloudPanel action.

1. State one action in plain language.
2. Provide the exact expected result and an official documentation link.
3. Ask the user to reply normally when it is done and include only values produced by that step.
4. Do not request JSON or all future infrastructure data.
5. Verify the result with SSH, GitHub API, DNS, TLS, HTTP, database, or application checks.
6. Set the corresponding internal checkpoint to `true` only after verification.
7. Run `scripts/validate_config.py` and continue with its `next_step`.

## Checkpoint order

1. `cloudpanel_site_created`: PHP site, test domain, primary site user, and actual path are known.
2. `deploy_user_created`: restricted deploy user exists and is assigned only to the target site.
3. `deploy_public_key_installed`: generated ED25519 public key was added to that user.
4. `deploy_key_login_verified`: key-only SSH succeeds and the site path is writable without broad privileges.
5. Storage checkpoint:
   - PostgreSQL: credentials target the approved service and `database_connection_verified` passes.
   - Bitrix24: application is installed on a dedicated test portal and `bitrix24_test_installation_verified` passes.
6. `entity_contract_verified` for `entity.*`: live create/read/update/delete and portal isolation checks pass.
7. `tls_verified`: trusted certificate, hostname, validity, and HTTPS redirect pass.
8. `backup_created`: a fresh nonempty backup exists under the approved backup provider.
9. `restore_drill_verified`: the backup was restored into an isolated test target and checked.
10. `test_deployment_verified`: GitHub deployed the expected test commit, health passed, and rollback was exercised.

## Evidence rule

A user's confirmation advances the conversation but is not proof by itself. Record the command, API response, artifact metadata, or external health result used to verify each checkpoint. If verification is impossible, leave the checkpoint false and use `LOCAL_READY` or `FILES_READY_UNVERIFIED`.
