#!/usr/bin/env python3
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "setup-development-environment" / "scripts" / "validate_config.py"
EXAMPLE = ROOT / "skills" / "setup-development-environment" / "assets" / "project-environment.example.json"


class ValidateConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.config["project"]["name"] = "demo"
        self.config["server"]["test"].update({
            "host": "203.0.113.10",
            "user": "deploy",
            "path": "/var/www/demo",
            "auth_method": "password",
        })
        self.config["site"]["test_url"] = "https://test.example.com"
        self.config["server"]["production"]["enabled"] = False

    def validate(self, config):
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
            json.dump(config, handle)
            handle.flush()
            result = subprocess.run(
                ["python3", str(VALIDATOR), handle.name, "postgresql"],
                check=False,
                capture_output=True,
                text=True,
            )
        return result, json.loads(result.stdout)

    def test_accepts_github_url_and_requests_transient_bootstrap_password(self):
        self.config["git"]["repository_url"] = "https://github.com/example/demo"

        result, payload = self.validate(self.config)

        self.assertEqual(0, result.returncode)
        self.assertTrue(payload["ok"])
        self.assertIn(
            {
                "environment": "test",
                "name": "DEPLOY_BOOTSTRAP_PASSWORD",
                "handling": "transient_secure_input_only",
            },
            payload["required_secrets"],
        )

    def test_keeps_owner_repository_compatibility_for_ssh_key_access(self):
        self.config["git"]["repository"] = "example/demo"
        self.config["server"]["test"]["auth_method"] = "ssh_key"

        result, payload = self.validate(self.config)

        self.assertEqual(0, result.returncode)
        self.assertTrue(payload["ok"])
        self.assertNotIn("DEPLOY_BOOTSTRAP_PASSWORD", result.stdout)

    def test_rejects_password_fields_without_echoing_the_secret(self):
        self.config["git"]["repository_url"] = "https://github.com/example/demo"
        self.config["server"]["test"]["password"] = "do-not-echo-this"

        result, payload = self.validate(self.config)

        self.assertEqual(1, result.returncode)
        self.assertFalse(payload["ok"])
        self.assertIn("server.test.password must not be stored", payload["invalid"][0])
        self.assertNotIn("do-not-echo-this", result.stdout)

    def test_missing_infrastructure_returns_one_fillable_request(self):
        config = copy.deepcopy(self.config)
        config["server"]["test"].update({"host": "", "user": "", "path": "", "auth_method": ""})

        result, payload = self.validate(config)

        self.assertEqual(1, result.returncode)
        self.assertEqual("", payload["request"]["git"]["repository_url"])
        self.assertEqual("", payload["request"]["server"]["test"]["user"])
        self.assertEqual("password", payload["request"]["server"]["test"]["auth_method"])
        self.assertIn("DEPLOY_BOOTSTRAP_PASSWORD", result.stdout)


if __name__ == "__main__":
    unittest.main()
