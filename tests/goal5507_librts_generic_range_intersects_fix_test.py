from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"


class Goal5507LibrtsGenericRangeIntersectsFixTest(unittest.TestCase):
    def test_native_contract_uses_generic_two_direction_float32_rule(self) -> None:
        source = KERNEL.read_text(encoding="utf-8")
        self.assertIn("trace_aabb_index_segment(q.max_x, q.min_y, q.min_x, q.max_y, idx)", source)
        self.assertIn("trace_aabb_index_segment(indexed.min_x, indexed.min_y, indexed.max_x, indexed.max_y, idx)", source)
        self.assertIn("query_diagonal_hits_indexed && !indexed_diagonal_hits_query", source)
        self.assertIn("const float tmax_limit = 1.00000011920928955078f", source)
        self.assertIn("const float t_far_scale = 1.00000071525573730469f", source)

    def test_core_source_contains_no_librts_identity(self) -> None:
        source = KERNEL.read_text(encoding="utf-8").lower()
        self.assertNotIn("librts", source)
        self.assertNotIn("rtspatial", source)
        self.assertNotIn("paper", source)


if __name__ == "__main__":
    unittest.main()
