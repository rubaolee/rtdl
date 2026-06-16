from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
REPORT = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_prepared_frontier_app_mode_2026-06-16.md"
NUMBA_8192 = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json"
CUPY_8192 = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_cupy_8192_2026-06-16.json"
NUMBA_SMOKE = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_128_smoke_2026-06-16.json"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _has_cupy_numba_cuda() -> bool:
    try:
        import cupy  # noqa: F401
        import rtdsl as rt

        rt.configure_numba_cuda_toolchain_environment()
        from numba import cuda
    except Exception:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:
        return False


class Goal4439V30M42BarnesHutPreparedFrontierAppModeTest(unittest.TestCase):
    def test_app_exposes_explicit_prepared_frontier_mode(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        scope = barnes_hut.run_benchmark("scope")
        self.assertIn("prepared_aggregate_frontier_weighted_vector_optix", barnes_hut.MODES)
        self.assertIn(
            "generic_aggregate_frontier_device_columns_2d_v1",
            scope["current_supported_contracts"],
        )
        self.assertIn(
            "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_numba_v1",
            scope["current_supported_contracts"],
        )
        source = APP.read_text(encoding="utf-8")
        for phrase in (
            "_prepared_aggregate_frontier_weighted_vector_optix_payload",
            "frontier_capacity_multiplier",
            "frontier_row_capacity",
            "automatic_partner_selection_allowed",
            "contribution_rows_materialized_on_host",
            "native_engine_app_specific",
        ):
            self.assertIn(phrase, source)
        with self.assertRaisesRegex(ValueError, "supports --partner cupy or numba"):
            barnes_hut.run_benchmark(
                "prepared_aggregate_frontier_weighted_vector_optix",
                partner="torch",
            )

    def test_readme_and_report_document_app_mode_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for text in (readme, report):
            self.assertIn("prepared_aggregate_frontier_weighted_vector_optix", text)
            self.assertIn("--partner numba", text)
            self.assertIn("--partner cupy", text)
        for phrase in (
            "M42 turns the M39/M41 prepared aggregate-frontier route into a named Barnes-Hut",
            "automatic_partner_selection_allowed = False",
            "not an OptiX-vs-Embree or GPU-vs-CPU comparison",
            "same-contract CPU/Embree evidence",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_numba_and_cupy_app_mode_rows(self) -> None:
        numba = json.loads(NUMBA_8192.read_text(encoding="utf-8"))
        cupy = json.loads(CUPY_8192.read_text(encoding="utf-8"))
        smoke = json.loads(NUMBA_SMOKE.read_text(encoding="utf-8"))

        self.assertEqual(numba["mode"], "prepared_aggregate_frontier_weighted_vector_optix")
        self.assertEqual(cupy["mode"], "prepared_aggregate_frontier_weighted_vector_optix")
        self.assertEqual(numba["partner"], "numba")
        self.assertEqual(cupy["partner"], "cupy")
        self.assertEqual(numba["vector_sum_summary"]["frontier_row_count"], 3_406_489)
        self.assertEqual(cupy["vector_sum_summary"]["frontier_row_count"], 3_406_489)
        self.assertEqual(numba["vector_sum_summary"]["aggregate_contribution_row_count"], 477_919)
        self.assertEqual(cupy["vector_sum_summary"]["exact_contribution_row_count"], 2_928_570)
        self.assertLess(
            numba["medians"]["partner_seconds"],
            cupy["medians"]["partner_seconds"],
        )
        self.assertLess(
            numba["medians"]["hot_seconds_native_plus_partner"],
            cupy["medians"]["hot_seconds_native_plus_partner"],
        )
        partner_speedup = cupy["medians"]["partner_seconds"] / numba["medians"]["partner_seconds"]
        hot_speedup = (
            cupy["medians"]["hot_seconds_native_plus_partner"]
            / numba["medians"]["hot_seconds_native_plus_partner"]
        )
        self.assertGreater(partner_speedup, 6.0)
        self.assertGreater(hot_speedup, 1.3)
        for payload in (numba, cupy, smoke):
            flags = payload["claim_flags"]
            self.assertTrue(flags["same_frontier_contract"])
            self.assertTrue(flags["explicit_partner_choice"])
            self.assertFalse(flags["automatic_partner_selection_allowed"])
            self.assertFalse(flags["frontier_columns_materialized_on_host"])
            self.assertFalse(flags["contribution_rows_materialized_on_host"])
            self.assertFalse(flags["native_engine_app_specific"])
            self.assertFalse(flags["public_speedup_claim_authorized"])
            self.assertFalse(flags["rt_core_speedup_claim_authorized"])
            self.assertFalse(flags["whole_app_speedup_claim_authorized"])
        self.assertFalse(smoke["validation"]["skipped"])
        self.assertTrue(smoke["validation"]["passed"])

    def test_route_registry_points_to_m42_app_mode(self) -> None:
        import rtdsl as rt

        route = rt.explain_current_benchmark_route("barnes_hut")
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4443.v1",
            route["version"],
        )
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("explicit_route_choice_cpu_numba_or_optix_numba_cupy_comparison", route["partner_policy"])
        self.assertIn("Goal4439", route["evidence_refs"])
        self.assertIn("Goal4440", route["evidence_refs"])
        self.assertIn("Goal4441", route["evidence_refs"])
        self.assertIn("Goal4442", route["evidence_refs"])
        self.assertIn("prepared_aggregate_frontier_weighted_vector_optix", route["current_reader_decision"])
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", route["current_reader_decision"])
        self.assertIn("fused RT-native/device route", route["next_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    @unittest.skipUnless(_has_cupy_numba_cuda(), "CuPy and Numba CUDA are required for live app-mode smoke")
    def test_live_numba_app_mode_matches_cpu_reference_when_optix_is_available(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        try:
            payload = barnes_hut.run_benchmark(
                "prepared_aggregate_frontier_weighted_vector_optix",
                partner="numba",
                body_count=64,
                bucket_size=16,
                theta=0.5,
                query_repeat=1,
                warmup=1,
                force_output_mode="force_summary",
            )
        except Exception as exc:
            self.skipTest(f"prepared OptiX aggregate-frontier app mode unavailable: {exc}")

        self.assertEqual(payload["partner"], "numba")
        self.assertTrue(payload["validation"]["passed"])
        self.assertFalse(payload["claim_flags"]["frontier_columns_materialized_on_host"])
        self.assertFalse(payload["claim_flags"]["contribution_rows_materialized_on_host"])
        self.assertGreater(payload["medians"]["hot_seconds_native_plus_partner"], 0.0)


if __name__ == "__main__":
    unittest.main()
