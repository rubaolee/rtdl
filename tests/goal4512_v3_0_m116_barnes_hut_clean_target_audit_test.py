from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4512_v3_0_m116_barnes_hut_clean_target_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4512_v3_0_m116_barnes_hut_clean_target_audit_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4512_m116_barnes_hut_clean_target_audit.py"


class Goal4512V30M116BarnesHutCleanTargetAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4512_m116_barnes_hut_clean_target_audit")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_current_route_policy_is_scale_dependent_and_explicit(self) -> None:
        policy = self.packet["current_route_policy"]
        rows = {row["body_count"]: row for row in policy["rows"]}

        self.assertEqual("rtdl.v3_0.barnes_hut_clean_target_audit.goal4512.v1", self.packet["version"])
        self.assertEqual(5, len(rows))
        self.assertTrue(policy["small_scale_fastest_all_cpu_numba"])
        self.assertTrue(policy["large_scale_fastest_all_numba_cuda"])
        self.assertTrue(policy["prepared_optix_numba_loses_all_rows"])
        self.assertEqual("cpu_numba_fused", rows[8192]["fastest_route_id"])
        self.assertEqual("cpu_numba_fused", rows[32768]["fastest_route_id"])
        self.assertEqual("numba_cuda_fused", rows[65536]["fastest_route_id"])
        self.assertEqual("numba_cuda_fused", rows[131072]["fastest_route_id"])
        for row in rows.values():
            self.assertFalse(row["rt_core_route_faster_than_best_current_route"], row)
            self.assertGreater(row["optix_numba_slower_than_best_current_route"], 1.0, row)
        self.assertGreater(policy["optix_numba_slower_than_best_range"]["max"], 13.0)
        self.assertGreater(policy["optix_numba_slower_than_best_range"]["min"], 3.0)

    def test_future_rt_native_fused_primitive_is_required_not_implemented(self) -> None:
        future = self.packet["future_rt_native_fused_primitive"]
        readiness = self.packet["readiness"]

        self.assertTrue(future["required"])
        self.assertFalse(future["implemented"])
        self.assertEqual(
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
            future["proposed_contract"],
        )
        self.assertIn("aggregate-frontier row emission", future["must_avoid"])
        self.assertIn("native RT program or equivalent payload accumulation", future["implementation_requirements"])
        self.assertIn("do not drive RT cores", future["why_numba_cuda_is_not_rt_core"])
        self.assertTrue(readiness["internal_v3_clean_target_closed"])
        self.assertFalse(readiness["rt_core_acceleration_closed"])
        self.assertFalse(readiness["rt_core_speedup_claim_authorized"])
        self.assertFalse(readiness["automatic_partner_selection_authorized"])

    def test_m113_is_not_current_barnes_hut_path(self) -> None:
        applicability = self.packet["m113_applicability"]

        self.assertFalse(applicability["current_route_should_use_m113"])
        self.assertIn("fused weighted-vector RT-native primitive", applicability["reason"])
        self.assertIn("without aggregate-frontier row emission", applicability["reason"])

    def test_report_readme_index_and_script_capture_closeout(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4512 / V3 M116", report)
        self.assertIn("RT-core acceleration success", report)
        self.assertIn("Current route should use M113: `False`", report)
        self.assertIn("Goal4512", readme)
        self.assertIn("route-policy target", readme)
        self.assertIn("RT-core acceleration success", readme)
        self.assertIn("Goal4512 Barnes-Hut clean-target audit", index)
        self.assertIn("PACKET_VERSION", script)


if __name__ == "__main__":
    unittest.main()
