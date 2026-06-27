from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"
README = ROOT / "examples" / "current" / "research_benchmarks" / "barnes_hut" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_2026-06-16.md"
SMOKE = ROOT / "docs" / "reports" / "goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_64_smoke_2026-06-16.json"
SCALE = ROOT / "docs" / "reports" / "goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_8192_r11_2026-06-16.json"
EVIDENCE_INDEX = ROOT / "docs" / "learn" / "benchmark_evidence_index.md"
PARTNER_MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"


def _has_numba_cuda() -> bool:
    try:
        from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment

        configure_numba_cuda_toolchain_environment()
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4450V30M54BarnesHutNumbaCudaAppModeTest(unittest.TestCase):
    def test_app_mode_is_front_door_for_reusable_fused_partner(self) -> None:
        from examples.benchmark_apps.barnes_hut import rtdl_barnes_hut_benchmark_app as app

        source = APP.read_text(encoding="utf-8")
        block = source[
            source.index("def _fused_frontier_force_sum_numba_cuda_payload") :
            source.index("def _fused_frontier_force_sum_payload")
        ]
        scope = app.scope_payload()

        self.assertIn("fused_frontier_force_sum_bucketized_numba_cuda", app.MODES)
        self.assertIn(
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
            scope["current_supported_contracts"],
        )
        self.assertIn("rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda", block)
        self.assertIn("kernel_event_median_sec", block)
        self.assertIn("frontier_rows_materialized_on_host", block)
        self.assertIn("rt_core_speedup_claim_authorized", block)
        for forbidden in (
            "import torch",
            "from torch",
            "load_inline(",
            "CPP_SOURCE",
            "CUDA_SOURCE =",
        ):
            self.assertNotIn(forbidden, block)

    def test_report_docs_and_current_guidance_include_app_mode_boundary(self) -> None:
        import rtdsl as rt

        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        scale = json.loads(SCALE.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}
        barnes = rows["barnes_hut"]

        for text in (report, readme, evidence_index, partner_matrix):
            self.assertIn("Goal4450", text)
            self.assertIn("fused_frontier_force_sum_bucketized_numba_cuda", text)
        self.assertIn("not an RT-core primitive", report)
        self.assertTrue(smoke["validation"]["passed"])
        self.assertFalse(smoke["claim_flags"]["rt_cores_used"])
        self.assertFalse(smoke["claim_flags"]["rt_core_speedup_claim_authorized"])
        self.assertEqual(scale["body_count"], 8192)
        self.assertEqual(scale["vector_sum_summary"]["contribution_row_count"], 3_406_489)
        self.assertIn("Goal4450", barnes["evidence_refs"])
        self.assertIn("fused_frontier_force_sum_bucketized_numba_cuda", barnes["current_recommended_path"])
        self.assertFalse(barnes["broad_rt_core_claim_authorized"])

    @unittest.skipUnless(_has_numba_cuda(), "Numba CUDA is required for live app-mode smoke")
    def test_live_app_mode_matches_cpu_reference_and_keeps_claim_flags_closed(self) -> None:
        from examples.benchmark_apps.barnes_hut import rtdl_barnes_hut_benchmark_app as app

        payload = app.run_benchmark(
            "fused_frontier_force_sum_bucketized_numba_cuda",
            body_count=64,
            theta=0.5,
            bucket_size=8,
            max_depth=32,
            query_repeat=2,
            warmup=1,
            force_output_mode="force_summary",
        )

        self.assertEqual(payload["mode"], "fused_frontier_force_sum_bucketized_numba_cuda")
        self.assertEqual(payload["backend"], "numba_cuda_fused_aggregate_tree_vector_sum")
        self.assertTrue(payload["validation"]["passed"])
        self.assertEqual(
            payload["vector_sum_summary"]["contribution_row_count"],
            payload["validation"]["reference_frontier_row_count"],
        )
        self.assertIsNotNone(payload["run_phases"]["kernel_event_median_sec"])
        self.assertFalse(payload["vector_sum_summary"]["frontier_rows_materialized_on_host"])
        self.assertFalse(payload["vector_sum_summary"]["contribution_rows_materialized_on_host"])
        self.assertFalse(payload["claim_flags"]["rt_cores_used"])
        self.assertFalse(payload["claim_flags"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["benchmark_metadata"]["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
