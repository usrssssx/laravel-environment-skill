#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


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
    return parsed.scheme == "https" and bool(parsed.netloc)


def main():
    if len(sys.argv) != 3:
        print("Usage: validate_config.py <project-environment.json> <postgresql|bitrix24_entity>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    profile = sys.argv[2].lower()
    if profile not in {"postgresql", "bitrix24_entity"}:
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

    required = [
        "project.name",
        "project.frontend",
        "git.repository",
        "git.main_branch",
        "git.test_branch",
        "server.test.host",
        "server.test.port",
        "server.test.user",
        "server.test.path",
        "site.test_url",
        "deployment.test_on_push",
        "deployment.production_trigger",
        "deployment.production_approval",
        "deployment.delivery",
    ]

    production_enabled = value_at(data, "server.production.enabled") is True
    if production_enabled:
        required.extend([
            "server.production.host",
            "server.production.port",
            "server.production.user",
            "server.production.path",
            "site.production_url",
        ])

    if profile == "bitrix24_entity":
        required.extend([
            "bitrix24.application_code",
            "bitrix24.redirect_url",
            "bitrix24.scope",
            "bitrix24.uninstall_data_policy",
        ])

    missing = [field for field in required if missing_value(value_at(data, field))]
    invalid = []

    frontend = value_at(data, "project.frontend")
    if frontend not in {None, "", "blade", "vue3"}:
        invalid.append("project.frontend must be blade or vue3")

    repository = value_at(data, "git.repository")
    if repository and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(repository)):
        invalid.append("git.repository must use owner/repository format")

    fixed_values = {
        "git.main_branch": "main",
        "git.test_branch": "test",
        "deployment.delivery": "release_archive",
    }
    for field, expected in fixed_values.items():
        value = value_at(data, field)
        if value not in {None, "", expected}:
            invalid.append(f"{field} must be {expected}")

    for field in ["server.test.port", "server.production.port"]:
        value = value_at(data, field)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 65535):
            invalid.append(f"{field} must be an integer from 1 to 65535")

    for field in ["server.test.path", "server.production.path"]:
        value = value_at(data, field)
        if value and not str(value).startswith("/"):
            invalid.append(f"{field} must be an absolute path")

    for field in ["site.test_url", "site.production_url"]:
        value = value_at(data, field)
        if value and not valid_https_url(value):
            invalid.append(f"{field} must be an https URL")

    trigger = value_at(data, "deployment.production_trigger")
    if trigger not in {None, "", "tag", "release", "manual"}:
        invalid.append("deployment.production_trigger must be tag, release, or manual")

    if profile == "bitrix24_entity":
        redirect_url = value_at(data, "bitrix24.redirect_url")
        if redirect_url and not valid_https_url(redirect_url):
            invalid.append("bitrix24.redirect_url must be an https URL")
        policy = value_at(data, "bitrix24.uninstall_data_policy")
        if policy not in {None, "", "retain", "anonymize", "delete"}:
            invalid.append("bitrix24.uninstall_data_policy must be retain, anonymize, or delete")

    request = {}
    for field in missing:
        default = fixed_values.get(field, 22 if field.endswith(".port") else "")
        set_path(request, field, default)
    for field, expected in fixed_values.items():
        if value_at(data, field) not in {expected}:
            set_path(request, field, expected)

    required_secrets = [
        {"environment": "test", "name": "DEPLOY_SSH_KEY"},
        {"environment": "test", "name": "DEPLOY_KNOWN_HOSTS"},
    ]
    if production_enabled:
        required_secrets.extend([
            {"environment": "production", "name": "DEPLOY_SSH_KEY"},
            {"environment": "production", "name": "DEPLOY_KNOWN_HOSTS"},
        ])
    if profile == "bitrix24_entity":
        required_secrets.extend([
            {"environment": "test", "name": "BITRIX24_CLIENT_ID"},
            {"environment": "test", "name": "BITRIX24_CLIENT_SECRET"},
        ])
        if production_enabled:
            required_secrets.extend([
                {"environment": "production", "name": "BITRIX24_CLIENT_ID"},
                {"environment": "production", "name": "BITRIX24_CLIENT_SECRET"},
            ])

    result = {
        "ok": not missing and not invalid,
        "storage_profile": profile,
        "missing": missing,
        "invalid": invalid,
        "request": request,
        "required_secrets": required_secrets,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
