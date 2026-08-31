from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_remote_pod_validation_driver.py"
REPORT = ROOT / "docs" / "reports" / "goal4291_remote_pod_driver_noninteractive_ssh_2026-06-11.md"


class Goal4291RemotePodDriverNoninteractiveSshTest(unittest.TestCase):
    def test_dry_run_ssh_command_is_noninteractive(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--target",
                "root@example.invalid",
                "--port",
                "22022",
                "--identity-file",
                "~/.ssh/id_ed25519",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        command = " ".join(payload["command"])

        self.assertIn("BatchMode=yes", command)
        self.assertIn("StrictHostKeyChecking=accept-new", command)
        self.assertIn("ConnectTimeout=20", command)
        self.assertIn("ServerAliveInterval=30", command)
        self.assertIn("ServerAliveCountMax=4", command)
        self.assertIn("LogLevel=ERROR", command)

    def test_report_records_live_pod_trigger_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("redacted live pod endpoint", text)
        self.assertNotIn("194.68.245.114:22158", text)
        self.assertIn("host-key prompt", text)
        self.assertIn("does not run hardware validation by itself", text)


if __name__ == "__main__":
    unittest.main()
