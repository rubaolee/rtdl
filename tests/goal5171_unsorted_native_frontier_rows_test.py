from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _fixture(query_count: int = 32, cell_count: int = 8):
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


def _empty_native(row_capacity: int, *, sort_rows: bool):
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
        "sort_rows": bool(sort_rows),
        "frontier_row_order": "sorted_unique" if sort_rows else "native_unsorted",
        "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2",
    }


class Goal5171UnsortedNativeFrontierRowsTest(unittest.TestCase):
    def test_partner_forwards_unsorted_native_row_policy(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture()
        calls: list[bool] = []

        def fake_native(**kwargs):
            calls.append(bool(kwargs["sort_rows"]))
            return _empty_native(kwargs["row_capacity"], sort_rows=kwargs["sort_rows"])

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=1.0,
                current_best_distances=np.ones(32),
                current_best_item_ids=np.full(32, -1, dtype=np.int64),
                max_inline_points=8,
                emit_pruned_rows=False,
                sort_rows=False,
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual(calls, [False])
        self.assertEqual(result["metadata"]["frontier_row_order"], "native_unsorted")
        self.assertFalse(result["metadata"]["sort_rows"])
        self.assertEqual(result["row_table"]["metadata"]["frontier_row_order"], "native_unsorted")
        self.assertFalse(result["row_table"]["metadata"]["sort_rows"])
        self.assertEqual(result["metadata"]["native_generic_symbol"], "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2")

    def test_partner_default_preserves_sorted_unique_policy(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture()
        calls: list[bool] = []

        def fake_native(**kwargs):
            calls.append(bool(kwargs["sort_rows"]))
            return _empty_native(kwargs["row_capacity"], sort_rows=kwargs["sort_rows"])

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=1.0,
                current_best_distances=np.ones(32),
                current_best_item_ids=np.full(32, -1, dtype=np.int64),
                max_inline_points=8,
                emit_pruned_rows=False,
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual(calls, [True])
        self.assertEqual(result["metadata"]["frontier_row_order"], "sorted_unique")
        self.assertTrue(result["metadata"]["sort_rows"])

    def test_route_and_matrix_expose_frontier_row_order_policy(self) -> None:
        route_script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")
        matrix_script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_seeded_performance_matrix.py"
        ).read_text(encoding="utf-8")

        for text in (route_script, matrix_script):
            self.assertIn("--frontier-row-order", text)
            self.assertIn("choices=(\"sorted\", \"native\")", text)
            self.assertIn("frontier_row_order", text)

    def test_native_runtime_fail_closed_requires_v2_for_unsorted(self) -> None:
        runtime_source = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        start = runtime_source.index("def collect_cell_mbr_nearest_frontier_3d_optix")
        end = runtime_source.index("@dataclass(frozen=True)", start)
        window = runtime_source[start:end]
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2", window)
        self.assertIn("required when sort_rows=False", window)
        self.assertIn("sort_rows", window)
        self.assertIn("frontier_row_order", window)


if __name__ == "__main__":
    unittest.main()
