from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4466_v3_0_m70_triangle_ray_batch_cap_tuning_com_orkut_2026-06-16.md"
SWEEP = ROOT / "docs" / "reports" / "goal4466_v3_0_m70_triangle_ray_batch_cap_planner_sweep_com_orkut_2026-06-16.json"
PROBE_10M = ROOT / "docs" / "reports" / "goal4466_v3_0_m70_triangle_segmented_scene_com_orkut_probe_10m_2026-06-16.json"
PROBE_15M = ROOT / "docs" / "reports" / "goal4466_v3_0_m70_triangle_segmented_scene_com_orkut_probe_15m_2026-06-16.json"
M69_PROBE = ROOT / "docs" / "reports" / "goal4465_v3_0_m69_triangle_segmented_scene_com_orkut_probe_2026-06-16.json"

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4466V30M70TriangleRayBatchCapTuningTest(unittest.TestCase):
    def test_planner_sweep_records_batch_count_tradeoff(self) -> None:
        sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
        rows = {row["segment_max_two_hop_rows"]: row for row in sweep["rows"]}

        self.assertEqual(4466, sweep["goal"])
        self.assertEqual("ray_batch_cap_planner_sweep", sweep["implementation"])
        self.assertEqual(1_744, rows[5_000_000]["ray_segment_count"])
        self.assertEqual(885, rows[10_000_000]["ray_segment_count"])
        self.assertEqual(456, rows[20_000_000]["ray_segment_count"])
        self.assertEqual(147, rows[80_000_000]["ray_segment_count"])
        self.assertEqual(59, rows[5_000_000]["scene_count"])

    def test_15m_probe_is_best_measured_safe_cap(self) -> None:
        m69 = json.loads(M69_PROBE.read_text(encoding="utf-8"))["rows"][0]
        ten = json.loads(PROBE_10M.read_text(encoding="utf-8"))["rows"][0]
        fifteen = json.loads(PROBE_15M.read_text(encoding="utf-8"))["rows"][0]

        self.assertEqual(627_584_181, fifteen["observed_triangle_count"])
        self.assertTrue(fifteen["triangle_count_matches_expected"])
        self.assertEqual(600, fifteen["segmentation"]["ray_segment_count"])
        self.assertEqual(15_000_000, fifteen["segmentation"]["max_two_hop_rows"])
        self.assertLess(fifteen["timing_ms"]["total"], ten["timing_ms"]["total"])
        self.assertLess(fifteen["timing_ms"]["total"], m69["timing_ms"]["total"])
        self.assertLess(fifteen["timing_ms"]["segment_ray_build_median_ms"], m69["timing_ms"]["segment_ray_build_median_ms"])

    def test_report_and_registries_keep_tuning_explicit(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("18,000,000", report)
        self.assertIn("20,000,000", report)
        self.assertIn("CUDA OOM during query", report)
        self.assertIn("not a universal default", report)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4475.v1", route["version"])
        self.assertIn("Goal4466", route["evidence_refs"])
        self.assertIn("15M", route["user_choice_guidance"])
        self.assertIn("do not auto-hide larger caps", route["user_choice_guidance"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4475.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("Goal4466", triangle["evidence_refs"])
        self.assertIn("larger tested caps unsafe", triangle["current_recommended_path"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(triangle["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()


