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
    def test_cloudpanel_path_helper_discovers_path_over_key_only_ssh(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            fake_ssh = fake_bin / "ssh"
            fake_ssh.write_text(
                "#!/usr/bin/env bash\n"
                "printf 'path=/home/site-user/htdocs/test.example.com\\n'\n",
                encoding="utf-8",
            )
            fake_ssh.chmod(0o755)
            key = temp / "deploy_key"
            known_hosts = temp / "known_hosts"
            key.write_text("private-test-fixture", encoding="utf-8")
            known_hosts.write_text("test.example.com ssh-ed25519 fixture", encoding="utf-8")
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"

            result = subprocess.run(
                [
                    str(SKILL_SCRIPTS / "discover_cloudpanel_site_path.sh"),
                    "test.example.com",
                    "22",
                    "deploy-demo",
                    "site-user",
                    "test.example.com",
                    str(key),
                    str(known_hosts),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(0, result.returncode)
            self.assertEqual("path=/home/site-user/htdocs/test.example.com", result.stdout.strip())

    def test_github_auth_helper_starts_web_login_and_verifies_result(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory) / "bin"
            fake_bin.mkdir()
            state = Path(directory) / "authenticated"
            calls = Path(directory) / "calls"
            fake_gh = fake_bin / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env bash\n"
                "echo \"$*\" >> \"$FAKE_GH_CALLS\"\n"
                "if [[ \"$1 $2\" == \"auth status\" ]]; then\n"
                "  [[ -f \"$FAKE_GH_STATE\" ]]\n"
                "  exit\n"
                "fi\n"
                "if [[ \"$1 $2\" == \"auth login\" ]]; then\n"
                "  touch \"$FAKE_GH_STATE\"\n"
                "  exit 0\n"
                "fi\n"
                "exit 1\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)
            env = os.environ.copy()
            env.update({
                "PATH": f"{fake_bin}:{env['PATH']}",
                "FAKE_GH_CALLS": str(calls),
                "FAKE_GH_STATE": str(state),
            })

            result = subprocess.run(
                [str(SKILL_SCRIPTS / "start_github_auth.sh")],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(0, result.returncode)
            call_log = calls.read_text(encoding="utf-8")
            self.assertIn("auth login --hostname github.com --git-protocol https --web", call_log)
            self.assertEqual(2, call_log.count("auth status --hostname github.com"))
            self.assertIn("authentication verified", result.stdout)

    def test_github_auth_helper_skips_login_when_session_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_bin = Path(directory) / "bin"
            fake_bin.mkdir()
            calls = Path(directory) / "calls"
            fake_gh = fake_bin / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env bash\n"
                "echo \"$*\" >> \"$FAKE_GH_CALLS\"\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)
            env = os.environ.copy()
            env.update({
                "PATH": f"{fake_bin}:{env['PATH']}",
                "FAKE_GH_CALLS": str(calls),
            })

            result = subprocess.run(
                [str(SKILL_SCRIPTS / "start_github_auth.sh")],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

            self.assertEqual(0, result.returncode)
            self.assertEqual("auth status --hostname github.com\n", calls.read_text(encoding="utf-8"))
            self.assertIn("already authenticated", result.stdout)

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
