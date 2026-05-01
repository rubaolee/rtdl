from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1016RtxHistoricalReviewSupersessionAuditTest(unittest.TestCase):
    def test_historical_robot_candidate_mentions_are_superseded(self) -> None:
        module = __import__(
            "scripts.goal1016_rtx_historical_review_supersession_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertEqual(payload["current_public_wording_source"], "rtdsl.rtx_public_wording_matrix()")
        self.assertEqual(payload["historical_review_count"], 3)
        self.assertEqual(payload["historical_review_requires_supersession_count"], 3)
        self.assertTrue(payload["superseding_public_wording_ok"])
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        for row in payload["rows"]:
            self.assertTrue(row["mentions_robot_candidate"])
            self.assertTrue(row["requires_supersession_context"])
            self.assertEqual(row["current_public_wording_status"], "public_wording_blocked")

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1016.json"
            output_md = Path(tmpdir) / "goal1016.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1016_rtx_historical_review_supersession_audit.py",
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
            self.assertIn("Goal1016 RTX Historical Review Supersession Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["superseding_public_wording_ok"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("public_wording_blocked", markdown)
            self.assertIn("Historical candidate classifications", markdown)


if __name__ == "__main__":
    unittest.main()
