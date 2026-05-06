from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1185_goal1184_public_status_sync_audit as goal1185


ROOT = Path(__file__).resolve().parents[1]


class Goal1185Goal1184PublicStatusSyncAuditTest(unittest.TestCase):
    def test_current_public_status_sync_is_valid(self) -> None:
        payload = goal1185.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["public_wording_row_count_expected"], 13)
        self.assertGreaterEqual(payload["doc_count"], 8)
        self.assertEqual(payload["failing_doc_count"], 0)

    def test_audit_covers_public_docs_and_goal1184_reviews(self) -> None:
        payload = goal1185.build_audit()
        paths = {row["path"] for row in payload["rows"]}
        self.assertIn("docs/v1_0_rtx_app_status.md", paths)
        self.assertIn("docs/app_engine_support_matrix.md", paths)
        self.assertIn("docs/reports/goal1184_two_ai_consensus_2026-04-30.md", paths)
        self.assertIn("docs/reports/goal1184_claude_live_pod_intake_review_2026-04-30.md", paths)

    def test_forbidden_phrases_reject_public_speedup_promotion(self) -> None:
        self.assertIn("Goal1184 public speedup", goal1185.FORBIDDEN_PHRASES)
        self.assertIn("Goal1184 reviewed public RTX sub-path wording rows: `13`", goal1185.FORBIDDEN_PHRASES)
        payload = goal1185.build_audit()
        all_forbidden = [phrase for row in payload["rows"] for phrase in row["forbidden_phrases"]]
        self.assertEqual(all_forbidden, [])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "audit.json"
            output_md = Path(tmp) / "audit.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1185_goal1184_public_status_sync_audit.py",
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
            stdout = json.loads(result.stdout)
            self.assertTrue(stdout["valid"])
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1184", markdown)
            self.assertIn("external-review input only", markdown)
            self.assertIn("expected reviewed public wording rows: `13`", markdown)


if __name__ == "__main__":
    unittest.main()
