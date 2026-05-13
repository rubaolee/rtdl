from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1903_v2_partner_pod_batch_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal1903_v2_partner_pod_batch_packet_2026-05-13.md"


class Goal1903V2PartnerPodBatchPacketTest(unittest.TestCase):
    def test_runner_batches_all_current_v2_partner_perf_heads(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("RUN_FIXED_RADIUS", text)
        self.assertIn("RUN_SEGMENT_POLYGON", text)
        self.assertIn("RUN_ROAD_HAZARD", text)
        self.assertIn("goal1878_fixed_radius_app_adapter_perf.py", text)
        self.assertIn("goal1863_segment_polygon_hitcount_v2_partner_perf.py", text)
        self.assertIn("goal1897_road_hazard_prepared_reuse_pod_runner.sh", text)
        self.assertIn("REQUIRE_RTX", text)
        self.assertIn("refusing accepted pod batch on non-RTX GPU", text)
        self.assertIn("goal1903_v2_partner_pod_batch_summary.json", text)
        self.assertIn("clearing this run's target artifacts", text)
        self.assertIn("SEGMENT_POLYGON_COUNTS", text)
        self.assertIn("ROAD_HAZARD_COUNTS", text)
        self.assertIn("expected status=measurement", text)
        self.assertIn("expected status=pass", text)
        self.assertIn("strict_counts_match failed", text)
        self.assertIn("unexpectedly true", text)
        self.assertNotIn('glob("goal1903_segment_polygon_batch_pod_*.json")', text)
        self.assertIn("v2_0_release_authorized", text)
        self.assertIn("whole_app_speedup_claim_authorized", text)
        self.assertIn("broad_rt_core_speedup_claim_authorized", text)

    def test_report_lists_default_outputs_and_dry_run_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pre-pod-ready", text)
        self.assertIn("goal1903_fixed_radius_batch_pod.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_512.json", text)
        self.assertIn("goal1903_segment_polygon_batch_pod_2048.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_512.json", text)
        self.assertIn("goal1889_road_hazard_prepared_reuse_pod_2048.json", text)
        self.assertIn("REQUIRE_RTX=0", text)
        self.assertIn("must not be used for accepted RTX evidence", text)
        self.assertIn("not from a broad filesystem glob", text)
        self.assertIn("validates the requested fixed-radius", text)
        self.assertIn("scripts/goal1905_v2_partner_pod_batch_acceptance.py", text)
        self.assertIn("Shared focused tests passed: 16 tests", text)
        self.assertIn("Goal1897 nested road-hazard packet passed: 14 tests", text)
        self.assertIn("13275c462af5eadfb624b287a937d8af00d13e51", text)
        self.assertIn("batch orchestration only", text)
        self.assertIn("does not by itself authorize v2.0 release", text)


if __name__ == "__main__":
    unittest.main()
