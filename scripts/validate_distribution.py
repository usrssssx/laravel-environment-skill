#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "setup-development-environment"


def fail(errors, message):
    errors.append(message)


def main():
    errors = []
    required = [
        SKILL / "SKILL.md",
        SKILL / "agents" / "openai.yaml",
        SKILL / "assets" / "project-environment.example.json",
        SKILL / "scripts" / "preflight.sh",
        SKILL / "scripts" / "validate_config.py",
        SKILL / "scripts" / "generate_deploy_key.sh",
        SKILL / "scripts" / "start_github_auth.sh",
        SKILL / "scripts" / "verify_ssh_access.sh",
        SKILL / "scripts" / "verify_postgresql.sh",
        SKILL / "scripts" / "verify_tls.py",
        SKILL / "scripts" / "verify_backup_artifact.py",
        SKILL / "references" / "cloudpanel.md",
        SKILL / "references" / "manual-checkpoints.md",
        SKILL / "references" / "backup-policy.md",
        SKILL / "references" / "bitrix24-browser-gate.md",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "bootstrap" / "app.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "routes" / "web.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "config" / "bitrix24.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "app" / "Http" / "Controllers" / "Bitrix24AppController.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "app" / "Services" / "Bitrix24" / "LaunchVerifier.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "resources" / "views" / "bitrix24" / "gate.blade.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "resources" / "views" / "bitrix24" / "app.blade.php.tpl",
        SKILL / "assets" / "starter" / "bitrix24-browser-gate" / "tests" / "Feature" / "Bitrix24BrowserGateTest.php.tpl",
    ]
    for path in required:
        if not path.is_file():
            fail(errors, f"missing required file: {path.relative_to(ROOT)}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not frontmatter:
        fail(errors, "SKILL.md has invalid frontmatter")
    else:
        metadata = frontmatter.group(1)
        if not re.search(r"^name:\s+setup-development-environment$", metadata, re.MULTILINE):
            fail(errors, "SKILL.md has an unexpected name")
        if not re.search(r"^description:\s+\S", metadata, re.MULTILINE):
            fail(errors, "SKILL.md is missing a description")

    config_path = SKILL / "assets" / "project-environment.example.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("git", {}).get("main_branch") != "main":
        fail(errors, "main branch must be main")
    if config.get("git", {}).get("test_branch") != "test":
        fail(errors, "test branch must be test")
    if config.get("deployment", {}).get("delivery") != "release_archive":
        fail(errors, "deployment delivery must be release_archive")
    if "repository_url" not in config.get("git", {}):
        fail(errors, "example config must include git.repository_url")
    for environment in ["test", "production"]:
        if "auth_method" not in config.get("server", {}).get(environment, {}):
            fail(errors, f"example config must include server.{environment}.auth_method")
    required_checkpoints = {
        "cloudpanel_site_created",
        "deploy_user_created",
        "deploy_public_key_installed",
        "deploy_key_login_verified",
        "tls_verified",
        "backup_created",
        "restore_drill_verified",
        "test_deployment_verified",
    }
    missing_checkpoints = required_checkpoints - set(config.get("checkpoints", {}))
    if missing_checkpoints:
        fail(errors, f"example config is missing checkpoints: {sorted(missing_checkpoints)}")

    input_contract = (SKILL / "references" / "input-contract.md").read_text(encoding="utf-8")
    completion_requirements = {
        "GitHub repository URL request": "git.repository_url",
        "server bootstrap password request": "DEPLOY_BOOTSTRAP_PASSWORD",
        "stepwise collection": "Request only the current validator `next_step`",
        "no user-facing JSON": "Do not ask the user for JSON",
        "agent-started GitHub authentication": "run `scripts/start_github_auth.sh` with TTY enabled",
    }
    for label, marker in completion_requirements.items():
        if marker not in input_contract:
            fail(errors, f"missing pre-completion requirement: {label}")
    if "```json" in input_contract:
        fail(errors, "input contract must not show a user-facing JSON block")

    cloudpanel_text = (SKILL / "references" / "cloudpanel.md").read_text(encoding="utf-8")
    for marker in ["Stock CloudPanel v2", "ED25519", "self-signed certificate"]:
        if marker not in cloudpanel_text:
            fail(errors, f"CloudPanel reference is missing requirement: {marker}")

    starter = SKILL / "assets" / "starter" / "bitrix24-browser-gate"
    controller_text = (starter / "app" / "Http" / "Controllers" / "Bitrix24AppController.php.tpl").read_text(encoding="utf-8")
    verifier_text = (starter / "app" / "Services" / "Bitrix24" / "LaunchVerifier.php.tpl").read_text(encoding="utf-8")
    bootstrap_text = (starter / "bootstrap" / "app.php.tpl").read_text(encoding="utf-8")
    gate_text = (starter / "resources" / "views" / "bitrix24" / "gate.blade.php.tpl").read_text(encoding="utf-8")

    security_requirements = {
        "direct-access message": (gate_text, "Откройте приложение из Битрикс24"),
        "server-side app.info verification": (verifier_text, "/rest/app.info.json"),
        "outbound redirect blocking": (verifier_text, "'allow_redirects' => false"),
        "public-address validation": (verifier_text, "FILTER_FLAG_NO_PRIV_RANGE"),
        "OAuth token excluded from session": (controller_text, "'bitrix24.context'"),
        "authorized frame policy": (controller_text, "frame-ancestors https://{$portal}"),
        "narrow CSRF exception": (bootstrap_text, "'bitrix24/launch'"),
    }
    for label, (text, marker) in security_requirements.items():
        if marker not in text:
            fail(errors, f"missing browser-gate requirement: {label}")

    session_write = re.search(
        r"session\(\)->put\('bitrix24\.context', \[(.*?)\]\);",
        controller_text,
        re.DOTALL,
    )
    if not session_write:
        fail(errors, "browser-gate session write was not found")
    elif re.search(r"AUTH_ID|REFRESH_ID|access_token|refresh_token", session_write.group(1), re.IGNORECASE):
        fail(errors, "OAuth token must not be written into the application session")

    forbidden = {
        "personal macOS path": re.compile(r"/Users/[^/]+/"),
        "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "Docker command": re.compile(r"\bdocker\s+(?:compose|build|run)\b", re.IGNORECASE),
        "Docker delivery": re.compile(r'"docker_image"'),
    }
    for path in SKILL.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in forbidden.items():
            if pattern.search(text):
                fail(errors, f"{label} found in {path.relative_to(ROOT)}")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Distribution validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
