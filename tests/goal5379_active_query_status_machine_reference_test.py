from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5379ActiveQueryStatusMachineReferenceTest(unittest.TestCase):
    def test_reference_emits_completed_offload_miss_and_abort_rows(self) -> None:
        import rtdsl as rt

        result = rt.active_query_status_machine_reference_numpy_columns(
            query_row_ids=[0, 1, 2, 3, 4],
            active_queue_indices=[10, 11, 12, 13, 14],
            source_ids=[100, 101, 102, 103, 104],
            current_best_sq=[10.0, np.inf, 5.0, 8.0, np.inf],
            current_best_item_ids=[1000, -1, 1002, 1003, -1],
            candidate_query_row_ids=[0, 1, 2, 3],
            candidate_cell_ids=[50, 51, 52, 53],
            candidate_min_sq=[1.0, 1.0, 6.0, 0.2],
            candidate_max_sq=[4.0, 10.0, 7.0, 1.5],
            candidate_work_counts=[3, 9, 1, 2],
            candidate_exact_best_sq=[2.0, np.inf, 4.0, 0.5],
            candidate_exact_item_ids=[900, -1, 902, 903],
            heavy_threshold=5,
            radius_sq=100.0,
            global_bound_sq=2.0,
            return_metadata=True,
        )

        self.assertEqual(result["metadata"]["contract"], rt.ACTIVE_QUERY_STATUS_MACHINE_CONTRACT)
        self.assertEqual(result["metadata"]["app_semantics"], "none")
        self.assertFalse(result["metadata"]["explicit_app_option_support_claimed"])

        self.assertEqual(result["offload_rows"]["active_queue_indices"].tolist(), [11])
        self.assertEqual(result["offload_rows"]["query_row_ids"].tolist(), [1])
        self.assertEqual(result["offload_rows"]["cell_ids"].tolist(), [51])
        self.assertEqual(result["offload_rows"]["work_counts"].tolist(), [9])

        self.assertEqual(result["completed_rows"]["active_queue_indices"].tolist(), [10, 12])
        self.assertEqual(result["completed_rows"]["nearest_item_ids"].tolist(), [900, 1002])
        self.assertEqual(result["completed_rows"]["nearest_distance_sq"].tolist(), [2.0, 5.0])

        self.assertEqual(result["miss_rows"]["active_queue_indices"].tolist(), [14])
        self.assertEqual(result["miss_rows"]["status_codes"].tolist(), [rt.ACTIVE_QUERY_STATUS_KIND_CODES["miss"]])

        self.assertEqual(result["aborted_rows"]["active_queue_indices"].tolist(), [13])
        self.assertEqual(result["aborted_rows"]["status_codes"].tolist(), [rt.ACTIVE_QUERY_STATUS_KIND_CODES["aborted"]])

        telemetry = result["telemetry"]
        self.assertEqual(telemetry["offload_row_count"], 1)
        self.assertEqual(telemetry["completed_row_count"], 2)
        self.assertEqual(telemetry["miss_row_count"], 1)
        self.assertEqual(telemetry["aborted_row_count"], 1)
        self.assertEqual(telemetry["pruned_by_radius_or_current_best_count"], 1)
        self.assertFalse(telemetry["overflowed"])

    def test_feedback_updates_active_query_state_by_queue_index(self) -> None:
        import rtdsl as rt

        feedback = rt.apply_active_query_feedback_numpy_columns(
            active_queue_indices=[10, 11, 12],
            current_best_sq=[5.0, np.inf, 3.0],
            current_best_item_ids=[500, -1, 300],
            feedback_active_queue_indices=[11, 12],
            feedback_best_sq=[4.0, 3.0],
            feedback_item_ids=[400, 250],
            return_metadata=True,
        )

        columns = feedback["columns"]
        self.assertEqual(columns["active_queue_indices"].tolist(), [10, 11, 12])
        self.assertEqual(columns["current_best_sq"].tolist(), [5.0, 4.0, 3.0])
        self.assertEqual(columns["current_best_item_ids"].tolist(), [500, 400, 250])
        self.assertEqual(feedback["metadata"]["feedback_updates_applied"], 2)
        self.assertEqual(feedback["metadata"]["app_semantics"], "none")

    def test_reference_preserves_multiple_offload_rows_for_one_active_query(self) -> None:
        import rtdsl as rt

        result = rt.active_query_status_machine_reference_numpy_columns(
            query_row_ids=[0],
            active_queue_indices=[10],
            source_ids=[100],
            current_best_sq=[np.inf],
            current_best_item_ids=[-1],
            candidate_query_row_ids=[0, 0, 0],
            candidate_cell_ids=[50, 51, 52],
            candidate_min_sq=[1.0, 2.0, 3.0],
            candidate_max_sq=[4.0, 5.0, 6.0],
            candidate_work_counts=[9, 10, 11],
            heavy_threshold=5,
            return_metadata=True,
        )

        self.assertEqual(result["offload_rows"]["active_queue_indices"].tolist(), [10, 10, 10])
        self.assertEqual(result["offload_rows"]["cell_ids"].tolist(), [50, 51, 52])
        self.assertEqual(result["updated_state"]["status_codes"].tolist(), [rt.ACTIVE_QUERY_STATUS_KIND_CODES["offload"]])
        self.assertEqual(result["telemetry"]["offload_row_count"], 3)
        self.assertEqual(result["telemetry"]["completed_row_count"], 0)
        self.assertEqual(result["telemetry"]["miss_row_count"], 0)

    def test_overflow_fails_closed_without_partial_output_rows(self) -> None:
        import rtdsl as rt

        result = rt.active_query_status_machine_reference_numpy_columns(
            query_row_ids=[0, 1, 2],
            active_queue_indices=[10, 11, 12],
            source_ids=[100, 101, 102],
            current_best_sq=[1.0, np.inf, np.inf],
            current_best_item_ids=[200, -1, -1],
            candidate_query_row_ids=[1, 2],
            candidate_cell_ids=[51, 52],
            candidate_min_sq=[0.0, 0.0],
            candidate_max_sq=[10.0, 10.0],
            candidate_work_counts=[8, 9],
            heavy_threshold=5,
            row_capacity=2,
            return_metadata=True,
        )

        self.assertTrue(result["telemetry"]["overflowed"])
        self.assertEqual(result["telemetry"]["attempted_output_row_count"], 3)
        self.assertEqual(result["telemetry"]["emitted_output_row_count"], 0)
        for section in ("offload_rows", "completed_rows", "miss_rows", "aborted_rows"):
            for array in result[section].values():
                self.assertEqual(array.size, 0)

    def test_unknown_feedback_and_candidate_rows_fail_closed(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "feedback active queue index"):
            rt.apply_active_query_feedback_numpy_columns(
                active_queue_indices=[10],
                current_best_sq=[1.0],
                current_best_item_ids=[100],
                feedback_active_queue_indices=[99],
                feedback_best_sq=[0.5],
                feedback_item_ids=[50],
            )

        with self.assertRaisesRegex(ValueError, "candidate query row id"):
            rt.active_query_status_machine_reference_numpy_columns(
                query_row_ids=[0],
                active_queue_indices=[10],
                source_ids=[100],
                current_best_sq=[np.inf],
                current_best_item_ids=[-1],
                candidate_query_row_ids=[99],
                candidate_cell_ids=[51],
                candidate_min_sq=[0.0],
                candidate_max_sq=[1.0],
                candidate_work_counts=[1],
                heavy_threshold=5,
            )

    def test_public_surface_and_app_neutral_source(self) -> None:
        import rtdsl as rt

        for name in (
            "ACTIVE_QUERY_STATUS_MACHINE_CONTRACT",
            "ACTIVE_QUERY_STATUS_KIND_CODES",
            "ACTIVE_QUERY_ABORT_REASON_CODES",
            "ACTIVE_QUERY_OFFLOAD_ROW_SCHEMA",
            "ACTIVE_QUERY_TERMINAL_ROW_SCHEMA",
            "active_query_status_machine_reference_numpy_columns",
            "apply_active_query_feedback_numpy_columns",
        ):
            self.assertIn(name, rt.__all__)

        source = inspect.getsource(rt.active_query_status_machine_reference_numpy_columns).lower()
        feedback_source = inspect.getsource(rt.apply_active_query_feedback_numpy_columns).lower()
        for text in (source, feedback_source):
            for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
