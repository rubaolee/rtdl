from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as app,
)


ROOT = Path(__file__).resolve().parents[1]


class Goal2621ContactManifoldCollectKBoundedBenchmarkTest(unittest.TestCase):
    def test_scope_keeps_engine_primitive_generic(self) -> None:
        payload = app.scope_payload()

        self.assertEqual(payload["status"], "promoted_benchmark_internal_no_public_speedup_claim")
        self.assertEqual(payload["primitive_under_test"], "COLLECT_K_BOUNDED")
        self.assertEqual(
            payload["primitive_behavior"],
            "bounded generic int64 witness row collection",
        )
        self.assertFalse(payload["engine_boundary"]["native_collision_logic_allowed"])
        self.assertEqual(payload["row_schema"], app.ROW_SCHEMA)

    def test_tiny_fixture_has_exact_expected_witness_rows(self) -> None:
        payload = app.cpu_reference_payload(dataset="tiny")

        self.assertEqual(
            payload["candidate_id_rows"],
            ((0, 10, 0), (0, 11, 1), (2, 30, 2)),
        )
        self.assertEqual(payload["valid_count"], 3)
        self.assertEqual(payload["correctness_oracle"], "deterministic_python_triangle_intersection")

    def test_collect_path_uses_generic_collect_k_rows(self) -> None:
        payload = app.collect_k_reference_payload(dataset="tiny", witness_capacity=3)

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["primitive_under_test"], "COLLECT_K_BOUNDED")
        self.assertEqual(
            payload["candidate_id_rows"],
            ((0, 10, 0), (0, 11, 1), (2, 30, 2)),
        )
        self.assertFalse(payload["overflowed"])
        self.assertTrue(payload["complete_candidate_coverage"])

    def test_native_embree_collect_path_if_local_library_exists(self) -> None:
        library_path = app._default_library_path("embree")
        if library_path is None:
            self.skipTest("local Embree library unavailable")

        payload = app.native_collect_k_payload(dataset="tiny", witness_capacity=3, backend="embree")

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["native_generic_symbol"], "rtdl_embree_collect_k_bounded_i64")
        self.assertEqual(payload["candidate_id_rows"], ((0, 10, 0), (0, 11, 1), (2, 30, 2)))
        self.assertFalse(payload["engine_boundary"]["native_collision_logic_allowed"])

    def test_standalone_cpp_baseline_matches_reference_if_compiler_exists(self) -> None:
        if not app.shutil.which("c++") and not app.shutil.which("clang++") and not app.shutil.which("g++"):
            self.skipTest("C++ compiler unavailable")

        payload = app.cpp_baseline_payload(dataset="tiny", repeat_count=2)

        self.assertEqual(payload["baseline"], "standalone_cpp_exact_triangle_pairs")
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["candidate_id_rows"], ((0, 10, 0), (0, 11, 1), (2, 30, 2)))
        self.assertIn("without RTDL engine calls", payload["claim_boundary"])

    def test_overflow_fails_closed_without_partial_rows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "partial_result_returned=False"):
            app.collect_k_reference_payload(dataset="tiny", witness_capacity=2)

    def test_app_source_does_not_call_collision_specific_native_symbols(self) -> None:
        source = inspect.getsource(app)

        self.assertIn("collect_k_bounded_rows", source)
        self.assertIn("cpp_contact_witness_baseline.cpp", source)
        self.assertNotIn("collect_shape_pair_candidates_bounded", source)
        self.assertNotIn("rtdl_embree_collect_shape_pair_candidates_bounded", source)
        self.assertNotIn("rtdl_optix_collect_shape_pair_candidates_bounded", source)

    def test_docs_record_promoted_boundary_without_speedup_claim(self) -> None:
        catalog = (ROOT / "docs" / "application_catalog.md").read_text(encoding="utf-8")
        primitive_catalog = (ROOT / "docs" / "rtdl_primitive_catalog.md").read_text(
            encoding="utf-8"
        )
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal2621_bounded_contact_witness_collect_k_candidate_2026-05-25.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reports"
            / "goal2621_bounded_contact_witness_collect_k_3ai_consensus_2026-05-25.md"
        ).read_text(encoding="utf-8")
        smoke_script = (ROOT / "scripts" / "goal2617_surface_smoke.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("contact_manifold/", catalog)
        self.assertIn("Promoted benchmark for generic bounded witness collection", catalog)
        self.assertIn("no native contact/collision ABI and no speedup claim", catalog)
        self.assertIn("`COLLECT_K_BOUNDED` | Stable primitive", primitive_catalog)
        self.assertIn("bounded witness-row collection", primitive_catalog)
        self.assertIn("collision/contact semantics stay in Python app code", primitive_catalog)
        self.assertIn("promoted the app to", report)
        self.assertIn("does not authorize public speedup claims", report)
        self.assertIn("Pod OptiX Evidence", report)
        self.assertIn("No collision-specific native primitive", report)
        self.assertIn("Promotion Addendum", consensus)
        self.assertIn("promoted internal benchmark app", consensus)
        self.assertIn("COLLECT_K_BOUNDED` is promoted to stable", consensus)
        self.assertIn("contact_manifold_collect_k_benchmark", smoke_script)


if __name__ == "__main__":
    unittest.main()
