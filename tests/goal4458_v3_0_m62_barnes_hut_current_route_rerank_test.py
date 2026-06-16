from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_0_m62_barnes_hut_current_route_rerank.py"
DRY_RUN = ROOT / "build" / "goal4458_m62_barnes_hut_current_route_rerank_dry_run_test.json"
REPORT = ROOT / "docs" / "reports" / "goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.md"
EVIDENCE = ROOT / "docs" / "reports" / "goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.json"
EVIDENCE_INDEX = ROOT / "docs" / "learn" / "benchmark_evidence_index.md"
PARTNER_MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
README = ROOT / "examples" / "current" / "research_benchmarks" / "barnes_hut" / "README.md"


class Goal4458V30M62BarnesHutCurrentRouteRerankTest(unittest.TestCase):
    def test_script_dry_run_declares_current_route_rerank_boundary(self) -> None:
        if DRY_RUN.exists():
            DRY_RUN.unlink()
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--body-counts",
                "8192",
                "--repeat",
                "2",
                "--warmup",
                "1",
                "--output",
                str(DRY_RUN),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode)
        payload = json.loads(DRY_RUN.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["version"], "rtdl.v3_0.barnes_hut_current_route_rerank.goal4458.v1")
        self.assertEqual(tuple(payload["body_counts"]), (8192,))
        route_ids = {row["route_id"] for row in payload["routes"]}
        self.assertEqual(
            route_ids,
            {
                "cpu_numba_fused",
                "numba_cuda_fused",
                "optix_numba_prepared_frontier",
                "optix_cupy_prepared_frontier",
            },
        )
        self.assertIn("does not authorize a Barnes-Hut RT-core speedup claim", payload["claim_boundary"])

    def test_pod_evidence_reranks_current_front_doors_without_rt_speedup_claim(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        rows = {
            (int(row["body_count"]), row["route_id"]): row
            for row in payload["rows"]
        }
        comparisons = {int(row["body_count"]): row for row in payload["comparisons"]}

        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["repeat"], 31)
        self.assertEqual(payload["warmup"], 3)
        for body_count, expected_count in {
            8192: 3_406_489,
            16384: 12_727_680,
            32768: 15_514_679,
        }.items():
            comparison = comparisons[body_count]
            self.assertEqual(comparison["fastest_route_id"], "cpu_numba_fused")
            self.assertGreater(comparison["optix_numba_over_numba_cuda"], 3.0)
            self.assertGreater(comparison["optix_cupy_over_optix_numba"], 1.0)
            for route_id in (
                "cpu_numba_fused",
                "numba_cuda_fused",
                "optix_numba_prepared_frontier",
                "optix_cupy_prepared_frontier",
            ):
                row = rows[(body_count, route_id)]
                self.assertEqual(row["contribution_row_count"], expected_count)
                self.assertFalse(row["rt_core_speedup_claim_authorized"])
                self.assertFalse(row["public_speedup_claim_authorized"])
                self.assertFalse(row["frontier_rows_materialized_on_host"])
                self.assertFalse(row["contribution_rows_materialized_on_host"])
            self.assertTrue(rows[(body_count, "optix_numba_prepared_frontier")]["rt_core_accelerated_metadata"])
            self.assertTrue(rows[(body_count, "optix_cupy_prepared_frontier")]["rt_core_accelerated_metadata"])
            self.assertFalse(rows[(body_count, "cpu_numba_fused")]["rt_core_accelerated_metadata"])
            self.assertFalse(rows[(body_count, "numba_cuda_fused")]["rt_core_accelerated_metadata"])

        self.assertFalse(payload["claim_flags"]["automatic_partner_selection_authorized"])
        self.assertFalse(payload["claim_flags"]["rt_core_speedup_claim_authorized"])

    def test_docs_and_route_guidance_record_m62_boundary(self) -> None:
        import rtdsl as rt

        report = REPORT.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("barnes_hut")

        for text in (report, evidence_index, partner_matrix, readme):
            self.assertIn("Goal4458", text)
            self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", text)
            self.assertIn("fused_frontier_force_sum_bucketized_numba_cuda", text)
        self.assertIn("not a Barnes-Hut RT-core speedup claim", report)
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4480.v1",
            route["version"],
        )
        self.assertIn("Goal4458", route["evidence_refs"])
        self.assertIn("fused Numba CUDA", route["current_reader_decision"])
        self.assertIn("prepared OptiX contract, Numba remains faster than CuPy", route["current_reader_decision"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["broad_rt_core_claim_authorized"])


if __name__ == "__main__":
    unittest.main()


