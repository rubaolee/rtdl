from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "reports" / "goal1038_next_rtx_ready_app_rerun_packet_2026-04-26.md"


class Goal1038NextRtxReadyAppRerunPacketTest(unittest.TestCase):
    def test_packet_targets_only_four_baseline_ready_apps(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        for app in (
            "outlier_detection",
            "dbscan_clustering",
            "service_coverage_gaps",
            "event_hotspot_screening",
        ):
            self.assertIn(app, text)
        for target in (
            "prepared_fixed_radius_density_summary",
            "prepared_fixed_radius_core_flags",
            "prepared_gap_summary",
            "prepared_count_summary",
        ):
            self.assertIn(f"--only {target}", text)
        self.assertNotIn("--only prepared_pose_flags", text)
        self.assertNotIn("--only graph_visibility_edges_gate", text)

    def test_packet_references_corrected_local_baseline_evidence(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("Goal1036 fixed", text)
        self.assertIn("goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.md", text)
        self.assertIn("all 12 CPU/Embree/SciPy rows passed", text)

    def test_packet_preserves_cost_and_claim_boundaries(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("Do not start a pod for a single app", text)
        self.assertIn("Copy these artifacts back before stopping the pod", text)
        self.assertIn("does not authorize public speedup claims", text)
        self.assertIn("phase separation", text)
        self.assertIn("repeated runs", text)


if __name__ == "__main__":
    unittest.main()
