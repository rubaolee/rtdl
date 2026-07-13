from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.aabb_index import AABB_INDEX_2D_CONTRACT


SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5519_operation_scoped_aabb_validity_fix_gate.json"


class Goal5519OperationScopedAabbValidityFixTest(unittest.TestCase):
    def test_native_validity_guard_is_range_intersects_only(self):
        source = SOURCE.read_text(encoding="utf-8")
        expected = (
            "if (params.operation == 3u) {\n"
            "        const uint32_t indexed_idx = params.intersect_pass == 1u ? qidx : prim;\n"
            "        if (!box_is_strictly_valid(params.indexed_boxes[indexed_idx])) return;\n"
            "    }"
        )
        self.assertIn(expected, source)
        contract = AABB_INDEX_2D_CONTRACT["indexed_box_validity"]
        self.assertIn("OptiX", contract)
        self.assertIn("range_intersects", contract)
        self.assertIn("point_contains", contract)
        self.assertIn("range_contains", contract)

    def test_exact_lakes_count_and_intersection_regressions_pass(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "generic_operation_scoped_aabb_validity_regression_fixed")
        self.assertEqual(payload["root_cause"]["delta"], 79)
        self.assertTrue(payload["corrected_exact_case"]["matched"])
        self.assertEqual(payload["corrected_exact_case"]["author_count"], 101418)
        self.assertEqual(payload["corrected_exact_case"]["fixed_rtdl_count"], 101418)
        self.assertEqual(
            payload["generic_regressions"]["operation_discriminating_counts"],
            {"point_contains": 1, "range_contains": 1, "range_intersects": 0},
        )
        self.assertEqual(payload["generic_regressions"]["range_intersects_prefix_count"], 34581812)
        self.assertEqual(payload["generic_regressions"]["range_intersects_degenerate_count"], 0)
        self.assertTrue(all(payload["checks"].values()))

    def test_claim_boundary_remains_bounded_and_app_neutral(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["generic_native_semantic_fix_claimed"])
        self.assertFalse(boundary["complete_range_contains_matrix_claimed"])
        self.assertFalse(boundary["pointwise_relation_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_specific_rtdl_core_behavior_authorized"])
        source = SOURCE.read_text(encoding="utf-8").lower()
        self.assertNotIn("librts", source)
        self.assertNotIn("rtspatial", source)


if __name__ == "__main__":
    unittest.main()
