from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

from examples.current.research_benchmarks.triangle_counting import rtdl_triangle_counting_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4465_v3_0_m69_triangle_segment_planner_com_orkut_2026-06-16.md"
PLANNER_EVIDENCE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4465_v3_0_m69_triangle_segment_planner_com_orkut_2026-06-16.json"
)
APP_PROBE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4465_v3_0_m69_triangle_segmented_scene_com_orkut_probe_2026-06-16.json"
)

routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")


class Goal4465V30M69TriangleSegmentPlannerOptimizationTest(unittest.TestCase):
    def test_segment_planner_preserves_greedy_boundaries(self) -> None:
        ranges = app._segment_edge_ranges_from_counts((3, 4, 10, 1, 2), max_two_hop_rows=5)
        zero_then_oversized = app._segment_edge_ranges_from_counts((0, 0, 6), max_two_hop_rows=5)

        self.assertEqual(ranges, ((0, 1, 3), (1, 2, 4), (2, 3, 10), (3, 5, 3)))
        self.assertEqual(zero_then_oversized, ((0, 2, 0), (2, 3, 6)))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            app._segment_edge_ranges_from_counts((1, -1), max_two_hop_rows=5)

    def test_app_uses_vectorized_prefix_searchsorted_segment_planner(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("counts_prefix[1:] = np.cumsum", source)
        self.assertIn("np.searchsorted", source)
        self.assertIn("segment_rows = int(counts_prefix[end] - counts_prefix[start])", source)

    def test_com_orkut_planner_evidence_records_m69_speedup(self) -> None:
        evidence = json.loads(PLANNER_EVIDENCE.read_text(encoding="utf-8"))
        first_run = evidence["runs"][0]

        self.assertEqual(4465, evidence["goal"])
        self.assertEqual("vectorized_prefix_searchsorted_segment_planner", evidence["implementation"])
        self.assertEqual("com_orkut", evidence["dataset"])
        self.assertLess(evidence["plan_ms_median"], 4_000)
        self.assertGreater(evidence["planner_speedup_vs_goal4464_build_geometry"], 7.0)
        self.assertEqual(59, first_run["scene_count"])
        self.assertEqual(1_744, first_run["ray_segment_count"])
        self.assertEqual(117_117_316, first_run["total_directed_edges"])
        self.assertEqual(8_579_930_671, first_run["total_two_hop_rows"])

    def test_full_probe_remains_exact_after_planner_optimization(self) -> None:
        probe = json.loads(APP_PROBE.read_text(encoding="utf-8"))
        row = probe["rows"][0]

        self.assertEqual(4465, probe["goal"])
        self.assertEqual("v3_0_m69", probe["milestone"])
        self.assertEqual(627_584_181, row["observed_triangle_count"])
        self.assertTrue(row["triangle_count_matches_expected"])
        self.assertLess(row["timing_ms"]["build_geometry"], 5_000)
        self.assertLess(row["timing_ms"]["total"], 40_000)
        self.assertFalse(row["global_two_hop_summary_materialized"])
        self.assertFalse(row["global_triangle_scene_materialized"])

    def test_report_and_registries_record_m69_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        route = routes.explain_current_benchmark_route("triangle_counting")
        rows = {row["app"]: row for row in adequacy.current_benchmark_adequacy()}
        triangle = rows["triangle_counting"]

        self.assertIn("Goal4465", report)
        self.assertIn("28.885s to 3.665s", report)
        self.assertIn("not a native-engine specialization", route["user_choice_guidance"])
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4478.v1", route["version"])
        self.assertIn("Goal4465", route["evidence_refs"])
        self.assertIn("Goal4465", triangle["evidence_refs"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4478.v1", adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION)
        self.assertIn("prepared ray-batch weighted-sum API", triangle["next_generic_runtime_action"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(triangle["paper_reproduction_claim_authorized"])


if __name__ == "__main__":
    unittest.main()



