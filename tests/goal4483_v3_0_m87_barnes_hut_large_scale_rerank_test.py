from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "docs/reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_2026-06-16.json"
PACKET = ROOT / "docs/reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_packet_2026-06-16.json"
REPORT = ROOT / "docs/reports/goal4483_v3_0_m87_barnes_hut_large_scale_rerank_packet_2026-06-16.md"


class Goal4483V30M87BarnesHutLargeScaleRerankTest(unittest.TestCase):
    def test_large_scale_packet_promotes_scale_dependent_guidance(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))

        self.assertEqual(4483, packet["goal"])
        self.assertEqual("barnes_hut_large_scale_rerank_complete", packet["status"])
        self.assertFalse(packet["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(packet["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertIn("scale-dependent", packet["route_decision"]["after_m87"])

        rows = {int(row["body_count"]): row for row in packet["rows"]}
        self.assertEqual({65536, 131072}, set(rows))
        for row in rows.values():
            self.assertEqual("numba_cuda_fused", row["fastest_route_id"])
            self.assertGreater(row["numba_cuda_speedup_vs_cpu_numba"], 2.0)
            self.assertGreater(row["numba_cuda_speedup_vs_optix_numba"], 5.0)
            self.assertGreater(row["optix_numba_slower_than_cpu_numba"], 1.0)

    def test_raw_rerank_rows_keep_rt_core_boundary(self) -> None:
        payload = json.loads(RAW.read_text(encoding="utf-8"))
        rows = {
            (int(row["body_count"]), row["route_id"]): row
            for row in payload["rows"]
        }
        comparisons = {int(row["body_count"]): row for row in payload["comparisons"]}

        self.assertEqual(payload["body_counts"], [65536, 131072])
        self.assertEqual(payload["repeat"], 11)
        self.assertEqual(payload["warmup"], 2)
        for body_count, expected_contribution_rows in {
            65536: 55_935_606,
            131072: 68_023_506,
        }.items():
            self.assertEqual("numba_cuda_fused", comparisons[body_count]["fastest_route_id"])
            self.assertGreater(comparisons[body_count]["optix_numba_over_numba_cuda"], 5.0)
            self.assertTrue(rows[(body_count, "optix_numba_prepared_frontier")]["rt_core_accelerated_metadata"])
            self.assertFalse(rows[(body_count, "numba_cuda_fused")]["rt_core_accelerated_metadata"])
            for route_id in (
                "cpu_numba_fused",
                "numba_cuda_fused",
                "optix_numba_prepared_frontier",
                "optix_cupy_prepared_frontier",
            ):
                row = rows[(body_count, route_id)]
                self.assertEqual(expected_contribution_rows, row["contribution_row_count"])
                self.assertFalse(row["rt_core_speedup_claim_authorized"])
                self.assertFalse(row["public_speedup_claim_authorized"])
                self.assertFalse(row["frontier_rows_materialized_on_host"])
                self.assertFalse(row["contribution_rows_materialized_on_host"])

    def test_report_and_registry_record_m87_guidance(self) -> None:
        routes = importlib.import_module("rtdsl.current_benchmark_route_decisions")
        adequacy = importlib.import_module("rtdsl.current_benchmark_adequacy")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("scale-dependent", report)
        self.assertIn("Numba CUDA fused", report)
        self.assertIn("no Barnes-Hut RT-core speedup claim", report)
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1",
            routes.CURRENT_BENCHMARK_ROUTE_DECISION_VERSION,
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4507.v1",
            adequacy.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        route_row = {
            row["app"]: row for row in routes.current_benchmark_route_decisions()
        }["barnes_hut"]
        adequacy_row = {
            row["app"]: row for row in adequacy.current_benchmark_adequacy()
        }["barnes_hut"]

        self.assertIn("Goal4483", route_row["evidence_refs"])
        self.assertIn("Goal4483", adequacy_row["evidence_refs"])
        self.assertIn("scale-dependent", route_row["current_reader_decision"])
        self.assertIn("65,536 / 131,072", route_row["user_choice_guidance"])
        self.assertIn("fused Numba CUDA", adequacy_row["current_recommended_path"])


if __name__ == "__main__":
    unittest.main()
