from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal978RtxSpeedupClaimCandidateAuditTest(unittest.TestCase):
    def test_audit_covers_all_rows_without_authorizing_public_claims(self) -> None:
        module = __import__(
            "scripts.goal978_rtx_speedup_claim_candidate_audit",
            fromlist=["build_audit"],
        )
        payload = module.build_audit()
        self.assertEqual(payload["row_count"], 17)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertEqual(payload["current_public_wording_source"], "rtdsl.rtx_public_wording_matrix()")
        self.assertGreater(payload["candidate_count"], 0)
        self.assertIn("does not authorize public speedup claims", payload["boundary"])
        for row in payload["rows"]:
            self.assertFalse(row["public_speedup_claim_authorized"])

    def test_decisions_are_conservative_for_known_rows(self) -> None:
        module = __import__(
            "scripts.goal978_rtx_speedup_claim_candidate_audit",
            fromlist=["build_audit"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_audit()["rows"]
        }

        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["recommendation"],
            "candidate_for_separate_2ai_public_claim_review",
        )
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["current_public_wording_status"],
            "public_wording_blocked",
        )
        self.assertIn(
            "100 ms",
            rows[("robot_collision_screening", "prepared_pose_flags")]["current_public_wording_boundary"],
        )
        self.assertEqual(
            rows[("database_analytics", "prepared_db_session_sales_risk")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("graph_analytics", "graph_visibility_edges_gate")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("polygon_pair_overlap_area_rows", "polygon_pair_overlap_optix_native_assisted_phase_gate")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("hausdorff_distance", "directed_threshold_prepared")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("ann_candidate_search", "candidate_threshold_prepared")]["recommendation"],
            "candidate_for_separate_2ai_public_claim_review",
        )
        self.assertEqual(
            rows[("barnes_hut_force_app", "node_coverage_prepared")]["recommendation"],
            "reject_current_public_speedup_claim",
        )
        self.assertEqual(
            rows[("outlier_detection", "prepared_fixed_radius_density_summary")]["claim_scope"],
            "prepared fixed-radius scalar threshold-count traversal only",
        )
        self.assertEqual(
            rows[("dbscan_clustering", "prepared_fixed_radius_core_flags")]["claim_scope"],
            "prepared fixed-radius scalar core-count traversal only",
        )

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal978.json"
            output_md = Path(tmpdir) / "goal978.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal978_rtx_speedup_claim_candidate_audit.py",
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
            self.assertIn("Goal978 RTX Speedup Claim Candidate Audit", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["row_count"], 17)
            self.assertIn("current public wording status", output_md.read_text(encoding="utf-8"))
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
