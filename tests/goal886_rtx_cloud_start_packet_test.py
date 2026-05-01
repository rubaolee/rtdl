import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal886_rtx_cloud_start_packet_2026-04-24.md"


class Goal886RtxCloudStartPacketTest(unittest.TestCase):
    def test_packet_allows_cloud_start_but_not_claims(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("Cloud can start now", text)
        self.assertIn("does not authorize public RTX speedup claims", text)
        self.assertIn("After copying artifacts back, stop or terminate the pod", text)

    def test_packet_has_active_and_deferred_commands(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("Command 1: Active Evidence Batch", text)
        self.assertIn("Command 2: Same-Pod Deferred Exploration Batch", text)
        self.assertIn("goal769_rtx_pod_one_shot.py", text)
        self.assertIn("--include-deferred", text)

    def test_packet_covers_all_deferred_targets(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        for app in (
            "graph_analytics",
            "service_coverage_gaps",
            "event_hotspot_screening",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "hausdorff_distance",
            "ann_candidate_search",
            "facility_knn_assignment",
            "barnes_hut_force_app",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            with self.subTest(app=app):
                self.assertIn(f"--only {app}", text)


if __name__ == "__main__":
    unittest.main()
