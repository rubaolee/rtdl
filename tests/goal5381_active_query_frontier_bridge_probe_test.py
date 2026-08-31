from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))


class Goal5381ActiveQueryFrontierBridgeProbeTest(unittest.TestCase):
    def test_bridge_summary_compares_to_author_oracle_without_claiming_lb(self) -> None:
        import run_xhd_active_query_frontier_bridge_probe as probe

        source_columns = {
            "ids": np.asarray([100, 101, 102], dtype=np.int64),
        }
        native_frontier = {
            "nearest_state": {
                "query_point_ids": np.asarray([100, 101, 102], dtype=np.int64),
                "current_best_distances": np.asarray([1.0, np.inf, 2.0], dtype=np.float64),
                "current_best_item_ids": np.asarray([200, -1, 202], dtype=np.int64),
            },
            "row_table": {
                "columns": {
                    "frontier_kind_codes": np.asarray([2, 2], dtype=np.int64),
                    "query_row_ids": np.asarray([0, 1], dtype=np.int64),
                    "query_point_ids": np.asarray([100, 101], dtype=np.int64),
                    "cell_ids": np.asarray([50, 51], dtype=np.int64),
                    "point_begin_offsets": np.asarray([0, 8], dtype=np.uint64),
                    "point_counts": np.asarray([9, 10], dtype=np.uint64),
                    "min_distances": np.asarray([0.5, 0.6], dtype=np.float64),
                    "max_distances": np.asarray([2.0, 3.0], dtype=np.float64),
                }
            },
        }
        author_oracle = {
            "active_in_queue_size": 3,
            "raw_offload_rows_before_sort_reduce": 5,
            "raw_offload_rows_author_width_bytes": 40,
        }

        summary = probe.bridge_status_summary_from_native_frontier(
            source_columns=source_columns,
            native_frontier=native_frontier,
            max_inline_points=8,
            author_oracle=author_oracle,
        )

        self.assertEqual(summary["bridge_contract"], "generic_active_query_status_from_frontier_rows_v1")
        self.assertEqual(summary["offload_row_count"], 2)
        self.assertEqual(summary["completed_row_count"], 1)
        self.assertEqual(summary["miss_row_count"], 0)
        trace_summary = summary["trace_summary"]
        self.assertEqual("generic_active_query_status_trace_summary_v1", trace_summary["contract"])
        self.assertEqual(2, trace_summary["row_count"])
        self.assertEqual(3, trace_summary["active_query_count"])
        self.assertEqual([0, 1], trace_summary["sample_indices"])
        self.assertEqual([100, 101], trace_summary["samples"]["source_ids"])
        self.assertEqual([50, 51], trace_summary["samples"]["cell_ids"])
        comparison = summary["comparison_to_author"]
        self.assertTrue(comparison["active_query_count_parity"])
        self.assertEqual(comparison["author_raw_offload_rows_before_sort_reduce"], 5)
        self.assertEqual(comparison["rtdl_bridge_offload_rows"], 2)
        self.assertEqual(comparison["row_delta_author_minus_rtdl_bridge"], 3)
        self.assertFalse(comparison["row_count_parity"])
        self.assertEqual(comparison["rtdl_bridge_author_width_bytes"], 16)
        self.assertFalse(comparison["author_width_byte_parity"])
        self.assertFalse(comparison["hash_comparable_to_author"])
        self.assertFalse(comparison["sample_comparable_to_author"])
        self.assertFalse(summary["claim_boundary"]["explicit_lb_support_claimed"])
        self.assertFalse(summary["claim_boundary"]["row_count_parity_claimed"])
        self.assertFalse(summary["claim_boundary"]["hash_sample_parity_claimed"])

    def test_probe_script_keeps_claim_boundary_false_and_uses_generic_bridge(self) -> None:
        script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_active_query_frontier_bridge_probe.py"
        ).read_text(encoding="utf-8")
        self.assertIn("active_query_status_from_frontier_row_table_numpy_columns", script)
        self.assertIn("active_query_status_trace_summary_numpy_columns", script)
        self.assertIn('"explicit_lb_support_claimed": False', script)
        self.assertIn('"row_count_parity_claimed": False', script)
        self.assertIn('"hash_sample_parity_claimed": False', script)
        self.assertIn('"source_limited_smoke_claimed_as_author_oracle_parity": False', script)
        self.assertIn("--source-limit", script)
        self.assertIn("Goal5374 author oracle", script)


if __name__ == "__main__":
    unittest.main()
