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
        self.config["project"].update({"name": "demo", "frontend": "blade"})
        self.config["git"]["repository_url"] = "https://github.com/example/demo"
        self.config["server"]["test"].update({
            "host": "203.0.113.10",
            "user": "deploy-demo",
            "site_user": "demo-site",
            "path": "/home/demo-site/htdocs/test.example.com",
            "auth_method": "ssh_key",
        })
        self.config["server"]["production"]["enabled"] = False
        self.config["site"]["test_url"] = "https://test.example.com"
        self.config["database"].update({
            "management": "cloudpanel",
            "host": "127.0.0.1",
            "port": 3306,
            "name": "demo",
            "user": "demo_app",
        })
        self.config["backup"].update({"provider": "provider-snapshots", "scope": "database"})
        for checkpoint in self.config["checkpoints"]:
            self.config["checkpoints"][checkpoint] = True

    def validate(self, config, profile="mysql"):
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
            json.dump(config, handle)
            handle.flush()
            result = subprocess.run(
                ["python3", str(VALIDATOR), handle.name, profile],
                check=False,
                capture_output=True,
                text=True,
            )
        return result, json.loads(result.stdout)

    def test_complete_mysql_configuration_is_ready(self):
        result, payload = self.validate(self.config)

        self.assertEqual(0, result.returncode)
        self.assertTrue(payload["ok"])
        self.assertIsNone(payload["next_step"])
        self.assertNotIn(
            "DATABASE_PASSWORD",
            {secret["name"] for secret in payload["required_secrets"]},
        )

    def test_returns_only_the_next_manual_stage(self):
        config = copy.deepcopy(self.config)
        config["server"]["test"].update({"site_user": "", "path": ""})
        config["checkpoints"]["cloudpanel_site_created"] = False
        config["checkpoints"]["deploy_user_created"] = False

        result, payload = self.validate(config)

        self.assertEqual(1, result.returncode)
        self.assertEqual("cloudpanel_site", payload["next_step"]["id"])
        self.assertIn("server.test.site_user", payload["next_step"]["missing_fields"])
        self.assertNotIn("server.test.path", payload["next_step"]["missing_fields"])
        self.assertNotIn("server.test.user", payload["request"].get("server", {}).get("test", {}))

    def test_site_path_is_discovered_during_deploy_key_checkpoint(self):
        config = copy.deepcopy(self.config)
        config["server"]["test"]["path"] = ""
        config["checkpoints"]["deploy_public_key_installed"] = False
        config["checkpoints"]["deploy_key_login_verified"] = False

        result, payload = self.validate(config)

        self.assertEqual(1, result.returncode)
        self.assertEqual("deploy_key", payload["next_step"]["id"])
        self.assertIn("server.test.path", payload["next_step"]["missing_fields"])

    def test_rejects_native_database_management_for_mysql(self):
        self.config["database"]["management"] = "native_explicit"

        result, payload = self.validate(self.config)

        self.assertEqual(1, result.returncode)
        self.assertIn("cloudpanel or external_managed", payload["invalid"][0])

    def test_cloudpanel_mysql_requests_only_name_and_user(self):
        config = copy.deepcopy(self.config)
        config["database"].update({
            "management": "cloudpanel",
            "host": "127.0.0.1",
            "port": 3306,
            "name": "",
            "user": "",
        })
        config["checkpoints"]["database_connection_verified"] = False

        result, payload = self.validate(config)

        self.assertEqual(1, result.returncode)
        self.assertEqual("mysql", payload["next_step"]["id"])
        self.assertEqual(
            ["database.name", "database.user"],
            payload["next_step"]["missing_fields"],
        )
        self.assertNotIn("host", payload["request"]["database"])
        self.assertNotIn("port", payload["request"]["database"])

    def test_rejects_password_fields_without_echoing_secret(self):
        self.config["server"]["test"]["password"] = "do-not-echo-this"

        result, payload = self.validate(self.config)

        self.assertEqual(1, result.returncode)
        self.assertIn("server.test.password must not be stored", payload["invalid"][0])
        self.assertNotIn("do-not-echo-this", result.stdout)

    def test_entity_profile_requires_real_portal_installation_before_contract(self):
        config = copy.deepcopy(self.config)
        config["bitrix24"].update({
            "application_code": "example.demo",
            "redirect_url": "https://test.example.com/bitrix24/launch",
            "test_portal_url": "https://example.bitrix24.ru",
            "scope": ["entity"],
            "uninstall_data_policy": "delete",
        })
        config["backup"]["scope"] = "per_portal"
        config["checkpoints"]["bitrix24_test_installation_verified"] = False
        config["checkpoints"]["entity_contract_verified"] = False

        result, payload = self.validate(config, "bitrix24_entity")

        self.assertEqual(1, result.returncode)
        self.assertEqual("bitrix24_application", payload["next_step"]["id"])
        self.assertIn(
            "checkpoints.bitrix24_test_installation_verified",
            payload["next_step"]["incomplete_checkpoints"],
        )

    def test_daily_backup_retention_must_not_exceed_five_days(self):
        self.config["backup"]["retention_days"] = 7

        result, payload = self.validate(self.config)

        self.assertEqual(1, result.returncode)
        self.assertIn("from 1 to 5", payload["invalid"][0])

    def test_daily_backup_retention_accepts_one_to_five_days(self):
        for days in range(1, 6):
            with self.subTest(days=days):
                config = copy.deepcopy(self.config)
                config["backup"]["retention_days"] = days
                result, payload = self.validate(config)
                self.assertEqual(0, result.returncode)
                self.assertTrue(payload["ok"])

    def test_removed_postgresql_profile_is_rejected(self):
        result, payload = self.validate(self.config, "postgresql")

        self.assertEqual(2, result.returncode)
        self.assertIn("mysql or bitrix24_entity", payload["invalid"][0])


if __name__ == "__main__":
    unittest.main()
