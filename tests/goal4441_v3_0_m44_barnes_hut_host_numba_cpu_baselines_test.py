from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
REPORT = ROOT / "docs/reports/goal4441_v3_0_m44_barnes_hut_host_numba_cpu_baselines_2026-06-16.md"
CPU_SMOKE = ROOT / "docs/reports/goal4441_v3_0_m44_barnes_hut_cpu_host_numba_128_smoke_2026-06-16.json"
EMBREE_SMOKE = ROOT / "docs/reports/goal4441_v3_0_m44_barnes_hut_embree_host_numba_128_smoke_2026-06-16.json"
CPU_8192 = ROOT / "docs/reports/goal4441_v3_0_m44_barnes_hut_cpu_host_numba_8192_2026-06-16.json"
EMBREE_8192 = ROOT / "docs/reports/goal4441_v3_0_m44_barnes_hut_embree_host_numba_8192_2026-06-16.json"
CPU_PY_8192 = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_cpu_host_8192_2026-06-16.json"
EMBREE_PY_8192 = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_embree_host_8192_2026-06-16.json"
OPTIX_NUMBA_8192 = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _has_numba_cpu() -> bool:
    try:
        import numba  # noqa: F401
        import numpy  # noqa: F401
    except Exception:
        return False
    return True


class Goal4441V30M44BarnesHutHostNumbaCpuBaselinesTest(unittest.TestCase):
    def test_app_exposes_host_numba_cpu_modes(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        scope = barnes_hut.run_benchmark("scope")
        self.assertIn("aggregate_frontier_weighted_vector_cpu_host_numba", barnes_hut.MODES)
        self.assertIn("aggregate_frontier_weighted_vector_embree_host_numba", barnes_hut.MODES)
        self.assertIn(
            "generic_aggregate_frontier_collect_2d_host_numba_cpu_weighted_vector_sum_baseline",
            scope["current_supported_contracts"],
        )

        source = APP.read_text(encoding="utf-8")
        for phrase in (
            "_host_numba_cpu_weighted_vector_sum_from_frontier_i64_rows",
            "_host_numba_cpu_frontier_vector_sum_kernel",
            "parallel_by_source_offsets",
            "raw_c_or_cuda_kernel_required",
            "numba_cpu_njit_used",
        ):
            self.assertIn(phrase, source)

    def test_readme_and_report_document_m44_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for text in (readme, report):
            self.assertIn("aggregate_frontier_weighted_vector_cpu_host_numba", text)
            self.assertIn("aggregate_frontier_weighted_vector_embree_host_numba", text)
        for phrase in (
            "replace the Python dict-based host vector accumulation",
            "724.7x",
            "681.1x",
            "remaining Barnes-Hut CPU-side bottleneck",
            "frontier collection and host row materialization",
            "not a same device-resident OptiX-vs-Embree comparison",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_shows_numba_cpu_continuation_fix(self) -> None:
        cpu_smoke = json.loads(CPU_SMOKE.read_text(encoding="utf-8"))
        embree_smoke = json.loads(EMBREE_SMOKE.read_text(encoding="utf-8"))
        cpu_numba = json.loads(CPU_8192.read_text(encoding="utf-8"))
        embree_numba = json.loads(EMBREE_8192.read_text(encoding="utf-8"))
        cpu_python = json.loads(CPU_PY_8192.read_text(encoding="utf-8"))
        embree_python = json.loads(EMBREE_PY_8192.read_text(encoding="utf-8"))
        optix_numba = json.loads(OPTIX_NUMBA_8192.read_text(encoding="utf-8"))

        for smoke in (cpu_smoke, embree_smoke):
            self.assertFalse(smoke["validation"]["skipped"])
            self.assertTrue(smoke["validation"]["passed"])
            self.assertEqual(smoke["frontier_collection"]["frontier_row_count"], 8_766)
            self.assertEqual(smoke["vector_sum_summary"]["run_median_seconds"], smoke["run_phases"]["vector_run_median_sec"])

        for payload in (cpu_numba, embree_numba):
            self.assertEqual(payload["body_count"], 8192)
            self.assertEqual(payload["frontier_collection"]["frontier_row_count"], 3_406_489)
            self.assertEqual(payload["vector_sum_summary"]["aggregate_contribution_row_count"], 477_919)
            self.assertEqual(payload["vector_sum_summary"]["exact_contribution_row_count"], 2_928_570)
            self.assertAlmostEqual(
                payload["vector_sum_summary"]["checksum_force_x"],
                optix_numba["vector_sum_summary"]["checksum_force_x"],
                places=8,
            )
            self.assertAlmostEqual(
                payload["vector_sum_summary"]["checksum_force_y"],
                optix_numba["vector_sum_summary"]["checksum_force_y"],
                places=8,
            )
            flags = payload["claim_flags"]
            self.assertTrue(flags["numba_cpu_njit_used"])
            self.assertFalse(flags["python_vector_sum_used"])
            self.assertTrue(flags["frontier_rows_materialized_on_host"])
            self.assertFalse(flags["same_device_resident_contract"])
            self.assertFalse(flags["public_speedup_claim_authorized"])

        cpu_vector_speedup = (
            cpu_python["run_phases"]["vector_sum_sec"]
            / cpu_numba["run_phases"]["vector_run_median_sec"]
        )
        embree_vector_speedup = (
            embree_python["run_phases"]["vector_sum_sec"]
            / embree_numba["run_phases"]["vector_run_median_sec"]
        )
        self.assertGreater(cpu_vector_speedup, 700.0)
        self.assertGreater(embree_vector_speedup, 650.0)
        self.assertGreater(
            cpu_numba["run_phases"]["frontier_collect_sec"],
            1000.0 * cpu_numba["run_phases"]["vector_run_median_sec"],
        )
        self.assertGreater(
            embree_numba["run_phases"]["frontier_collect_sec"],
            1000.0 * embree_numba["run_phases"]["vector_run_median_sec"],
        )

    def test_route_registry_records_m44_without_public_backend_wording(self) -> None:
        import rtdsl as rt

        route = rt.explain_current_benchmark_route("barnes_hut")
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4472.v1",
            route["version"],
        )
        self.assertIn("Goal4441", route["evidence_refs"])
        self.assertIn("Goal4442", route["evidence_refs"])
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", route["current_reader_decision"])
        self.assertIn("fused RT-native/device route", route["next_runtime_action"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    @unittest.skipUnless(_has_numba_cpu(), "Numba CPU is required for live host+Numba smoke")
    def test_live_cpu_host_numba_mode_matches_reference_on_small_case(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        payload = barnes_hut.run_benchmark(
            "aggregate_frontier_weighted_vector_cpu_host_numba",
            body_count=32,
            bucket_size=16,
            theta=0.5,
            warmup=1,
            query_repeat=2,
            force_output_mode="force_summary",
        )

        self.assertEqual(payload["mode"], "aggregate_frontier_weighted_vector_cpu_host_numba")
        self.assertFalse(payload["validation"]["skipped"])
        self.assertTrue(payload["validation"]["passed"])
        self.assertTrue(payload["claim_flags"]["numba_cpu_njit_used"])
        self.assertFalse(payload["claim_flags"]["python_vector_sum_used"])


if __name__ == "__main__":
    unittest.main()


