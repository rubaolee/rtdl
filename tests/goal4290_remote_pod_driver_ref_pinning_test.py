from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_remote_pod_validation_driver.py"
RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "v2_10_remote_pod_validation_driver.md"
REPORT = ROOT / "docs" / "reports" / "goal4290_remote_pod_driver_ref_pinning_2026-06-11.md"


class Goal4290RemotePodDriverRefPinningTest(unittest.TestCase):
    def _dry_run(self, *extra: str) -> dict[str, object]:
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
                *extra,
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_default_ref_is_visible_in_dry_run(self) -> None:
        payload = self._dry_run()

        self.assertEqual("https://github.com/rubaolee/rtdl.git", payload["repo_url"])
        self.assertEqual("main", payload["ref"])
        self.assertIn("git clone --depth 1", str(payload["remote_script"]))

    def test_non_main_ref_fetches_and_detaches(self) -> None:
        payload = self._dry_run("--repo-url", "https://example.invalid/fork.git", "--ref", "v2.10")
        script = str(payload["remote_script"])

        self.assertEqual("https://example.invalid/fork.git", payload["repo_url"])
        self.assertEqual("v2.10", payload["ref"])
        self.assertIn("https://example.invalid/fork.git", script)
        self.assertIn("git fetch --depth 1 origin 'v2.10'", script)
        self.assertIn("git checkout --detach FETCH_HEAD", script)

    def test_runbook_and_report_document_ref_boundary(self) -> None:
        runbook = RUNBOOK.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("--ref main", runbook)
        self.assertIn("--repo-url", runbook)
        self.assertIn("does not move tags", report)
        self.assertIn("authorize performance claims", report)


if __name__ == "__main__":
    unittest.main()
