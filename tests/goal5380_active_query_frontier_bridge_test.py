from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5380ActiveQueryFrontierBridgeTest(unittest.TestCase):
    def test_frontier_rows_lower_to_active_query_status_rows(self) -> None:
        import rtdsl as rt

        frontier = {
            "columns": {
                "frontier_kind_codes": np.asarray([1, 2, 3], dtype=np.int64),
                "query_row_ids": np.asarray([0, 1, 3], dtype=np.int64),
                "query_point_ids": np.asarray([100, 101, 103], dtype=np.int64),
                "cell_ids": np.asarray([50, 51, 53], dtype=np.int64),
                "point_begin_offsets": np.asarray([0, 8, 21], dtype=np.uint64),
                "point_counts": np.asarray([3, 9, 1], dtype=np.uint64),
                "min_distances": np.asarray([1.0, 1.0, 0.5], dtype=np.float64),
                "max_distances": np.asarray([2.0, 4.0, 1.0], dtype=np.float64),
            }
        }

        result = rt.active_query_status_from_frontier_row_table_numpy_columns(
            query_row_ids=[0, 1, 2, 3, 4],
            active_queue_indices=[10, 11, 12, 13, 14],
            source_ids=[100, 101, 102, 103, 104],
            current_best_sq=[10.0, np.inf, np.inf, 8.0, np.inf],
            current_best_item_ids=[1000, -1, -1, 1003, -1],
            frontier_row_table=frontier,
            candidate_exact_best_sq=[2.0, np.inf, np.inf],
            candidate_exact_item_ids=[900, -1, -1],
            heavy_threshold=5,
            global_bound_sq=1.0,
            return_metadata=True,
        )

        self.assertEqual(result["metadata"]["contract"], rt.ACTIVE_QUERY_FRONTIER_BRIDGE_CONTRACT)
        self.assertEqual(result["metadata"]["reference_contract"], rt.ACTIVE_QUERY_STATUS_MACHINE_CONTRACT)
        self.assertEqual(result["metadata"]["app_semantics"], "none")
        self.assertEqual(result["metadata"]["frontier_row_count"], 3)
        self.assertEqual(result["metadata"]["frontier_kind_codes_observed"], (1, 2, 3))
        self.assertFalse(result["metadata"]["explicit_app_option_support_claimed"])

        self.assertEqual(result["completed_rows"]["active_queue_indices"].tolist(), [10])
        self.assertEqual(result["completed_rows"]["nearest_item_ids"].tolist(), [900])
        self.assertEqual(result["completed_rows"]["nearest_distance_sq"].tolist(), [2.0])

        self.assertEqual(result["offload_rows"]["active_queue_indices"].tolist(), [11])
        self.assertEqual(result["offload_rows"]["cell_ids"].tolist(), [51])
        self.assertEqual(result["offload_rows"]["work_counts"].tolist(), [9])
        self.assertEqual(result["offload_rows"]["lower_bounds_sq"].tolist(), [1.0])
        self.assertEqual(result["offload_rows"]["upper_bounds_sq"].tolist(), [16.0])

        self.assertEqual(result["aborted_rows"]["active_queue_indices"].tolist(), [13])
        self.assertEqual(
            result["aborted_rows"]["status_codes"].tolist(),
            [rt.ACTIVE_QUERY_STATUS_KIND_CODES["aborted"]],
        )

        self.assertEqual(result["miss_rows"]["active_queue_indices"].tolist(), [12, 14])
        self.assertEqual(
            result["miss_rows"]["status_codes"].tolist(),
            [rt.ACTIVE_QUERY_STATUS_KIND_CODES["miss"], rt.ACTIVE_QUERY_STATUS_KIND_CODES["miss"]],
        )

        telemetry = result["telemetry"]
        self.assertEqual(telemetry["active_query_count"], 5)
        self.assertEqual(telemetry["candidate_row_count"], 3)
        self.assertEqual(telemetry["completed_row_count"], 1)
        self.assertEqual(telemetry["offload_row_count"], 1)
        self.assertEqual(telemetry["aborted_row_count"], 1)
        self.assertEqual(telemetry["miss_row_count"], 2)

    def test_frontier_bridge_fails_closed_on_bad_columns(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "missing required columns"):
            rt.active_query_status_from_frontier_row_table_numpy_columns(
                query_row_ids=[0],
                active_queue_indices=[10],
                source_ids=[100],
                current_best_sq=[np.inf],
                current_best_item_ids=[-1],
                frontier_row_table={"columns": {"query_row_ids": np.asarray([0])}},
                heavy_threshold=5,
            )

        with self.assertRaisesRegex(ValueError, "frontier max distances"):
            rt.active_query_status_from_frontier_row_table_numpy_columns(
                query_row_ids=[0],
                active_queue_indices=[10],
                source_ids=[100],
                current_best_sq=[np.inf],
                current_best_item_ids=[-1],
                frontier_row_table={
                    "columns": {
                        "query_row_ids": np.asarray([0], dtype=np.int64),
                        "cell_ids": np.asarray([50], dtype=np.int64),
                        "point_counts": np.asarray([1], dtype=np.uint64),
                        "min_distances": np.asarray([2.0], dtype=np.float64),
                        "max_distances": np.asarray([1.0], dtype=np.float64),
                    }
                },
                heavy_threshold=5,
            )

    def test_public_surface_and_app_neutral_source(self) -> None:
        import rtdsl as rt

        self.assertIn("ACTIVE_QUERY_FRONTIER_BRIDGE_CONTRACT", rt.__all__)
        self.assertIn("active_query_status_from_frontier_row_table_numpy_columns", rt.__all__)

        source = inspect.getsource(rt.active_query_status_from_frontier_row_table_numpy_columns).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
