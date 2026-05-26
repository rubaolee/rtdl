from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import rtdsl as rt
from tests._embree_support import embree_available


APP = importlib.import_module(
    "examples.v2_0.research_benchmarks.librts_spatial_index.rtdl_librts_spatial_index_benchmark_app"
)
ROOT = Path(__file__).resolve().parents[1]


class GenericAabbIndexPrimitiveTest(unittest.TestCase):
    def test_generic_aabb_index_matches_tiny_cpu_oracle(self) -> None:
        fixture = APP.make_tiny_fixture()
        result = rt.query_aabb_index_2d(
            fixture.boxes,
            point_queries=fixture.point_queries,
            box_queries=fixture.box_queries,
            operation="all",
            resolution=4,
        )
        self.assertEqual(result["primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(result["contract"], "generic_prepared_aabb_index_query_2d")
        self.assertEqual(result["counts"], APP.run_counts(fixture, "all")["counts"])
        self.assertFalse(result["native_engine_customization"])
        self.assertIn("Generic CPU reference", result["claim_boundary"])
        self.assertIn("not LibRTS-specific", result["claim_boundary"])

    def test_prepared_index_reuses_cells_across_operation_queries(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=96, query_count=24, seed=2576)
        prepared = rt.prepare_aabb_index_2d(
            fixture.boxes,
            point_queries=fixture.point_queries,
            box_queries=fixture.box_queries,
            resolution=16,
        )
        point_result = prepared.count(point_queries=fixture.point_queries, operation="point_contains")
        box_result = prepared.count(box_queries=fixture.box_queries, operation="range_intersects")
        self.assertEqual(point_result["counts"], APP.run_counts(fixture, "point_contains")["counts"])
        self.assertEqual(box_result["counts"], APP.run_counts(fixture, "range_intersects")["counts"])
        self.assertGreater(prepared.candidate_entries, 0)
        self.assertGreater(point_result["candidate_checks"]["point_contains"], 0)

    def test_app_partner_grid_reference_lowers_to_generic_aabb_primitive(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=64, query_count=32, seed=41)
        result = APP.run_grid_counts(fixture, "all", resolution=16)
        self.assertEqual(result["generic_primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(result["primitive_contract"], "generic_prepared_aabb_index_query_2d")
        self.assertTrue(result["matches_cpu_reference"])
        self.assertFalse(result["native_engine_customization"])

    def test_public_exports_include_behavior_named_aabb_api(self) -> None:
        for name in (
            "AABB_INDEX_2D_CONTRACT",
            "Aabb2D",
            "AabbIndex2D",
            "EmbreeAabbIndex2D",
            "OptixAabbIndex2D",
            "prepare_aabb_index_2d",
            "query_aabb_index_2d",
        ):
            self.assertIn(name, rt.__all__)
            self.assertTrue(hasattr(rt, name))

    @unittest.skipUnless(embree_available(), "Embree runtime is not available")
    def test_embree_aabb_index_matches_tiny_cpu_oracle(self) -> None:
        fixture = APP.make_tiny_fixture()
        result = rt.query_aabb_index_2d(
            fixture.boxes,
            point_queries=fixture.point_queries,
            box_queries=fixture.box_queries,
            operation="all",
            backend="embree",
        )

        self.assertEqual(result["backend"], "embree")
        self.assertEqual(result["counts"], APP.run_counts(fixture, "all")["counts"])
        self.assertFalse(result["native_engine_customization"])
        self.assertIn("columnar conjunctive-scan", result["claim_boundary"])

    def test_report_records_app_agnostic_boundary(self) -> None:
        report = (
            ROOT / "docs/reports/goal2576_librts_generic_aabb_index_primitive_2026-05-24.md"
        ).read_text(encoding="utf-8")
        self.assertIn("AABB_INDEX_QUERY_2D", report)
        self.assertIn("no `LibRTS` native symbol", report)
        self.assertIn("app-agnostic names and metadata", report)


if __name__ == "__main__":
    unittest.main()
