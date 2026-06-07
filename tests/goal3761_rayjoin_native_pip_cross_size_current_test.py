from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_9_benchmark_adequacy import (
    V2_9_BENCHMARK_ADEQUACY_VERSION,
    summarize_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3761_rayjoin_native_pip_cross_size_current_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3761_rayjoin_native_pip_cross_size_current_2026-06-07.md"


class Goal3761RayjoinNativePipCrossSizeCurrentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_artifact_is_clean_current_main_cross_size_packet(self) -> None:
        self.assertEqual(self.payload["schema"], "rtdl.goal3688.rayjoin_native_pip_safe_mixed_composite.v1")
        self.assertEqual(self.payload["source_commit_short"], "69a4cc0a")
        self.assertFalse(self.payload["goal3688_scoped_source_dirty"])
        self.assertEqual(self.payload["counts"], [512, 1024, 2048, 4096])
        self.assertEqual(self.payload["repeat"], 10)
        self.assertEqual(self.payload["warmup"], 3)
        self.assertTrue(self.payload["summary"]["all_counts_match"])
        self.assertEqual(self.payload["summary"]["row_count"], 4)
        self.assertGreater(self.payload["summary"]["geomean_native_pip_safe_mixed_speedup_vs_all_cupy"], 280.0)
        self.assertGreater(self.payload["summary"]["min_native_pip_safe_mixed_speedup_vs_all_cupy"], 100.0)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)

    def test_each_cross_size_row_has_exact_count_parity_and_positive_workload_routes(self) -> None:
        rows = {int(row["chain_count"]): row for row in self.payload["rows"]}
        self.assertEqual(set(rows), {512, 1024, 2048, 4096})
        self.assertGreater(rows[4096]["native_pip_safe_mixed_speedup_vs_all_cupy"], 700.0)
        for row in rows.values():
            self.assertTrue(row["all_counts_match"])
            self.assertGreater(row["native_pip_safe_mixed_speedup_vs_all_cupy"], 100.0)
            workloads = {workload["workload"]: workload for workload in row["workloads"]}
            self.assertEqual(set(workloads), {"pip", "lsi", "overlay_seed"})
            self.assertEqual(workloads["pip"]["candidate_route_kind"], "rtdl_optix_native_scalar_count_executor")
            self.assertEqual(workloads["lsi"]["candidate_route_kind"], "rtdl_optix_exact_refined_count")
            self.assertEqual(workloads["overlay_seed"]["candidate_route_kind"], "rtdl_optix_active_count")
            for workload in workloads.values():
                self.assertTrue(workload["counts_match"])
                self.assertEqual(
                    int(workload["all_cupy_baseline"]["row_count"]),
                    int(workload["candidate_route"]["row_count"]),
                )
                self.assertGreater(float(workload["candidate_speedup_vs_cupy"]), 1.0)

    def test_matrix_promotes_goal3761_as_current_spatial_rayjoin_evidence(self) -> None:
        self.assertEqual(V2_9_BENCHMARK_ADEQUACY_VERSION, "rtdl.v2_10.benchmark_adequacy_after_goal3785.v1")
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(summary["adequacy_counts"]["strong"], 3)
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        rayjoin = rows["spatial_rayjoin"]
        self.assertIn("Goal3761", rayjoin["evidence_refs"])
        self.assertIn("288.759x", rayjoin["current_performance_reading"])
        self.assertIn("non-dense baseline policy", rayjoin["next_generic_runtime_action"])

    def test_report_documents_result_and_boundaries(self) -> None:
        self.assertIn("RayJoin Native-PIP Cross-Size Current Packet", self.report)
        self.assertIn("288.759x", self.report)
        self.assertIn("779.090x", self.report)
        self.assertIn("8192 Boundary", self.report)
        self.assertIn("does not authorize", self.report)
        self.assertIn("not a public `RTDL beats RayJoin` claim", self.report)


if __name__ == "__main__":
    unittest.main()
