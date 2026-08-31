from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"
ARTIFACTS = (
    "librts_goal5470_partitioned_range_probe_sparse_gtx1070.json",
    "librts_goal5470_partitioned_range_probe_gtx1070.json",
    "librts_goal5470_partitioned_range_probe_large_gtx1070.json",
    "librts_goal5470_partitioned_range_probe_dense_gtx1070.json",
)


class Goal5470PartitionedAabbNativeSpikeNoGoTest(unittest.TestCase):
    def test_all_matrix_rows_match_and_no_case_clears_the_material_win_gate(self):
        for filename in ARTIFACTS:
            with self.subTest(filename=filename):
                payload = json.loads((RESULTS / filename).read_text(encoding="utf-8"))
                self.assertTrue(payload["decision"]["all_rows_match_k1"])
                self.assertFalse(
                    payload["decision"]["continue_native_partitioned_traversal"]
                )
                self.assertLess(
                    payload["decision"]["best_end_to_end_speedup_vs_k1"], 1.02
                )
                for summary in payload["summaries"].values():
                    self.assertTrue(summary["matches_k1_rows"])
                    self.assertTrue(summary["row_hash_stable"])
                    self.assertTrue(summary["row_count_stable"])

    def test_unpromoted_native_and_public_symbols_are_absent_after_revert(self):
        paths = (
            ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
            ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp",
            ROOT / "src" / "rtdsl" / "optix_runtime.py",
            ROOT / "src" / "rtdsl" / "__init__.py",
        )
        forbidden = (
            "prepare_partitioned_aabb_box_queries_2d",
            "partitioned_range_intersection_rows",
            "backward_ray_intersection_counts",
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
