#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


PROFILES = {"postgresql", "bitrix24_entity"}
FIXED_VALUES = {
    "git.main_branch": "main",
    "git.test_branch": "test",
    "deployment.delivery": "release_archive",
    "control_panel.type": "cloudpanel",
    "control_panel.manual_only": True,
}


def value_at(data, dotted_path):
    value = data
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def missing_value(value):
    return value is None or value == "" or value == []


def set_path(data, dotted_path, value=""):
    cursor = data
    parts = dotted_path.split(".")
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[parts[-1]] = value


def valid_https_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def github_repository_from_url(value):
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    try:
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2:
        return None
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    candidate = f"{owner}/{repository}"
    return candidate if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", candidate) else None


def forbidden_secret_paths(value, prefix=""):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key.lower() in {
                "password",
                "ssh_password",
                "server_password",
                "database_password",
                "deploy_bootstrap_password",
                "private_key",
            }:
                found.append(path)
            found.extend(forbidden_secret_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_secret_paths(child, f"{prefix}[{index}]"))
    return found


def stage_definitions(profile, production_enabled):
    stages = [
        {"id": "project", "fields": ["project.name", "project.frontend"], "checkpoints": []},
        {"id": "github", "fields": ["git.repository_url"], "checkpoints": []},
        {
            "id": "cloudpanel_site",
            "fields": [
                "server.test.host",
                "server.test.port",
                "server.test.site_user",
                "server.test.path",
                "site.test_url",
            ],
            "checkpoints": ["checkpoints.cloudpanel_site_created"],
        },
        {
            "id": "deploy_user",
            "fields": ["server.test.user", "server.test.auth_method"],
            "checkpoints": ["checkpoints.deploy_user_created"],
        },
        {
            "id": "deploy_key",
            "fields": [],
            "checkpoints": [
                "checkpoints.deploy_public_key_installed",
                "checkpoints.deploy_key_login_verified",
            ],
        },
    ]
    if profile == "postgresql":
        stages.append({
            "id": "postgresql",
            "fields": [
                "database.management",
                "database.host",
                "database.port",
                "database.name",
                "database.user",
            ],
            "checkpoints": ["checkpoints.database_connection_verified"],
        })
    else:
        stages.extend([
            {
                "id": "bitrix24_application",
                "fields": [
                    "bitrix24.application_code",
                    "bitrix24.redirect_url",
                    "bitrix24.test_portal_url",
                    "bitrix24.scope",
                    "bitrix24.uninstall_data_policy",
                ],
                "checkpoints": ["checkpoints.bitrix24_test_installation_verified"],
            },
            {
                "id": "entity_contract",
                "fields": [],
                "checkpoints": ["checkpoints.entity_contract_verified"],
            },
        ])
    stages.extend([
        {"id": "tls", "fields": [], "checkpoints": ["checkpoints.tls_verified"]},
        {
            "id": "backup_restore",
            "fields": [
                "backup.provider",
                "backup.scope",
                "backup.schedule",
                "backup.retention_days",
            ],
            "checkpoints": ["checkpoints.backup_created", "checkpoints.restore_drill_verified"],
        },
        {
            "id": "test_deployment",
            "fields": [],
            "checkpoints": ["checkpoints.test_deployment_verified"],
        },
    ])
    if production_enabled:
        stages.append({
            "id": "production_configuration",
            "fields": [
                "server.production.host",
                "server.production.port",
                "server.production.user",
                "server.production.path",
                "server.production.auth_method",
                "site.production_url",
            ],
            "checkpoints": [],
        })
    return stages


def validate(data, profile):
    invalid = []
    repository = value_at(data, "git.repository")
    repository_url = value_at(data, "git.repository_url")

    if repository and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(repository)):
        invalid.append("git.repository must use owner/repository format")
    repository_from_url = github_repository_from_url(repository_url) if repository_url else None
    if repository_url and repository_from_url is None:
        invalid.append("git.repository_url must use https://github.com/owner/repository format")
    if repository and repository_from_url and repository != repository_from_url:
        invalid.append("git.repository and git.repository_url must identify the same repository")

    frontend = value_at(data, "project.frontend")
    if frontend not in {None, "", "blade", "vue3"}:
        invalid.append("project.frontend must be blade or vue3")

    for field, expected in FIXED_VALUES.items():
        value = value_at(data, field)
        if value not in {None, "", expected}:
            invalid.append(f"{field} must be {str(expected).lower()}")

    for field in ["server.test.port", "server.production.port", "database.port"]:
        value = value_at(data, field)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 65535):
            invalid.append(f"{field} must be an integer from 1 to 65535")

    for field in ["server.test.path", "server.production.path"]:
        value = value_at(data, field)
        if value and not str(value).startswith("/"):
            invalid.append(f"{field} must be an absolute path")

    for field in ["server.test.auth_method", "server.production.auth_method"]:
        value = value_at(data, field)
        if value not in {None, "", "password", "ssh_key"}:
            invalid.append(f"{field} must be password or ssh_key")

    for field in ["site.test_url", "site.production_url", "bitrix24.redirect_url", "bitrix24.test_portal_url"]:
        value = value_at(data, field)
        if value and not valid_https_url(value):
            invalid.append(f"{field} must be an https URL")

    management = value_at(data, "database.management")
    if profile == "postgresql" and management not in {None, "", "external_managed", "native_explicit"}:
        invalid.append(
            "database.management must be external_managed or native_explicit; stock CloudPanel does not manage PostgreSQL"
        )
    schedule = value_at(data, "backup.schedule")
    if schedule not in {None, "", "daily"}:
        invalid.append("backup.schedule must be daily")
    retention = value_at(data, "backup.retention_days")
    if retention is not None:
        if not isinstance(retention, int) or isinstance(retention, bool) or retention < 7:
            invalid.append("backup.retention_days must be an integer of at least 7")
    scope = value_at(data, "backup.scope")
    expected_scope = "database" if profile == "postgresql" else "per_portal"
    if scope not in {None, "", expected_scope}:
        invalid.append(f"backup.scope must be {expected_scope} for {profile}")

    policy = value_at(data, "bitrix24.uninstall_data_policy")
    if profile == "bitrix24_entity" and policy not in {None, "", "retain", "anonymize", "delete"}:
        invalid.append("bitrix24.uninstall_data_policy must be retain, anonymize, or delete")

    for secret_path in forbidden_secret_paths(data):
        invalid.append(f"{secret_path} must not be stored in project-environment.json")

    stages = stage_definitions(profile, value_at(data, "server.production.enabled") is True)
    all_fields = []
    all_checkpoints = []
    next_step = None
    request = {}

    for stage in stages:
        stage_missing = [field for field in stage["fields"] if missing_value(value_at(data, field))]
        stage_incomplete = [field for field in stage["checkpoints"] if value_at(data, field) is not True]
        all_fields.extend(stage_missing)
        all_checkpoints.extend(stage_incomplete)
        if next_step is None and (stage_missing or stage_incomplete):
            next_step = {
                "id": stage["id"],
                "missing_fields": stage_missing,
                "incomplete_checkpoints": stage_incomplete,
            }
            for field in stage_missing:
                set_path(request, field, 22 if field.endswith(".port") else "")

    for field, expected in FIXED_VALUES.items():
        if value_at(data, field) != expected:
            all_fields.append(field)
            if next_step is None:
                next_step = {
                    "id": "fixed_configuration",
                    "missing_fields": [field],
                    "incomplete_checkpoints": [],
                }
                set_path(request, field, expected)

    required_secrets = [
        {"environment": "test", "name": "DEPLOY_SSH_KEY"},
        {"environment": "test", "name": "DEPLOY_KNOWN_HOSTS"},
    ]
    if value_at(data, "server.test.auth_method") in {None, "", "password"}:
        required_secrets.append({
            "environment": "test",
            "name": "DEPLOY_BOOTSTRAP_PASSWORD",
            "handling": "transient_only",
        })
    if profile == "postgresql":
        required_secrets.append({"environment": "test", "name": "DATABASE_PASSWORD"})
    else:
        required_secrets.extend([
            {"environment": "test", "name": "BITRIX24_CLIENT_ID"},
            {"environment": "test", "name": "BITRIX24_CLIENT_SECRET"},
        ])
    if value_at(data, "server.production.enabled") is True:
        required_secrets.extend([
            {"environment": "production", "name": "DEPLOY_SSH_KEY"},
            {"environment": "production", "name": "DEPLOY_KNOWN_HOSTS"},
        ])
        if value_at(data, "server.production.auth_method") in {None, "", "password"}:
            required_secrets.append({
                "environment": "production",
                "name": "DEPLOY_BOOTSTRAP_PASSWORD",
                "handling": "transient_only",
            })
        if profile == "postgresql":
            required_secrets.append({"environment": "production", "name": "DATABASE_PASSWORD"})
        else:
            required_secrets.extend([
                {"environment": "production", "name": "BITRIX24_CLIENT_ID"},
                {"environment": "production", "name": "BITRIX24_CLIENT_SECRET"},
            ])

    ok = not all_fields and not all_checkpoints and not invalid
    return {
        "ok": ok,
        "storage_profile": profile,
        "missing": list(dict.fromkeys(all_fields)),
        "incomplete_checkpoints": list(dict.fromkeys(all_checkpoints)),
        "invalid": invalid,
        "next_step": next_step,
        "request": request,
        "required_secrets": required_secrets,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: validate_config.py <project-environment.json> <postgresql|bitrix24_entity>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    profile = sys.argv[2].lower()
    if profile not in PROFILES:
        print(json.dumps({"ok": False, "invalid": ["storage profile must be postgresql or bitrix24_entity"]}, ensure_ascii=False, indent=2))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(json.dumps({"ok": False, "missing_file": str(path)}, ensure_ascii=False, indent=2))
        return 2
    except json.JSONDecodeError as error:
        print(json.dumps({"ok": False, "invalid_json": f"line {error.lineno}, column {error.colno}: {error.msg}"}, ensure_ascii=False, indent=2))
        return 2

    result = validate(data, profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
