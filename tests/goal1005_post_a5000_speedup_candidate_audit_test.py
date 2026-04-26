from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1005PostA5000SpeedupCandidateAuditTest(unittest.TestCase):
    def test_audit_uses_final_a5000_v2_artifacts_without_authorizing_claims(self) -> None:
        module = __import__(
            "scripts.goal1005_post_a5000_speedup_candidate_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertTrue(payload["source_is_final_a5000_v2"])
        self.assertEqual(payload["source_commit"], "914122ecd2f2c73f6a51ec2d5b04ca3d575d5681")
        self.assertEqual(payload["row_count"], 17)
        self.assertEqual(payload["candidate_count"], 8)
        self.assertEqual(payload["internal_only_count"], 1)
        self.assertEqual(payload["reject_count"], 8)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not authorize public speedup claims", payload["boundary"])
        for row in payload["rows"]:
            self.assertFalse(row["public_speedup_claim_authorized"])

    def test_final_a5000_phase_values_replace_stale_goal969_values(self) -> None:
        module = __import__(
            "scripts.goal1005_post_a5000_speedup_candidate_audit",
            fromlist=["build_audit"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_audit()["rows"]
        }
        robot = rows[("robot_collision_screening", "prepared_pose_flags")]
        self.assertEqual(robot["rtx_phase_key"], "prepared_pose_flags_warm_query_sec.median_sec")
        self.assertAlmostEqual(robot["rtx_native_or_query_phase_sec"], 0.000493242871016264)

        graph = rows[("graph_analytics", "graph_visibility_edges_gate")]
        self.assertEqual(graph["rtx_phase_key"], "records.optix_visibility_anyhit.sec")
        self.assertAlmostEqual(graph["rtx_native_or_query_phase_sec"], 2.584184078499675)

    def test_known_decisions_are_conservative(self) -> None:
        module = __import__(
            "scripts.goal1005_post_a5000_speedup_candidate_audit",
            fromlist=["build_audit"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_audit()["rows"]
        }
        self.assertEqual(
            rows[("database_analytics", "prepared_db_session_sales_risk")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("road_hazard_screening", "road_hazard_native_summary_gate")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("event_hotspot_screening", "prepared_count_summary")]["recommendation"],
            "internal_only_margin_or_scale",
        )
        self.assertEqual(
            rows[("facility_knn_assignment", "coverage_threshold_prepared")]["recommendation"],
            "candidate_for_separate_2ai_public_claim_review",
        )

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1005.json"
            output_md = Path(tmpdir) / "goal1005.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1005_post_a5000_speedup_candidate_audit.py",
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
            self.assertIn("Goal1005 Post-A5000 Speedup Candidate Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["row_count"], 17)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
