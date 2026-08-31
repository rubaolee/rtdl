from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _fixture(query_count: int = 200, cell_count: int = 20):
    query_points = {
        "ids": list(range(1000, 1000 + query_count)),
        "x": np.linspace(0.0, 1.0, query_count),
        "y": np.zeros(query_count),
        "z": np.zeros(query_count),
    }
    cell_columns = {
        "cell_ids": np.arange(cell_count, dtype=np.int64),
        "point_begin_offsets": np.arange(cell_count, dtype=np.int64),
        "point_counts": np.ones(cell_count, dtype=np.int64),
        "min_x": np.linspace(0.0, 1.0, cell_count),
        "max_x": np.linspace(0.0, 1.0, cell_count) + 0.01,
        "min_y": np.zeros(cell_count),
        "max_y": np.ones(cell_count) * 0.01,
        "min_z": np.zeros(cell_count),
        "max_z": np.ones(cell_count) * 0.01,
    }
    return query_points, cell_columns


def _empty_native(row_capacity: int):
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
        "valid_count": 0,
        "attempted_count": 0,
        "row_capacity": int(row_capacity),
        "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d",
    }


class Goal5169StreamingFrontierCapacityRetryTest(unittest.TestCase):
    def test_streaming_default_uses_smaller_inferred_capacity(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture(query_count=200, cell_count=20)
        calls: list[int] = []

        def fake_native(**kwargs):
            calls.append(int(kwargs["row_capacity"]))
            return _empty_native(kwargs["row_capacity"])

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=1.0,
                current_best_distances=np.ones(200),
                current_best_item_ids=np.full(200, -1, dtype=np.int64),
                max_inline_points=8,
                emit_pruned_rows=False,
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual(calls, [1600])
        self.assertEqual(result["metadata"]["full_row_capacity"], 4000)
        self.assertEqual(result["metadata"]["row_capacity"], 1600)
        self.assertEqual(result["metadata"]["row_capacity_policy"], "streaming_inferred_retry")
        self.assertEqual(result["metadata"]["row_capacity_attempts"], (1600,))

    def test_streaming_inferred_capacity_retries_fail_closed_overflow(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture(query_count=200, cell_count=20)
        calls: list[int] = []

        def fake_native(**kwargs):
            capacity = int(kwargs["row_capacity"])
            calls.append(capacity)
            if capacity < 3000:
                raise RuntimeError(
                    "OptiX cell-MBR nearest frontier 3D output overflowed; "
                    f"attempted 3000; capacity {capacity}; "
                    "failure_mode=fail_closed_overflow; partial_result_returned=False"
                )
            return _empty_native(capacity)

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=1.0,
                current_best_distances=np.ones(200),
                current_best_item_ids=np.full(200, -1, dtype=np.int64),
                max_inline_points=8,
                emit_pruned_rows=False,
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual(calls, [1600, 3200])
        self.assertEqual(result["metadata"]["row_capacity"], 3200)
        self.assertEqual(result["metadata"]["row_capacity_attempts"], (1600, 3200))

    def test_explicit_capacity_still_fails_closed_without_retry(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture(query_count=200, cell_count=20)
        calls: list[int] = []

        def fake_native(**kwargs):
            calls.append(int(kwargs["row_capacity"]))
            raise RuntimeError(
                "OptiX cell-MBR nearest frontier 3D output overflowed; "
                "failure_mode=fail_closed_overflow; partial_result_returned=False"
            )

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            with self.assertRaisesRegex(RuntimeError, "overflowed"):
                rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                    query_points,
                    cell_columns,
                    radius=1.0,
                    current_best_distances=np.ones(200),
                    current_best_item_ids=np.full(200, -1, dtype=np.int64),
                    max_inline_points=8,
                    row_capacity=10,
                    emit_pruned_rows=False,
                    return_split_frontiers=False,
                )

        self.assertEqual(calls, [10])

    def test_frontier_capacity_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_res4full_goal5169_frontier_capacity_matrix_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5169 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        case = {case["case"]: case for case in payload["cases"]}["res4full"]
        self.assertTrue(case["matched"])
        self.assertEqual(case["rtdl"]["validation_mode"], "author-only")
        self.assertGreater(case["rtdl"]["route_sec_median"], 0.0)
        self.assertIsNone(case["ratio_policy"]["author_avg_vs_rtdl_route_ratio"])


if __name__ == "__main__":
    unittest.main()
