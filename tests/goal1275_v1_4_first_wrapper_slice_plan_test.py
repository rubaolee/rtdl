from __future__ import annotations

from pathlib import Path
import unittest

from examples import rtdl_graph_analytics_app


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "reports"
    / "goal1275_v1_4_first_compatibility_wrapper_slice_plan_2026-05-05.md"
)


class Goal1275V14FirstWrapperSlicePlanTest(unittest.TestCase):
    def test_plan_selects_graph_visibility_edges_and_stays_within_v1_3_contract(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        for phrase in (
            "`graph_analytics.visibility_edges`",
            "`ANY_HIT`",
            "`COUNT_HITS`",
            "`REDUCE_INT(COUNT)`",
            "active backends: Embree and OptiX only",
            "Vulkan, HIPRT, and Apple RT remain untouched before v2.1",
            "BFS, triangle counting, shortest path, graph database",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_plan_requires_compatibility_wrapper_before_retiring_app_specific_path(self) -> None:
        text = PLAN.read_text(encoding="utf-8")

        for phrase in (
            "compatibility wrapper",
            "delegates to the existing behavior",
            "must not retire the existing app-specific OptiX summary path",
            "`optix_prepared_visibility_anyhit_count`",
            "performance-neutral or an accepted overhead is reviewed",
            "Do not expand public RTX wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_current_graph_visibility_summary_still_reports_bounded_claim_boundary(self) -> None:
        payload = rtdl_graph_analytics_app.run_app(
            "cpu_python_reference",
            "visibility_edges",
            copies=1,
            output_mode="summary",
        )
        section = payload["sections"]["visibility_edges"]

        self.assertEqual(section["summary"], {"visible_edge_count": 1, "blocked_edge_count": 3})
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("query_visibility_pair_rows_sec", section["run_phases"])
        self.assertIn("not BFS", section["boundary"])
        self.assertIn("Only visibility_edges is an OptiX", payload["honesty_boundary"])

    def test_current_optix_summary_source_contains_prepared_anyhit_count_boundary(self) -> None:
        source = (ROOT / "examples" / "rtdl_graph_analytics_app.py").read_text(encoding="utf-8")

        for phrase in (
            "prepare_optix_ray_triangle_any_hit_2d",
            "prepare_optix_rays_2d",
            "prepared_scene.count(prepared_rays)",
            "optix_prepared_visibility_anyhit_count",
            "query_anyhit_count_sec",
            "visibility_query_repeats",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
