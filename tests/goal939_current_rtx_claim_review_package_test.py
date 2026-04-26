from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal939CurrentRtxClaimReviewPackageTest(unittest.TestCase):
    def test_package_lists_current_goal937_ready_set(self) -> None:
        module = __import__("scripts.goal939_current_rtx_claim_review_package", fromlist=["build_package"])
        payload = module.build_package()
        self.assertEqual(payload["ready_count"], 16)
        self.assertEqual(
            payload["ready_apps"],
            [
                "database_analytics",
                "graph_analytics",
                "service_coverage_gaps",
                "event_hotspot_screening",
                "facility_knn_assignment",
                "road_hazard_screening",
                "segment_polygon_hitcount",
                "segment_polygon_anyhit_rows",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
                "hausdorff_distance",
                "ann_candidate_search",
                "outlier_detection",
                "dbscan_clustering",
                "robot_collision_screening",
                "barnes_hut_force_app",
            ],
        )

    def test_held_rows_keep_only_non_nvidia_apps_out(self) -> None:
        module = __import__("scripts.goal939_current_rtx_claim_review_package", fromlist=["build_package"])
        held = {row["app"]: row for row in module.build_package()["held_rows"]}
        self.assertEqual(set(held), {"apple_rt_demo", "hiprt_ray_triangle_hitcount"})
        for app in held:
            with self.subTest(app=app):
                self.assertNotEqual(held[app]["readiness_status"], "ready_for_rtx_claim_review")

    def test_package_preserves_no_public_speedup_boundary(self) -> None:
        module = __import__("scripts.goal939_current_rtx_claim_review_package", fromlist=["build_package"])
        payload = module.build_package()
        self.assertIn("does not authorize public speedup claims", payload["boundary"])
        self.assertIn("native_continuation_active", payload["native_continuation_summary"])
        self.assertIn("RTDL accelerates the whole app", payload["forbidden_wording"])
        self.assertIn("All graph/database/spatial work is RT-core accelerated", payload["forbidden_wording"])

    def test_fixed_radius_rows_use_current_scalar_public_terms(self) -> None:
        module = __import__("scripts.goal939_current_rtx_claim_review_package", fromlist=["build_package"])
        rows = {row["app"]: row for row in module.build_package()["rows"]}
        self.assertIn("scalar threshold-count", rows["outlier_detection"]["allowed_claim"])
        self.assertIn("density_count", rows["outlier_detection"]["required_action"])
        self.assertIn("scalar core-count", rows["dbscan_clustering"]["allowed_claim"])
        self.assertIn("core_count", rows["dbscan_clustering"]["required_action"])
        self.assertNotIn("core-threshold", rows["dbscan_clustering"]["allowed_claim"])

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "package.json"
            output_md = Path(tmpdir) / "package.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal939_current_rtx_claim_review_package.py",
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
            self.assertIn("Goal939 Current RTX Claim-Review Package", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["ready_count"], 16)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
