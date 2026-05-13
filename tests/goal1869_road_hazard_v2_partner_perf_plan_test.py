from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1869_road_hazard_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1869_road_hazard_v2_partner_perf_plan_2026-05-13.md"


class Goal1869RoadHazardV2PartnerPerfPlanTest(unittest.TestCase):
    def test_runner_records_dual_v1_8_baselines_and_v2_partner_path(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("road_hazard_hitcount", text)
        self.assertIn("prepare_optix_segment_polygon_hitcount_2d", text)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", text)
        self.assertIn("v1_8_one_shot_native_optix_road_hazard_rows", text)
        self.assertIn("v1_8_prepared_native_optix_road_hazard_rows", text)
        self.assertIn("v2_0_partner_road_hazard_priority_flags_", text)
        self.assertIn("query_median_ratio_vs_v1_8_one_shot_native", text)
        self.assertIn("query_median_ratio_vs_v1_8_prepared_native", text)

    def test_runner_prints_progress_and_keeps_claim_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("[setup]", text)
        self.assertIn("[timing]", text)
        self.assertIn("[artifact]", text)
        self.assertIn("flush=True", text)
        self.assertIn('"same_contract_timing_row": True', text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', text)

    def test_report_keeps_pod_timing_pending(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: ready-for-pod", report)
        self.assertIn("road_hazard_priority_flags_optix_partner_device_columns", report)
        self.assertIn("goal1869_road_hazard_v2_partner_perf_pod_512.json", report)
        self.assertIn("goal1869_road_hazard_v2_partner_perf_pod_2048.json", report)
        self.assertIn("does not contain pod timing evidence", report)
        self.assertIn("yet and does not authorize", report)
        self.assertIn("does not authorize v2.0 release wording", report)


if __name__ == "__main__":
    unittest.main()
