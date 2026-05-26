from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as app,
)


ROOT = Path(__file__).resolve().parents[1]


class Goal2622ContactManifoldGenericAabbDiscoveryTest(unittest.TestCase):
    def test_generic_aabb_pair_rows_emit_exact_intersection_candidates(self) -> None:
        result = rt.aabb_intersection_pair_rows_2d(
            indexed_boxes=((0.0, 0.0, 1.0, 1.0), (3.0, 0.0, 4.0, 1.0)),
            query_boxes=((0.5, 0.5, 0.6, 0.6), (2.0, 0.0, 2.5, 1.0)),
            indexed_ids=(10, 11),
            query_ids=(20, 21),
            resolution=4,
        )

        self.assertEqual(result["primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(result["contract"], "generic_aabb_intersection_pair_rows_2d")
        self.assertEqual(result["row_schema"], ("query_id", "indexed_id"))
        self.assertEqual(result["candidate_id_rows"], ((20, 10),))
        self.assertFalse(result["native_engine_customization"])

    def test_contact_app_aabb_broadphase_matches_tiny_reference(self) -> None:
        payload = app.aabb_broadphase_collect_k_payload(
            dataset="tiny",
            witness_capacity=3,
            resolution=16,
        )

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["candidate_discovery_primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(payload["primitive_under_test"], "COLLECT_K_BOUNDED")
        self.assertEqual(payload["candidate_id_rows"], ((0, 10, 0), (0, 11, 1), (2, 30, 2)))
        self.assertEqual(payload["exact_refinement_checks"], payload["aabb_candidate_pair_count"])
        self.assertFalse(payload["engine_boundary"]["native_collision_logic_allowed"])

    def test_grid_broadphase_removes_full_python_all_pairs_discovery(self) -> None:
        payload = app.aabb_broadphase_collect_k_payload(
            dataset="grid",
            grid_count=256,
            witness_capacity=256,
            resolution=256,
        )

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["valid_count"], 256)
        self.assertEqual(payload["all_pairs_count"], 256 * 256)
        self.assertLess(payload["exact_refinement_checks"], payload["all_pairs_count"] // 8)
        self.assertGreater(payload["aabb_pruning_ratio"], 0.80)

    def test_default_aabb_resolution_avoids_skinny_grid_cell_explosion(self) -> None:
        self.assertEqual(app.default_aabb_resolution(grid_count=512), 22)
        self.assertEqual(app.default_aabb_resolution(grid_count=65_536), 256)

        payload = app.aabb_broadphase_collect_k_payload(
            dataset="grid",
            grid_count=512,
            witness_capacity=512,
        )

        self.assertEqual(payload["resolution_policy"], "adaptive_sqrt_capped_16_256")
        self.assertLess(payload["resolution"], 512)
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["exact_refinement_checks"], 512)

    def test_aabb_broadphase_overflow_still_fails_closed(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "partial_result_returned=False"):
            app.aabb_broadphase_collect_k_payload(
                dataset="tiny",
                witness_capacity=2,
                resolution=16,
            )

    def test_app_uses_generic_aabb_discovery_without_shape_pair_native_collector(self) -> None:
        source = inspect.getsource(app)

        self.assertIn("aabb_intersection_pair_rows_2d", source)
        self.assertIn("AABB_INDEX_QUERY_2D", source)
        self.assertNotIn("collect_shape_pair_candidates_bounded", source)
        self.assertNotIn("rtdl_embree_collect_shape_pair_candidates_bounded", source)
        self.assertNotIn("rtdl_optix_collect_shape_pair_candidates_bounded", source)

    def test_docs_record_goal2622_boundary_and_consensus(self) -> None:
        readme = (
            ROOT
            / "examples"
            / "v2_0"
            / "research_benchmarks"
            / "contact_manifold"
            / "README.md"
        ).read_text(encoding="utf-8")
        primitive_catalog = (ROOT / "docs" / "rtdl_primitive_catalog.md").read_text(
            encoding="utf-8"
        )
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal2622_contact_manifold_generic_aabb_discovery_2026-05-25.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reports"
            / "goal2622_contact_manifold_generic_aabb_discovery_3ai_consensus_2026-05-25.md"
        ).read_text(encoding="utf-8")

        self.assertIn("aabb_broadphase_collect_k", readme)
        self.assertIn("AABB_INDEX_QUERY_2D", primitive_catalog)
        self.assertIn("generic AABB broadphase", report)
        self.assertIn("exact refinement remains app-owned", report)
        self.assertIn("3-AI Consensus", consensus)
        self.assertIn("no collision-specific native engine logic", consensus)


if __name__ == "__main__":
    unittest.main()
