from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3531_barnes_hut_p0_recovery_investigation_2026-06-05.md"
COLD = ROOT / "docs" / "reports" / "goal3531_barnes_hut_p0_focus_a5000" / "summary.json"
WARM = ROOT / "docs" / "reports" / "goal3531_barnes_hut_p0_warm_probe_a5000" / "summary.json"


class Goal3531BarnesHutP0RecoveryInvestigationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = REPORT.read_text(encoding="utf-8")
        self.lowered = self.report.lower()
        self.normalized_lowered = " ".join(self.lowered.split())
        self.cold = json.loads(COLD.read_text(encoding="utf-8"))
        self.warm = json.loads(WARM.read_text(encoding="utf-8"))

    def _ratio(self, payload: dict, body_count: int, key: str) -> float:
        row = next(item for item in payload["ratios"] if int(item["body_count"]) == body_count)
        return float(row[key])

    def test_report_records_source_artifacts_and_pod_metadata(self) -> None:
        self.assertIn("goal3531_barnes_hut_p0_focus_a5000/summary.json", self.report)
        self.assertIn("goal3531_barnes_hut_p0_warm_probe_a5000/summary.json", self.report)
        self.assertIn("root@69.30.85.203 -p 22057", self.report)
        self.assertIn("id_ed25519_rtdl_codex", self.report)
        self.assertIn("NVIDIA RTX A5000", self.report)

    def test_cold_one_shot_still_exposes_small_scale_regression(self) -> None:
        cold_8192 = self._ratio(self.cold, 8192, "v28_speedup_vs_v23")
        cold_32768 = self._ratio(self.cold, 32768, "v28_speedup_vs_v23")
        self.assertLess(cold_8192, 0.50)
        self.assertGreaterEqual(cold_32768, 0.95)
        self.assertIn("small-scale one-shot regression remains", self.report)

    def test_warm_prepared_query_recovers_both_scales(self) -> None:
        warm_8192 = self._ratio(self.warm, 8192, "v28_speedup_vs_v23_warm")
        warm_32768 = self._ratio(self.warm, 32768, "v28_speedup_vs_v23_warm")
        self.assertGreaterEqual(warm_8192, 0.95)
        self.assertGreaterEqual(warm_32768, 0.95)
        self.assertIn("0.983x", self.report)
        self.assertIn("1.015x", self.report)
        self.assertIn("recovered", self.report)

    def test_static_route_stays_generic_and_app_agnostic(self) -> None:
        self.assertIn("run_generic_prepared_fixed_radius_threshold_reached_count_2d", self.report)
        self.assertIn("PreparedOptixFixedRadiusCountThreshold2D.count_threshold_reached", self.report)
        self.assertIn("rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d", self.report)
        self.assertIn("generic prepared scalar primitive", self.normalized_lowered)
        self.assertIn("app-specific native-engine behavior", self.report)

    def test_engineering_decision_keeps_diagnostic_and_promoted_lanes_separate(self) -> None:
        self.assertIn("Same-runner diagnostic lane", self.report)
        self.assertIn("Promoted v2.8 lane", self.report)
        self.assertIn("warm/repeated prepared-query timing", self.report)
        self.assertIn("Do not use the old one-shot 8192 process metric", self.report)

    def test_claim_boundary_flags_remain_false(self) -> None:
        for payload in (self.cold, self.warm):
            boundary = payload["claim_boundary"]
            self.assertTrue(boundary["internal_investigation_only"])
            for key in (
                "public_speedup_claim_authorized",
                "v2_8_release_authorized",
                "whole_app_speedup_claim_authorized",
                "rt_core_speedup_claim_authorized",
                "paper_reproduction_claim_authorized",
                "true_zero_copy_claim_authorized",
            ):
                self.assertFalse(boundary[key])
        self.assertIn("does not authorize", self.lowered)


if __name__ == "__main__":
    unittest.main()
