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


def _empty_inline_native(row_capacity: int):
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
        "attempted_count": 0,
        "row_capacity": int(row_capacity),
        "sort_rows": False,
        "frontier_row_order": "native_unsorted",
        "inline_nearest": True,
        "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3",
    }


class Goal5172NativeInlineNearestFrontierTest(unittest.TestCase):
    def test_partner_passes_target_columns_and_uses_native_nearest_state(self) -> None:
        import rtdsl as rt

        query_points, target_points, cell_columns = _fixture()
        calls = []

        def fake_native(**kwargs):
            calls.append(kwargs)
            return _empty_inline_native(kwargs["row_capacity"])

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
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertTrue(call["inline_nearest"])
        self.assertFalse(call["sort_rows"])
        np.testing.assert_array_equal(call["target_point_ids"], target_points["ids"])
        np.testing.assert_allclose(call["target_coords"], np.column_stack((target_points["x"], target_points["y"], target_points["z"])))
        np.testing.assert_array_equal(call["point_row_indices"], cell_columns["point_row_indices"].astype(np.uint64))
        np.testing.assert_allclose(result["nearest_state"]["current_best_distances"], [0.0, 1.0])
        np.testing.assert_array_equal(result["nearest_state"]["current_best_item_ids"], [200, 201])
        self.assertTrue(result["metadata"]["inline_nearest"])
        self.assertEqual(result["metadata"]["native_generic_symbol"], "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3")
        self.assertEqual(result["row_table"]["metadata"]["inline_nearest"], True)

    def test_runtime_requires_v3_for_inline_nearest(self) -> None:
        runtime_source = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        start = runtime_source.index("def collect_cell_mbr_nearest_frontier_3d_optix")
        end = runtime_source.index("@dataclass(frozen=True)", start)
        window = runtime_source[start:end]
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3", window)
        self.assertIn("required when inline_nearest=True", window)
        self.assertIn("nearest_columns", window)

    def test_route_and_matrix_expose_frontier_inline_nearest(self) -> None:
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
            self.assertIn("--frontier-inline-nearest", text)
            self.assertIn("frontier_inline_nearest", text)
        self.assertIn('frontier_state = frontier["nearest_state"]', route_script)

    def test_native_api_declares_v3_inline_nearest_outputs(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3", prelude)
        self.assertIn("double* nearest_distances_out", prelude)
        self.assertIn("int64_t* nearest_item_ids_out", prelude)
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3", api)
        self.assertIn("inline_nearest", api)


if __name__ == "__main__":
    unittest.main()
