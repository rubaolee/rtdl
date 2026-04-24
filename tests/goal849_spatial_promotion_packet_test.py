from __future__ import annotations

import unittest

from scripts import goal849_spatial_promotion_packet as goal849


class Goal849SpatialPromotionPacketTest(unittest.TestCase):
    def test_packet_keeps_spatial_apps_partial_ready(self) -> None:
        payload = goal849.build_packet()
        self.assertTrue(payload["ready_for_local_promotion_packet"])
        self.assertFalse(payload["ready_for_rtx_claim_review_now"])
        by_app = {item["app"]: item for item in payload["apps"]}
        self.assertEqual(by_app["service_coverage_gaps"]["readiness_status"], "needs_real_rtx_artifact")
        self.assertEqual(by_app["event_hotspot_screening"]["readiness_status"], "needs_real_rtx_artifact")
        self.assertEqual(by_app["service_coverage_gaps"]["current_maturity"], "rt_core_partial_ready")
        self.assertEqual(by_app["event_hotspot_screening"]["current_maturity"], "rt_core_partial_ready")

    def test_packet_records_required_rt_core_modes(self) -> None:
        payload = goal849.build_packet()
        by_app = {item["app"]: item for item in payload["apps"]}
        self.assertEqual(by_app["service_coverage_gaps"]["require_rt_core_mode"], "gap_summary_prepared")
        self.assertEqual(by_app["event_hotspot_screening"]["require_rt_core_mode"], "count_summary_prepared")
        self.assertIn("real RTX optix-mode phase artifact", by_app["service_coverage_gaps"]["promotion_condition"])

    def test_dry_run_timings_are_present(self) -> None:
        payload = goal849.build_packet()
        for item in payload["apps"]:
            with self.subTest(app=item["app"]):
                timings = item["local_dry_run_timings_sec"]
                self.assertIn("input_build", timings)
                self.assertIn("cpu_reference_total", timings)


if __name__ == "__main__":
    unittest.main()
