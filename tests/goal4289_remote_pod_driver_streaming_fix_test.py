from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_remote_pod_validation_driver.py"
REPORT = ROOT / "docs" / "reports" / "goal4289_remote_pod_driver_streaming_fix_2026-06-11.md"


class Goal4289RemotePodDriverStreamingFixTest(unittest.TestCase):
    def test_execute_implementation_streams_lines(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("def _execute_ssh", source)
        self.assertIn("subprocess.Popen", source)
        self.assertIn("stderr=subprocess.STDOUT", source)
        self.assertIn("for line in process.stdout", source)
        self.assertIn("stream.write(decoded)", source)
        self.assertIn("threading.Timer", source)

    def test_json_dry_run_exposes_timeout(self) -> None:
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
                "--timeout-sec",
                "123",
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
        self.assertEqual(123, payload["timeout_sec"])
        self.assertEqual("dry_run", payload["mode"])

    def test_report_records_review_driven_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4287 Claude review", text)
        self.assertIn("visible progress markers", text)
        self.assertIn("does not run pod hardware validation", text)


if __name__ == "__main__":
    unittest.main()
