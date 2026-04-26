from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal971PostGoal969BaselineSpeedupReviewPackageTest(unittest.TestCase):
    def test_package_covers_all_goal969_rtx_rows_without_speedup_overclaim(self) -> None:
        module = __import__(
            "scripts.goal971_post_goal969_baseline_speedup_review_package",
            fromlist=["build_package"],
        )
        payload = module.build_package()
        self.assertEqual(payload["row_count"], 17)
        self.assertEqual(payload["group_count"], 8)
        self.assertEqual(payload["rtx_artifact_ready_count"], 17)
        self.assertEqual(payload["bad_rtx_artifact_count"], 0)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not authorize public speedup wording", payload["boundary"])

    def test_baseline_classification_is_conservative(self) -> None:
        module = __import__(
            "scripts.goal971_post_goal969_baseline_speedup_review_package",
            fromlist=["build_package"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_package()["rows"]
        }

        self.assertEqual(
            rows[("database_analytics", "prepared_db_session_sales_risk")]["baseline_status"],
            "same_semantics_baselines_complete",
        )
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["baseline_status"],
            "same_semantics_baselines_complete",
        )
        self.assertEqual(
            rows[("outlier_detection", "prepared_fixed_radius_density_summary")]["baseline_status"],
            "same_semantics_baselines_complete",
        )
        self.assertEqual(
            rows[("dbscan_clustering", "prepared_fixed_radius_core_flags")]["baseline_status"],
            "same_semantics_baselines_complete",
        )
        self.assertEqual(
            rows[("event_hotspot_screening", "prepared_count_summary")]["baseline_status"],
            "same_semantics_baselines_complete",
        )
        self.assertEqual(
            rows[("graph_analytics", "graph_visibility_edges_gate")]["baseline_status"],
            "same_semantics_baselines_complete",
        )
        self.assertTrue(
            rows[("database_analytics", "prepared_db_session_sales_risk")][
                "baseline_complete_for_speedup_review"
            ]
        )
        self.assertFalse(
            rows[("database_analytics", "prepared_db_session_sales_risk")][
                "public_speedup_claim_authorized"
            ]
        )
        self.assertTrue(
            rows[("graph_analytics", "graph_visibility_edges_gate")][
                "baseline_complete_for_speedup_review"
            ]
        )
        self.assertFalse(
            rows[("graph_analytics", "graph_visibility_edges_gate")][
                "public_speedup_claim_authorized"
            ]
        )

    def test_fixed_radius_claim_scope_uses_current_scalar_public_terms(self) -> None:
        module = __import__(
            "scripts.goal971_post_goal969_baseline_speedup_review_package",
            fromlist=["build_package"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_package()["rows"]
        }
        outlier = rows[("outlier_detection", "prepared_fixed_radius_density_summary")]
        dbscan = rows[("dbscan_clustering", "prepared_fixed_radius_core_flags")]
        self.assertEqual(
            outlier["claim_scope"],
            "prepared fixed-radius scalar threshold-count traversal only",
        )
        self.assertIn("not per-point outlier labels", outlier["non_claim"])
        self.assertEqual(
            dbscan["claim_scope"],
            "prepared fixed-radius scalar core-count traversal only",
        )
        self.assertIn("not per-point core flags", dbscan["non_claim"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal971.json"
            output_md = Path(tmpdir) / "goal971.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal971_post_goal969_baseline_speedup_review_package.py",
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
            self.assertIn("Goal971 Post-Goal969 Baseline/Speedup Review Package", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["row_count"], 17)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
