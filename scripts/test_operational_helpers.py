#!/usr/bin/env python3
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / "skills" / "setup-development-environment" / "scripts"


class OperationalHelpersTest(unittest.TestCase):
    def test_deploy_key_is_generated_once_without_printing_private_material(self):
        with tempfile.TemporaryDirectory() as directory:
            key_path = Path(directory) / "deploy_key"
            command = [str(SKILL_SCRIPTS / "generate_deploy_key.sh"), str(key_path), "test-deploy"]

            first = subprocess.run(command, check=False, capture_output=True, text=True)
            second = subprocess.run(command, check=False, capture_output=True, text=True)

            self.assertEqual(0, first.returncode)
            self.assertIn("ssh-ed25519", first.stdout)
            self.assertNotIn("PRIVATE KEY", first.stdout)
            self.assertEqual(0o600, key_path.stat().st_mode & 0o777)
            self.assertNotEqual(0, second.returncode)

    def test_backup_helper_accepts_fresh_artifact_and_rejects_stale_one(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "database.sql.gz"
            artifact.write_bytes(b"x" * 2048)
            command = [
                "python3",
                str(SKILL_SCRIPTS / "verify_backup_artifact.py"),
                directory,
                "--max-age-hours",
                "24",
            ]

            fresh = subprocess.run(command, check=False, capture_output=True, text=True)
            old_time = time.time() - (48 * 3600)
            os.utime(artifact, (old_time, old_time))
            stale = subprocess.run(command, check=False, capture_output=True, text=True)

            self.assertEqual(0, fresh.returncode)
            self.assertIn("database.sql.gz", fresh.stdout)
            self.assertNotEqual(0, stale.returncode)
            self.assertIn("stale", stale.stderr)


if __name__ == "__main__":
    unittest.main()
