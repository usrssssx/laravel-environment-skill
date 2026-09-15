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
