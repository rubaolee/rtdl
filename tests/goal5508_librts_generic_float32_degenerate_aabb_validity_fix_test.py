from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.aabb_index import AABB_INDEX_2D_CONTRACT

SOURCE = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
RESULT = ROOT / "Paper-reproduction-apps/librts-paper/results/goal5508_generic_float32_degenerate_aabb_validity_fix_gate.json"


class Goal5508GenericFloat32DegenerateAabbValidityFixTest(unittest.TestCase):
    @staticmethod
    def _selected_index(prim: int, qidx: int, intersect_pass: int) -> int:
        return qidx if intersect_pass == 1 else prim

    @staticmethod
    def _strictly_valid(box: tuple[float, float, float, float]) -> bool:
        min_x, min_y, max_x, max_y = box
        return min_x < max_x and min_y < max_y

    def test_forward_and_backward_select_different_indexed_records(self):
        # The forward pass indexes the primitive record; the reverse pass
        # indexes the query record.  Make the two validity outcomes differ so
        # a prim-only guard cannot pass this contract fixture.
        boxes = (
            (1.0, 0.0, 1.0, 2.0),  # degenerate primitive record
            (0.0, 0.0, 2.0, 2.0),  # valid query record
        )
        self.assertFalse(
            self._strictly_valid(
                boxes[self._selected_index(0, 1, 0)]
            )
        )
        self.assertTrue(
            self._strictly_valid(
                boxes[self._selected_index(0, 1, 1)]
            )
        )

    def test_generic_kernel_checks_indexed_validity_for_both_range_intersection_passes(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("box_is_strictly_valid", source)
        self.assertIn("if (params.operation == 3u)", source)
        self.assertIn("indexed_idx", source)
        self.assertIn("params.intersect_pass == 1u ? qidx : prim", source)
        self.assertIn("params.indexed_boxes[indexed_idx]", source)
        lowered = source.lower()
        self.assertNotIn("librts", lowered)
        self.assertNotIn("rtspatial", lowered)
        self.assertNotIn("paper", lowered)
        self.assertIn("indexed_box_validity", AABB_INDEX_2D_CONTRACT)
        self.assertIn("strict", AABB_INDEX_2D_CONTRACT["indexed_box_validity"])
        self.assertIn("OptiX", AABB_INDEX_2D_CONTRACT["indexed_box_validity"])
        self.assertIn("range_intersects", AABB_INDEX_2D_CONTRACT["indexed_box_validity"])
        self.assertIn("range_contains", AABB_INDEX_2D_CONTRACT["indexed_box_validity"])
        self.assertIn("intersection-only", AABB_INDEX_2D_CONTRACT["indexed_box_validity"])

    def test_official_prefixes_and_degenerate_subsets_match_author(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "generic_float32_degenerate_aabb_validity_fix_completed")
        self.assertTrue(payload["checks"]["official_parks_author_match"])
        self.assertTrue(payload["checks"]["official_lakes_author_match"])
        self.assertTrue(payload["checks"]["degenerate_parks_author_match"])
        self.assertTrue(payload["checks"]["degenerate_lakes_author_match"])
        for row in payload["official_prefix_matrix"]:
            self.assertEqual(row["fixed_delta"], 0)
            self.assertGreater(row["pre_fix_delta"], 0)
        for row in payload["degenerate_subset_matrix"]:
            self.assertEqual(row["invalid_after_float32_count"], 4)
            self.assertEqual(row["author_count"], 0)
            self.assertEqual(row["fixed_rtdl_count"], 0)
            self.assertGreater(row["pre_fix_rtdl_count"], 0)

    def test_claim_boundary_does_not_promote_full_matrix_or_performance(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["generic_native_semantic_fix_claimed"])
        self.assertFalse(boundary["full_official_input_adjudication"])
        self.assertFalse(boundary["complete_range_intersects_matrix_claimed"])
        self.assertFalse(boundary["paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["author_specific_rtdl_core_behavior_authorized"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()
