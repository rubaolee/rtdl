from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal2813RtnnUnsortedTopKSummaryTest(unittest.TestCase):
    def test_summary_only_f32_paths_use_unsorted_bounded_topk(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("frn_ranked_insert_unsorted_f32", core)
        self.assertIn("frn_ranked_f32_less", core)
        self.assertIn("frn_ranked_f32_worse", core)
        self.assertIn("worst_distance_sq", core)
        self.assertIn("nearest_index", core)
        self.assertIn("kth_index", core)

        summary_start = core.index("fixed_radius_neighbors_3d_grid_ranked_summary_f32")
        direct_start = core.index("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_direct")
        aggregate_start = core.index("fixed_radius_neighbors_3d_grid_compact", direct_start)
        summary_body = core[summary_start:direct_start]
        direct_body = core[direct_start:aggregate_start]

        self.assertIn("frn_ranked_insert_unsorted_f32", summary_body)
        self.assertIn("frn_ranked_insert_unsorted_f32", direct_body)
        self.assertNotIn("frn_ranked_insert_f32(d2", summary_body)
        self.assertNotIn("frn_ranked_insert_f32(d2", direct_body)
        self.assertNotIn("rtnn", core.lower())


if __name__ == "__main__":
    unittest.main()
