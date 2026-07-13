from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5388ActiveQueryTraceSummaryTest(unittest.TestCase):
    def test_generic_offload_trace_summary_counts_hashes_and_samples_rows(self) -> None:
        import rtdsl as rt

        summary = rt.active_query_status_trace_summary_numpy_columns(
            {
                "active_queue_indices": [10, 10, 11, 12],
                "query_row_ids": [0, 0, 1, 2],
                "source_ids": [100, 100, 101, 102],
                "cell_ids": [50, 51, 60, 70],
                "work_counts": [7, 9, 11, 13],
            },
            active_queue_indices=[10, 11, 12],
            hash_columns=("source_ids", "cell_ids"),
            sample_columns=("source_ids", "cell_ids", "work_counts"),
            return_metadata=True,
        )

        self.assertEqual("rtdl.generic.active_query_status_trace_summary.v1", summary["schema"])
        self.assertEqual(rt.ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT, summary["contract"])
        self.assertEqual("none", summary["app_semantics"])
        self.assertEqual(4, summary["row_count"])
        self.assertEqual(4, summary["status_count_offloading"])
        self.assertEqual(3, summary["active_query_count"])
        self.assertIsInstance(summary["raw_offload_row_hash"], int)
        self.assertEqual(["source_ids", "cell_ids"], summary["hash_columns"])
        self.assertEqual([0, 2, 3], summary["sample_indices"])
        self.assertEqual([100, 101, 102], summary["samples"]["source_ids"])
        self.assertEqual([50, 60, 70], summary["samples"]["cell_ids"])
        self.assertEqual([7, 11, 13], summary["samples"]["work_counts"])

        again = rt.active_query_status_trace_summary_numpy_columns(
            {
                "source_ids": [100, 100, 101, 102],
                "cell_ids": [50, 51, 60, 70],
            },
            hash_columns=("source_ids", "cell_ids"),
        )
        self.assertEqual(summary["raw_offload_row_hash"], again["raw_offload_row_hash"])
        self.assertEqual(
            "fnv1a_u64_over_selected_int64_columns",
            summary["metadata"]["hash_contract"],
        )
        self.assertFalse(summary["metadata"]["explicit_app_option_support_claimed"])

    def test_empty_offload_trace_summary_is_deterministic(self) -> None:
        import rtdsl as rt

        summary = rt.active_query_status_trace_summary_numpy_columns(
            {"source_ids": [], "cell_ids": []},
            hash_columns=("source_ids", "cell_ids"),
            sample_columns=("source_ids", "cell_ids"),
        )
        self.assertEqual(0, summary["row_count"])
        self.assertEqual(0, summary["status_count_offloading"])
        self.assertEqual([], summary["sample_indices"])
        self.assertEqual([], summary["samples"]["source_ids"])
        self.assertEqual(1469598103934665603, summary["raw_offload_row_hash"])

    def test_trace_summary_fails_closed_on_missing_or_invalid_columns(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "missing required columns"):
            rt.active_query_status_trace_summary_numpy_columns(
                {"source_ids": [1, 2]},
                hash_columns=("source_ids", "cell_ids"),
            )

        with self.assertRaisesRegex(ValueError, "same shape"):
            rt.active_query_status_trace_summary_numpy_columns(
                {"source_ids": [1, 2], "cell_ids": [3]},
                hash_columns=("source_ids", "cell_ids"),
            )

        with self.assertRaisesRegex(ValueError, "within the offload row table"):
            rt.active_query_status_trace_summary_numpy_columns(
                {"source_ids": [1, 2], "cell_ids": [3, 4]},
                hash_columns=("source_ids", "cell_ids"),
                sample_indices=[2],
            )

    def test_public_surface_and_app_neutral_source(self) -> None:
        import rtdsl as rt

        self.assertIn("ACTIVE_QUERY_STATUS_TRACE_SUMMARY_CONTRACT", rt.__all__)
        self.assertIn("active_query_status_trace_summary_numpy_columns", rt.__all__)

        source = inspect.getsource(rt.active_query_status_trace_summary_numpy_columns).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
