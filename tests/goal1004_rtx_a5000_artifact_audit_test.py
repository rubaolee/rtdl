from __future__ import annotations

import unittest
from pathlib import Path

from scripts.goal1004_rtx_a5000_artifact_audit import EXPECTED_COMMIT, audit


ROOT = Path(__file__).resolve().parents[1]
CLOUD_DIR = ROOT / "docs" / "reports" / "cloud_2026_04_26"


class Goal1004RtxA5000ArtifactAuditTest(unittest.TestCase):
    def test_final_cloud_artifacts_are_complete_and_bounded(self) -> None:
        payload = audit(CLOUD_DIR)
        self.assertEqual(payload["status"], "ok", payload["failed_checks"])
        self.assertEqual(payload["result_count"], 17)
        self.assertEqual(payload["expected_commit"], EXPECTED_COMMIT)
        self.assertFalse(payload["failed_results"])
        self.assertTrue(payload["checks"]["summary_dry_run_false"])
        self.assertTrue(payload["checks"]["nvidia_smi_json_confirms_rtx_a5000"])

    def test_expected_app_set_is_preserved(self) -> None:
        payload = audit(CLOUD_DIR)
        # There are 17 manifest entries but 16 unique app names because
        # database_analytics has two prepared-session paths.
        self.assertEqual(
            set(payload["apps"]),
            {
                "ann_candidate_search",
                "barnes_hut_force_app",
                "database_analytics",
                "dbscan_clustering",
                "event_hotspot_screening",
                "facility_knn_assignment",
                "graph_analytics",
                "hausdorff_distance",
                "outlier_detection",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
                "road_hazard_screening",
                "robot_collision_screening",
                "segment_polygon_anyhit_rows",
                "segment_polygon_hitcount",
                "service_coverage_gaps",
            },
        )

    def test_boundary_does_not_authorize_speedup_claims(self) -> None:
        payload = audit(CLOUD_DIR)
        self.assertIn("does not authorize public speedup claims", payload["boundary"])
        self.assertTrue(payload["checks"]["final_report_preserves_no_speedup_boundary"])


if __name__ == "__main__":
    unittest.main()
