from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1060PostGoal1058SpeedupCandidateAuditTest(unittest.TestCase):
    def test_audit_classifies_goal1058_artifacts_without_authorizing_claims(self) -> None:
        module = __import__(
            "scripts.goal1060_post_goal1058_speedup_candidate_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["row_count"], 11)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

        rows = {(row["app"], row["path_name"]): row for row in payload["rows"]}
        self.assertEqual(
            rows[("facility_knn_assignment", "coverage_threshold_prepared")][
                "recommendation"
            ],
            "candidate_for_separate_2ai_public_claim_review",
        )
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")][
                "current_public_wording_status"
            ],
            "public_wording_blocked",
        )
        self.assertEqual(
            rows[("event_hotspot_screening", "prepared_count_summary")][
                "recommendation"
            ],
            "candidate_for_separate_2ai_public_claim_review",
        )
        self.assertEqual(
            rows[("database_analytics", "prepared_db_session_sales_risk")][
                "recommendation"
            ],
            "reject_current_public_speedup_claim",
        )

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1060.json"
            output_md = Path(tmpdir) / "goal1060.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1060_post_goal1058_speedup_candidate_audit.py",
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
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1060 Post-Goal1058 Speedup Candidate Audit", markdown)
            self.assertIn("public speedup claims authorized here: `0`", markdown)


if __name__ == "__main__":
    unittest.main()
