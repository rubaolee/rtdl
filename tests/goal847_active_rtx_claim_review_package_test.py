from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal847ActiveRtxClaimReviewPackageTest(unittest.TestCase):
    def test_build_review_package_uses_green_active_gate(self) -> None:
        module = __import__("scripts.goal847_active_rtx_claim_review_package", fromlist=["build_review_package"])
        payload = module.build_review_package()
        self.assertEqual(payload["source_goal846_status"], "ok")
        self.assertEqual(payload["source_goal762_status"], "ok")
        self.assertEqual(payload["row_count"], 5)
        self.assertEqual(payload["reviewed_public_wording_count"], 2)
        self.assertEqual(payload["blocked_public_wording_count"], 1)

    def test_package_contains_robot_and_fixed_radius_phase_comparisons(self) -> None:
        module = __import__("scripts.goal847_active_rtx_claim_review_package", fromlist=["build_review_package"])
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_review_package()["rows"]
        }
        robot = rows[("robot_collision_screening", "prepared_pose_flags")]
        self.assertEqual(robot["cloud_query_metric_name"], "native_anyhit_query")
        self.assertEqual(robot["public_wording_status"], "public_wording_blocked")
        self.assertIn("100 ms", robot["public_wording_boundary"])
        self.assertEqual(len(robot["baseline_comparisons"]), 2)
        self.assertTrue(any(item["source_backend"] == "embree" for item in robot["baseline_comparisons"]))

        outlier = rows[("outlier_detection", "prepared_fixed_radius_density_summary")]
        self.assertEqual(outlier["cloud_query_metric_name"], "native_threshold_query")
        self.assertEqual(
            outlier["claim_scope"],
            "prepared fixed-radius scalar threshold-count traversal only",
        )
        self.assertEqual(outlier["public_wording_status"], "public_wording_reviewed")
        self.assertIn("not per-point outlier labels", outlier["non_claim"])
        self.assertEqual(len(outlier["baseline_comparisons"]), 2)
        self.assertTrue(any(phase["phase"] == "pack_points_sec" for phase in outlier["top_nonquery_phases"]))

        dbscan = rows[("dbscan_clustering", "prepared_fixed_radius_core_flags")]
        self.assertEqual(
            dbscan["claim_scope"],
            "prepared fixed-radius scalar core-count traversal only",
        )
        self.assertIn("not per-point core flags", dbscan["non_claim"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "review.json"
            output_md = Path(tmpdir) / "review.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal847_active_rtx_claim_review_package.py",
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
            self.assertIn("Goal847 Active RTX Claim Review Package", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["row_count"], 5)
            self.assertEqual(payload["blocked_public_wording_count"], 1)
            self.assertIn("public_wording_blocked", output_md.read_text(encoding="utf-8"))
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
