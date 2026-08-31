from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5384MultiroundActiveQueryStatusTest(unittest.TestCase):
    def test_multiround_reference_carries_offload_feedback_to_next_round(self) -> None:
        import rtdsl as rt

        result = rt.active_query_status_multiround_reference_numpy_columns(
            query_row_ids=[0, 1, 2],
            active_queue_indices=[10, 11, 12],
            source_ids=[100, 101, 102],
            current_best_sq=[np.inf, np.inf, 1.0],
            current_best_item_ids=[-1, -1, 200],
            round_candidate_tables=[
                {
                    "candidate_query_row_ids": [0, 1],
                    "candidate_cell_ids": [50, 51],
                    "candidate_min_sq": [0.5, 1.0],
                    "candidate_max_sq": [3.0, 8.0],
                    "candidate_work_counts": [2, 9],
                    "candidate_exact_best_sq": [3.0, np.inf],
                    "candidate_exact_item_ids": [300, -1],
                    "feedback_active_queue_indices": [11],
                    "feedback_best_sq": [2.5],
                    "feedback_item_ids": [250],
                },
                {
                    "candidate_query_row_ids": [1],
                    "candidate_cell_ids": [52],
                    "candidate_min_sq": [0.25],
                    "candidate_max_sq": [3.0],
                    "candidate_work_counts": [1],
                    "candidate_exact_best_sq": [2.0],
                    "candidate_exact_item_ids": [220],
                },
            ],
            heavy_threshold=5,
            return_metadata=True,
        )

        self.assertEqual(result["metadata"]["contract"], rt.ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT)
        self.assertEqual(result["metadata"]["single_round_contract"], rt.ACTIVE_QUERY_STATUS_MACHINE_CONTRACT)
        self.assertEqual(result["metadata"]["app_semantics"], "none")
        self.assertFalse(result["metadata"]["explicit_app_option_support_claimed"])

        telemetry = result["telemetry"]
        self.assertEqual(telemetry["round_count"], 2)
        self.assertEqual(telemetry["initial_active_query_count"], 3)
        self.assertEqual(telemetry["final_active_query_count"], 0)
        self.assertEqual(telemetry["raw_offload_rows_before_sort_reduce"], 1)
        self.assertEqual(telemetry["completed_row_count"], 3)
        self.assertEqual(telemetry["miss_queue_count"], 0)
        self.assertEqual(telemetry["feedback_row_count"], 1)
        self.assertEqual(telemetry["feedback_updates_applied"], 1)
        self.assertEqual(
            telemetry["rounds"],
            [
                {
                    "round_index": 0,
                    "active_query_count": 3,
                    "candidate_row_count": 2,
                    "offload_row_count": 1,
                    "completed_row_count": 2,
                    "miss_row_count": 0,
                    "aborted_row_count": 0,
                    "feedback_row_count": 1,
                    "feedback_updates_applied": 1,
                    "next_active_query_count": 1,
                },
                {
                    "round_index": 1,
                    "active_query_count": 1,
                    "candidate_row_count": 1,
                    "offload_row_count": 0,
                    "completed_row_count": 1,
                    "miss_row_count": 0,
                    "aborted_row_count": 0,
                    "feedback_row_count": 0,
                    "feedback_updates_applied": 0,
                    "next_active_query_count": 0,
                },
            ],
        )

        self.assertEqual(result["offload_rows"]["active_queue_indices"].tolist(), [11])
        self.assertEqual(result["offload_rows"]["cell_ids"].tolist(), [51])
        self.assertEqual(result["completed_rows"]["active_queue_indices"].tolist(), [10, 12, 11])
        self.assertEqual(result["completed_rows"]["nearest_item_ids"].tolist(), [300, 200, 220])
        self.assertEqual(result["completed_rows"]["nearest_distance_sq"].tolist(), [3.0, 1.0, 2.0])

    def test_feedback_shape_and_continue_status_fail_closed(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "feedback rows require"):
            rt.active_query_status_multiround_reference_numpy_columns(
                query_row_ids=[0],
                active_queue_indices=[10],
                source_ids=[100],
                current_best_sq=[np.inf],
                current_best_item_ids=[-1],
                round_candidate_tables=[
                    {
                        "candidate_query_row_ids": [0],
                        "candidate_cell_ids": [50],
                        "candidate_min_sq": [0.0],
                        "candidate_max_sq": [1.0],
                        "candidate_work_counts": [9],
                        "feedback_active_queue_indices": [10],
                    }
                ],
                heavy_threshold=5,
            )

        with self.assertRaisesRegex(ValueError, "unknown continue status kind"):
            rt.active_query_status_multiround_reference_numpy_columns(
                query_row_ids=[0],
                active_queue_indices=[10],
                source_ids=[100],
                current_best_sq=[np.inf],
                current_best_item_ids=[-1],
                round_candidate_tables=[
                    {
                        "candidate_query_row_ids": [0],
                        "candidate_cell_ids": [50],
                        "candidate_min_sq": [0.0],
                        "candidate_max_sq": [1.0],
                        "candidate_work_counts": [9],
                    }
                ],
                heavy_threshold=5,
                continue_status_kinds=("retry_later",),
            )

    def test_public_surface_and_app_neutral_source(self) -> None:
        import rtdsl as rt

        self.assertIn("ACTIVE_QUERY_MULTIROUND_STATUS_CONTRACT", rt.__all__)
        self.assertIn("active_query_status_multiround_reference_numpy_columns", rt.__all__)

        source = inspect.getsource(rt.active_query_status_multiround_reference_numpy_columns).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
