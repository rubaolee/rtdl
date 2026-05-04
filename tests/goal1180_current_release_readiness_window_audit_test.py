from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1180_current_release_readiness_window_audit as goal1180


ROOT = Path(__file__).resolve().parents[1]


class Goal1180CurrentReleaseReadinessWindowAuditTest(unittest.TestCase):
    def test_goal1177_to_goal1179_chain_is_current_and_reviewed(self) -> None:
        payload = goal1180.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["missing_files"], [])
        self.assertEqual(payload["surface_failure_count"], 0)
        self.assertEqual(payload["guardrail_failure_count"], 0)
        self.assertEqual(payload["consensus_failure_count"], 0)

    def test_current_surface_preserves_public_wording_count(self) -> None:
        payload = goal1180.build_audit()
        checked_text = "\n".join(
            (ROOT / row["path"]).read_text(encoding="utf-8")
            for row in payload["surface_rows"]
            if (ROOT / row["path"]).exists()
        )
        self.assertIn("reviewed public RTX sub-path wording rows: `12`", checked_text)
        self.assertIn("Goal1208 adds exactly one reviewed public wording row", checked_text)
        self.assertIn("Goal1177", checked_text)
        self.assertNotIn("Goal1177 authorizes public", checked_text)

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1180_current_release_readiness_window_audit.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1180 Current Release-Readiness Window Audit", markdown)
            self.assertIn("current-surface failures: `0`", markdown)


if __name__ == "__main__":
    unittest.main()
