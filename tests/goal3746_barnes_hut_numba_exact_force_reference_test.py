from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt
from examples.current.apps.simulation import rtdl_barnes_hut_force_app as app
from examples.current.research_benchmarks.barnes_hut import rtdl_barnes_hut_benchmark_app as benchmark


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src/rtdsl/app_adapters/barnes_hut.py"
PARTNER_ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
APP = ROOT / "examples/current/apps/simulation/rtdl_barnes_hut_force_app.py"
BENCHMARK = ROOT / "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
REPORT = ROOT / "docs/reports/goal3746_barnes_hut_numba_exact_force_reference_2026-06-07.md"
ARTIFACT = ROOT / "docs/reports/goal3746_barnes_hut_numba_exact_force_a5000/summary.json"


class Goal3746BarnesHutNumbaExactForceReferenceTest(unittest.TestCase):
    def test_weighted_point_columns_and_app_accept_numba_partner(self) -> None:
        self.assertTrue(hasattr(rt, "weighted_point_rows_to_partner_columns"))
        self.assertTrue(hasattr(rt, "pairwise_inverse_square_force_2d_partner_columns"))
        self.assertIn('partner == "numba"', PARTNER_ADAPTERS.read_text(encoding="utf-8"))
        self.assertIn('choices=("torch", "cupy", "numba")', APP.read_text(encoding="utf-8"))
        self.assertIn('choices=("torch", "cupy", "numba")', BENCHMARK.read_text(encoding="utf-8"))

    def test_numba_exact_force_kernel_is_app_scoped_and_non_authorizing(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")
        self.assertIn("def _numba_pairwise_force_2d_kernel", text)
        self.assertIn("numba_cuda_jit_used", text)
        self.assertIn('"raw_cuda_kernel_required": False', text)
        self.assertIn('"native_engine_row_contract": "not_called_partner_reference_only"', text)
        self.assertIn('"rt_core_speedup_claim_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)

    def test_readme_documents_numba_as_no_rawkernel_reference(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("--partner numba", text)
        self.assertIn("no-RawKernel reference", text)
        self.assertIn("not an RT-core claim", text)

    def test_report_records_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3746", text)
        self.assertIn("Numba CUDA JIT", text)
        self.assertIn("A5000 pod evidence", text)
        self.assertIn("not hierarchical Barnes-Hut acceleration", text)
        self.assertIn("not an RT-core claim", text)

    def test_pod_artifact_records_numba_cupy_same_contract_timing(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3746.barnes_hut_numba_exact_force_a5000.v1")
        self.assertTrue(payload["correctness"]["matches_oracle"])
        self.assertLess(payload["correctness"]["max_relative_error"], 1.0e-12)
        self.assertEqual(payload["tuning"], "numba_cuda_jit_fastmath_true")
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        for body_count in ("1024", "2048", "4096", "8192"):
            row = payload["comparison_by_body_count"][body_count]
            self.assertGreater(row["numba_speedup_vs_cupy"], 0.70)
            self.assertGreater(row["cupy_median_sec"], 0)
            self.assertGreater(row["numba_median_sec"], 0)

    def test_numba_exact_force_matches_cpu_oracle_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        payload = app.run_app(
            "partner_exact_force",
            partner="numba",
            body_count=64,
            output_mode="force_summary",
            skip_validation=False,
        )
        self.assertEqual(payload["partner"], "numba")
        self.assertTrue(payload["matches_oracle"])
        self.assertLess(payload["max_relative_error"], 1.0e-12)
        self.assertEqual(
            payload["partner_reference_contract"],
            "generic_pairwise_inverse_square_force_2d",
        )
        self.assertTrue(payload["partner_metadata"]["numba_cuda_jit_used"])
        self.assertFalse(payload["partner_metadata"]["raw_cuda_kernel_required"])
        self.assertFalse(payload["partner_metadata"]["rt_core_speedup_claim_authorized"])

    def test_benchmark_wrapper_runs_numba_exact_force_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        payload = benchmark.run_benchmark(
            "partner_exact_force",
            partner="numba",
            body_count=64,
            skip_validation=False,
        )
        self.assertEqual(payload["partner"], "numba")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(
            payload["benchmark_metadata"]["contract"],
            "generic_weighted_point_pairwise_inverse_square_force_partner_reference",
        )
        self.assertFalse(payload["benchmark_metadata"]["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
