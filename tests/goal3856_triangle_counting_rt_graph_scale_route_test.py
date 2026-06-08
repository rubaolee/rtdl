from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle_app,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3856_triangle_counting_rt_graph_scale_route_2026-06-08.md"
ARTIFACT = ROOT / "docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/summary.json"
STDOUT = (
    ROOT
    / "docs/reports/goal3856_triangle_counting_rt_graph_scale_a5000/outputs/"
    / "triangle_counting_optix_rt_graph_2a1_scale_default_2048.stdout.json"
)


class Goal3856TriangleCountingRtGraphScaleRouteTest(unittest.TestCase):
    def test_rt_graph_fixture_copies_preserve_oracle_count(self) -> None:
        payload = triangle_app.run_app(
            "rt_graph_2a1_generic_rt",
            fixture="degree_oriented_two_triangles",
            backend="cpu",
            detail="summary",
            repeat=2,
            warmup=1,
            rt_graph_copies=3,
        )

        self.assertEqual(payload["mode"], "rt_graph_2a1_generic_rt")
        self.assertEqual(payload["rt_graph_fixture_copies"], 3)
        self.assertEqual(payload["oracle_triangle_count"], 6)
        self.assertEqual(payload["generic_rt_weighted_triangle_count"], 6)
        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertEqual(payload["primitive_count"], 15)
        self.assertEqual(payload["ray_count"], 6)
        self.assertEqual(payload["timing_ms"]["query_repeat"], 2)
        self.assertEqual(payload["timing_ms"]["query_warmup"], 1)

    def test_scale_registry_uses_rt_graph_prepared_summary_route(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "triangle_counting")
        command = row["command"]

        self.assertEqual(row["row_id"], "triangle_counting_optix_rt_graph_2a1_scale_default_2048")
        self.assertIn("Goal3856", row["evidence_refs"])
        self.assertIn("rt_graph_2a1_generic_rt", command)
        self.assertIn("--rt-graph-copies", command)
        self.assertIn("2048", command)
        self.assertIn("--repeat", command)
        self.assertIn("--warmup", command)
        self.assertNotIn("--optix-graph-mode", command)
        self.assertNotIn("host_indexed", command)

    def test_a5000_artifact_records_prepared_generic_route(self) -> None:
        summary = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        row = summary["rows"][0]
        payload = json.loads(STDOUT.read_text(encoding="utf-8"))

        self.assertTrue(summary["all_pass"])
        self.assertEqual(row["status"], "pass")
        self.assertEqual(row["stderr_bytes"], 0)
        self.assertEqual(row["row_id"], "triangle_counting_optix_rt_graph_2a1_scale_default_2048")
        self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

        self.assertEqual(payload["mode"], "rt_graph_2a1_generic_rt")
        self.assertTrue(payload["triangle_count_matches_oracle"])
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["rt_core_path"], "generic_prepared_triangle_scene_3d_any_hit_weighted_sum")
        self.assertEqual(payload["oracle_triangle_count"], 4096)
        self.assertEqual(payload["generic_rt_weighted_triangle_count"], 4096)
        self.assertEqual(payload["primitive_count"], 10240)
        self.assertEqual(payload["ray_count"], 4096)
        self.assertEqual(payload["rt_graph_fixture_copies"], 2048)
        self.assertEqual(payload["timing_ms"]["query_repeat"], 3)
        self.assertEqual(payload["timing_ms"]["query_warmup"], 1)
        self.assertLess(payload["timing_ms"]["query_median_ms"], 1.0)

        summary_payload = payload["generic_rt_summary"]
        self.assertEqual(
            summary_payload["contract"],
            "PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_V1",
        )
        self.assertFalse(summary_payload["rows_materialized"])
        self.assertTrue(summary_payload["prepared_scene_used"])
        self.assertTrue(summary_payload["prepared_reused"])
        self.assertEqual(
            payload["v2_4_prepared_session"]["native_symbols"],
            ["rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum"],
        )

    def test_report_records_route_correction_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "route correction, not a public same-contract speedup claim",
            "host_indexed_fallback",
            "query_raw_view_sec",
            "0.896843",
            "0.214 ms",
            "rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
