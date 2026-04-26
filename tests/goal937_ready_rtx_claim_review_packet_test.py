from __future__ import annotations

import unittest
from pathlib import Path

from rtdsl.app_support_matrix import READY_FOR_RTX_CLAIM_REVIEW
from rtdsl.app_support_matrix import RT_CORE_READY
from rtdsl.app_support_matrix import optix_app_benchmark_readiness_matrix
from rtdsl.app_support_matrix import rt_core_app_maturity_matrix


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal939_current_rtx_claim_review_package_2026-04-25.md"


class Goal937ReadyRtxClaimReviewPacketTest(unittest.TestCase):
    def test_packet_lists_all_current_ready_candidates(self) -> None:
        readiness = optix_app_benchmark_readiness_matrix()
        maturity = rt_core_app_maturity_matrix()
        ready = sorted(
            app
            for app, row in readiness.items()
            if row.status == READY_FOR_RTX_CLAIM_REVIEW
            and maturity[app].current_status == RT_CORE_READY
        )
        expected = sorted(
            [
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
                "service_coverage_gaps",
                "segment_polygon_anyhit_rows",
                "segment_polygon_hitcount",
            ]
        )

        self.assertEqual(ready, expected)
        text = PACKET.read_text(encoding="utf-8")
        for app in ready:
            with self.subTest(app=app):
                self.assertIn(f"`{app}`", text)

    def test_packet_keeps_release_and_speedup_boundaries(self) -> None:
        text = PACKET.read_text(encoding="utf-8")

        self.assertIn("does not authorize public speedup claims", text)
        self.assertIn("not release authorization", text)
        self.assertIn("bounded NVIDIA OptiX/RTX-backed sub-path", text)
        self.assertIn("Forbidden wording", text)
        self.assertIn("All graph/database/spatial work is RT-core accelerated", text)


if __name__ == "__main__":
    unittest.main()
