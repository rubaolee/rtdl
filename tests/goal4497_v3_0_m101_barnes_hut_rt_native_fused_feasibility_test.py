from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
SCRIPT = ROOT / "scripts/goal4497_m101_barnes_hut_rt_native_fused_feasibility.py"


class Goal4497V30M101BarnesHutRtNativeFusedFeasibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {int(row["body_count"]): row for row in cls.packet["rows"]}

    def test_packet_defines_rt_native_fused_boundary(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.barnes_hut_rt_native_fused_feasibility.goal4497.v1",
            self.packet["version"],
        )
        self.assertEqual("Goal4497 / V3 M101", self.packet["goal"])
        self.assertEqual(5, self.packet["summary"]["scale_rows"])
        self.assertTrue(self.packet["summary"]["prepared_optix_numba_loses_all_rows"])
        self.assertEqual(
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
            self.packet["candidate_contract"]["proposed_contract"],
        )
        self.assertIn("aggregate-frontier row emission", self.packet["candidate_contract"]["must_avoid"])
        self.assertIn("native RT program or equivalent payload accumulation", self.packet["candidate_contract"]["implementation_requirements"])
        self.assertTrue(JSONL.exists())

    def test_scale_rows_keep_current_fastest_and_rt_core_boundary(self) -> None:
        expected = {
            8192: "cpu_numba_fused",
            16384: "cpu_numba_fused",
            32768: "cpu_numba_fused",
            65536: "numba_cuda_fused",
            131072: "numba_cuda_fused",
        }
        self.assertEqual(expected, {body: row["fastest_route_id"] for body, row in self.rows.items()})
        for body_count, row in self.rows.items():
            self.assertFalse(row["rt_core_route_faster_than_best_current_route"], body_count)
            self.assertGreater(row["optix_numba_slower_than_best_current_route"], 1.0, body_count)
        self.assertAlmostEqual(0.594241125, self.rows[131072]["optix_frontier_traversal_s"], places=9)

        boundary = self.packet["claim_boundary"]
        self.assertTrue(boundary["feasibility_gate_only"])
        self.assertFalse(boundary["rt_native_fused_primitive_implemented"])
        self.assertFalse(boundary["numba_cuda_fused_route_uses_rt_cores"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])

    def test_report_docs_and_current_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        matrix = MATRIX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("barnes_hut")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["barnes_hut"]

        self.assertIn("Goal4497 / V3 M101", report)
        self.assertIn("generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1", report)
        self.assertIn("Goal4497 Barnes-Hut RT-native fused feasibility", index)
        self.assertIn("Goal4497 defines the missing future generic RT-native", matrix)
        self.assertIn("PACKET_VERSION", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4503.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4503.v1", adequacy["version"])
        self.assertIn("Goal4497", route["evidence_refs"])
        self.assertIn("Goal4497", adequacy["evidence_refs"])
        self.assertIn("implement and validate the Goal4497", route["next_runtime_action"])
        self.assertIn("RT-native fused weighted-vector primitive", adequacy["next_generic_runtime_action"])
        self.assertTrue(route["pod_needed_next"])
        self.assertTrue(adequacy["pod_needed_next"])


if __name__ == "__main__":
    unittest.main()
