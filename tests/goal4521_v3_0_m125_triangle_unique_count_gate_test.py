from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4521_v3_0_m125_triangle_unique_count_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4521_v3_0_m125_triangle_unique_count_gate_2026-06-17.md"
README = ROOT / "examples/benchmark_apps/triangle_counting/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4521_m125_triangle_unique_count_gate.py"
SOURCE = ROOT / "src/rtdsl/v3_0_prepared_graph_chunk_executor.py"
INIT = ROOT / "src/rtdsl/__init__.py"


class Goal4521V30M125TriangleUniqueCountGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_scalar_unique_counts_fail_when_duplicate_keys_cross_chunks(self) -> None:
        counterexample = self.packet["associativity_counterexample"]
        self.assertEqual(5, counterexample["scalar_chunk_sum"])
        self.assertEqual(4, counterexample["global_unique_count"])
        self.assertFalse(counterexample["scalar_sum_matches_global_unique"])
        self.assertEqual(1, counterexample["cross_chunk_duplicate_delta"])
        self.assertTrue(counterexample["associative_merge_validated"])

    def test_generic_key_payload_merge_is_associative_and_exported(self) -> None:
        left = {"keys": ((1, 2), (1, 3)), "counts": (1, 1)}
        middle = {"keys": ((1, 3), (2, 4)), "counts": (1, 1)}
        right = {"keys": ((3, 5),), "counts": (1,)}
        all_at_once = rt.combine_v3_chunked_unique_count_key_payloads((left, middle, right))
        left_middle = rt.combine_v3_chunked_unique_count_key_payloads((left, middle))
        regrouped = rt.combine_v3_chunked_unique_count_key_payloads((
            {"keys": left_middle["unique_keys"], "counts": left_middle["counts"]},
            right,
        ))
        self.assertEqual(all_at_once["unique_keys"], regrouped["unique_keys"])
        self.assertEqual(all_at_once["counts"], regrouped["counts"])
        self.assertEqual(4, all_at_once["unique_key_count"])
        self.assertEqual(5, all_at_once["total_weight"])
        self.assertTrue(hasattr(rt, "assess_v3_chunked_unique_count_continuation_readiness"))
        self.assertTrue(hasattr(rt, "validate_v3_chunked_unique_count_continuation_readiness"))

    def test_current_triangle_gate_stays_blocked_but_generic_future_gate_can_plan(self) -> None:
        current = self.packet["current_triangle_validation"]
        future = self.packet["future_generic_payload_validation"]
        self.assertFalse(current["ready_for_m113_plan"])
        self.assertEqual(
            [
                "prepared_graph_capture_not_validated",
                "missing_key_count_payload",
                "chunk_boundary_duplicate_handling_not_associative",
            ],
            current["blockers"],
        )
        self.assertFalse(current["associative_duplicate_policy_available"])
        self.assertTrue(future["ready_for_m113_plan"])
        self.assertTrue(future["associative_duplicate_policy_available"])
        self.assertEqual("chunked_partner_continuation_required", future["plan_status"])
        self.assertEqual(3, future["chunk_count"])

    def test_report_docs_source_and_script_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertIn("Goal4521 / V3 M125", report)
        self.assertIn("Scalar sum matches global unique: `False`", report)
        self.assertIn("Goal4521", readme)
        self.assertIn("Goal4521 Triangle unique-count gate", index)
        self.assertIn("PACKET_VERSION", script)
        self.assertIn("combine_v3_chunked_unique_count_key_payloads", source)
        self.assertIn("assess_v3_chunked_unique_count_continuation_readiness", init)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["m113_promotion_authorized_for_current_triangle"])
        self.assertFalse(boundary["app_specific_native_callback_required"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
