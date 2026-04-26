from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1022HistoryReleaseDriftAuditTest(unittest.TestCase):
    def test_audit_detects_v096_history_drift_and_records_full_suite(self) -> None:
        module = __import__(
            "scripts.goal1022_history_release_drift_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["current_public_release"], "v0.9.6")
        self.assertTrue(payload["history_drift_detected"])
        self.assertTrue(payload["release_report_claims_history_catchup"])
        self.assertFalse(payload["complete_history_mentions_goal684"])
        self.assertFalse(payload["dashboard_mentions_goal684"])
        self.assertTrue(payload["refresh_context_current"])
        self.assertEqual(payload["full_suite_evidence"]["result"], "OK")
        self.assertEqual(payload["full_suite_evidence"]["tests"], 1969)
        self.assertEqual(payload["full_suite_evidence"]["skipped"], 196)

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1022.json"
            output_md = Path(tmpdir) / "goal1022.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1022_history_release_drift_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal1022 History Release Drift Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("history drift detected: `True`", markdown)
            self.assertIn("1969", markdown)
            self.assertIn("does not tag, release, or authorize public speedup claims", markdown)


if __name__ == "__main__":
    unittest.main()
