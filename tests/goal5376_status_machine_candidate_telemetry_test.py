from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _fixture():
    query_points = {
        "ids": np.asarray([10, 11], dtype=np.int64),
        "x": np.asarray([0.0, 2.0], dtype=np.float64),
        "y": np.asarray([0.0, 0.0], dtype=np.float64),
        "z": np.asarray([0.0, 0.0], dtype=np.float64),
    }
    target_points = {
        "ids": np.asarray([200, 201, 202], dtype=np.int64),
        "x": np.asarray([0.0, 1.0, 3.0], dtype=np.float64),
        "y": np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
        "z": np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
    }
    cell_columns = {
        "cell_ids": np.asarray([7], dtype=np.int64),
        "min_x": np.asarray([0.0], dtype=np.float64),
        "min_y": np.asarray([0.0], dtype=np.float64),
        "min_z": np.asarray([0.0], dtype=np.float64),
        "max_x": np.asarray([3.0], dtype=np.float64),
        "max_y": np.asarray([0.0], dtype=np.float64),
        "max_z": np.asarray([0.0], dtype=np.float64),
        "point_begin_offsets": np.asarray([0], dtype=np.int64),
        "point_counts": np.asarray([3], dtype=np.int64),
        "point_row_indices": np.asarray([0, 1, 2], dtype=np.int64),
    }
    return query_points, target_points, cell_columns


def _native_with_status_machine_telemetry(row_capacity: int):
    status_machine = {
        "schema": "rtdl.optix.cell_mbr_nearest_frontier_3d.status_machine_candidate_telemetry.v1",
        "contract": "generic_cell_mbr_frontier_status_machine_candidate",
        "active_in_queue_size": 2,
        "raw_offload_rows_before_sort_reduce": 5,
        "raw_offload_rows_author_width_bytes": 40,
        "status_count_init": 2,
        "status_count_offloading": 5,
        "status_count_aborted": None,
        "miss_queue_count": None,
        "cmax2_mbr_abort_count": None,
        "point_loop_early_break_count": 0,
        "current_best_state_source": "rtdl_inline_payload_initial_none_not_author_cmin2_restore",
        "row_count_parity_against_author_offloading_size": None,
        "explicit_lb_support_claimed": False,
        "row_count_parity_claimed": False,
        "same_denominator_memory_claimed": False,
    }
    return {
        "columns": {
            "frontier_kind_codes": np.asarray([], dtype=np.int64),
            "query_row_ids": np.asarray([], dtype=np.int64),
            "query_point_ids": np.asarray([], dtype=np.int64),
            "cell_ids": np.asarray([], dtype=np.int64),
            "point_begin_offsets": np.asarray([], dtype=np.uint64),
            "point_counts": np.asarray([], dtype=np.uint64),
            "min_distances": np.asarray([], dtype=np.float64),
            "max_distances": np.asarray([], dtype=np.float64),
        },
        "nearest_columns": {
            "source_ids": np.asarray([10, 11], dtype=np.int64),
            "nearest_distances": np.asarray([0.0, 1.0], dtype=np.float64),
            "nearest_item_ids": np.asarray([200, 201], dtype=np.int64),
        },
        "valid_count": 0,
        "attempted_count": 5,
        "row_capacity": int(row_capacity),
        "sort_rows": False,
        "frontier_row_order": "native_unsorted",
        "inline_nearest": True,
        "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5",
        "native_memory_telemetry_collected": True,
        "native_memory_telemetry": {
            "schema": "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v3",
            "raw_frontier_kind2_rows": 5,
            "status_machine_candidate_telemetry": status_machine,
        },
        "status_machine_telemetry_collected": True,
        "status_machine_telemetry": status_machine,
        "global_bound_early_break": True,
        "global_bound_early_break_count": 0,
        "global_bound_distance": 0.0,
        "per_source_witness_exact": True,
    }


class Goal5376StatusMachineCandidateTelemetryTest(unittest.TestCase):
    def test_partner_frontdoor_exposes_status_machine_candidate_telemetry(self) -> None:
        import rtdsl as rt

        query_points, target_points, cell_columns = _fixture()

        def fake_native(**kwargs):
            return _native_with_status_machine_telemetry(kwargs["row_capacity"])

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                target_point_columns=target_points,
                radius=2.0,
                current_best_distances=np.full(2, np.inf, dtype=np.float64),
                current_best_item_ids=np.full(2, -1, dtype=np.int64),
                max_inline_points=8,
                emit_pruned_rows=False,
                sort_rows=False,
                inline_nearest=True,
                global_bound_early_break=True,
                return_split_frontiers=False,
                return_metadata=True,
            )

        telemetry = result["metadata"]["status_machine_telemetry"]
        self.assertTrue(result["metadata"]["status_machine_telemetry_collected"])
        self.assertEqual(
            "generic_cell_mbr_frontier_status_machine_candidate",
            telemetry["contract"],
        )
        self.assertEqual(5, telemetry["raw_offload_rows_before_sort_reduce"])
        self.assertEqual(40, telemetry["raw_offload_rows_author_width_bytes"])
        self.assertIsNone(telemetry["row_count_parity_against_author_offloading_size"])
        self.assertFalse(telemetry["explicit_lb_support_claimed"])
        self.assertFalse(telemetry["same_denominator_memory_claimed"])

    def test_runtime_labels_candidate_as_non_author_lb_support(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        fn_start = runtime.index("def collect_cell_mbr_nearest_frontier_3d_optix")
        fn_end = runtime.index("@dataclass(frozen=True)", fn_start)
        window = runtime[fn_start:fn_end]
        self.assertIn("status_machine_candidate_telemetry.v1", window)
        self.assertIn("generic_cell_mbr_frontier_status_machine_candidate", window)
        self.assertIn("explicit_lb_support_claimed", window)
        self.assertIn("author cmin2/current-best restoration by in_q_idx", window)
        self.assertIn("author X-HD -lb implementation claim", window)


if __name__ == "__main__":
    unittest.main()
