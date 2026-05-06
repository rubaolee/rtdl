from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1186_current_release_readiness_after_goal1185_audit as goal1186


ROOT = Path(__file__).resolve().parents[1]


class Goal1186CurrentReleaseReadinessAfterGoal1185AuditTest(unittest.TestCase):
    def test_goal1184_goal1185_chain_is_current_and_reviewed(self) -> None:
        payload = goal1186.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["missing_files"], [])
        self.assertEqual(payload["surface_failure_count"], 0)
        self.assertEqual(payload["guardrail_failure_count"], 0)
        self.assertEqual(payload["consensus_failure_count"], 0)

    def test_current_surface_preserves_public_wording_count_and_boundary(self) -> None:
        payload = goal1186.build_audit()
        checked_text = "\n".join(
            (ROOT / row["path"]).read_text(encoding="utf-8")
            for row in payload["surface_rows"]
            if (ROOT / row["path"]).exists()
        )
        self.assertIn("Goal1184", checked_text)
        self.assertIn("external-review input only", checked_text)
        self.assertIn("Reviewed rows are bounded public sub-path wording", checked_text)
        self.assertIn("reviewed public RTX sub-path wording rows: `13`", checked_text)
        self.assertIn("Goal1208 adds exactly one reviewed public wording row", checked_text)
        self.assertNotIn("Goal1184 authorizes public", checked_text)
        self.assertNotIn("Goal1184 public speedup", checked_text)

    def test_guardrails_cover_forbidden_public_promotion(self) -> None:
        self.assertIn("Goal1184 public speedup", goal1186.FORBIDDEN_PUBLIC_SURFACE_PHRASES)
        self.assertNotIn("reviewed public RTX sub-path wording rows: `13`", goal1186.FORBIDDEN_PUBLIC_SURFACE_PHRASES)
        payload = goal1186.build_audit()
        forbidden_hits = [
            phrase
            for group in ("surface_rows", "guardrail_rows", "consensus_rows")
            for row in payload[group]
            for phrase in row["forbidden_phrases"]
        ]
        self.assertEqual(forbidden_hits, [])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1186_current_release_readiness_after_goal1185_audit.py",
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
            self.assertIn("Goal1186 Current Release-Readiness After Goal1185 Audit", markdown)
            self.assertIn("current-surface failures: `0`", markdown)
            self.assertIn("consensus failures: `0`", markdown)


if __name__ == "__main__":
    unittest.main()
