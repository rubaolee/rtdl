from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _point_columns(ids, coords):
    matrix = np.asarray(coords, dtype=np.float64)
    return {
        "ids": np.asarray(ids, dtype=np.int64),
        "x": matrix[:, 0],
        "y": matrix[:, 1],
        "z": matrix[:, 2],
        "coordinate_matrix": matrix,
        "coordinate_matrix_fields": ("x", "y", "z"),
    }


class Goal5202PackedCoordinateMatrixReuseTest(unittest.TestCase):
    def test_local_grid_seed_reuses_supplied_coordinate_matrix(self) -> None:
        import rtdsl as rt

        target_points = _point_columns(
            [10, 20, 30],
            [
                (0.0, 0.0, 0.0),
                (5.0, 0.0, 0.0),
                (10.0, 0.0, 0.0),
            ],
        )
        query_points = _point_columns(
            [100, 101],
            [
                (0.1, 0.0, 0.0),
                (9.9, 0.0, 0.0),
            ],
        )
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(8, 2, 2),
        )
        native_result = {
            "columns": {
                "nearest_item_ids": np.asarray([10, 30], dtype=np.int64),
                "nearest_distances": np.asarray([0.1, 0.1], dtype=np.float64),
                "seed_cell_ids": np.asarray([0, 28], dtype=np.int64),
            },
            "metadata": {
                "adapter": "seed_nearest_witness_local_grid_cell_3d_cuda",
                "partner": "optix_cuda",
                "contract": "generic_seed_nearest_witness_from_local_grid_cell",
                "native_generic_symbol": "rtdl_optix_seed_nearest_witness_local_grid_3d",
                "executor": "native_cuda",
                "app_semantics": "none",
            },
        }

        with patch(
            "rtdsl.optix_runtime.seed_nearest_witness_local_grid_cell_3d_cuda",
            return_value=native_result,
        ) as native_seed:
            seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                executor="native_cuda",
                return_metadata=True,
            )

        kwargs = native_seed.call_args.kwargs
        self.assertIs(kwargs["query_coords"], query_points["coordinate_matrix"])
        self.assertIs(kwargs["target_coords"], target_points["coordinate_matrix"])
        self.assertTrue(seed["metadata"]["query_coordinate_matrix_reused"])
        self.assertTrue(seed["metadata"]["target_coordinate_matrix_reused"])
        self.assertEqual(seed["metadata"]["app_semantics"], "none")

    def test_stale_coordinate_matrix_fails_closed(self) -> None:
        import rtdsl as rt

        target_points = _point_columns(
            [10],
            [(0.0, 0.0, 0.0)],
        )
        query_points = _point_columns(
            [100],
            [(0.0, 0.0, 0.0)],
        )
        query_points["coordinate_matrix"] = np.asarray([[999.0, 0.0, 0.0]], dtype=np.float64)
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 2, 2),
        )

        with self.assertRaisesRegex(ValueError, "coordinate_matrix does not match"):
            rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                executor="native_cuda",
            )

    def test_xhd_route_columns_create_matrix_views(self) -> None:
        route_path = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_cell_mbr_frontier_route_gate.py"
        spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate_goal5202", route_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        columns = module._columns_3d([(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)])
        matrix = columns["coordinate_matrix"]
        self.assertEqual(matrix.shape, (2, 3))
        self.assertEqual(tuple(columns["coordinate_matrix_fields"]), ("x", "y", "z"))
        self.assertTrue(np.shares_memory(matrix[:, 0], columns["x"]))
        self.assertTrue(np.shares_memory(matrix[:, 1], columns["y"]))
        self.assertTrue(np.shares_memory(matrix[:, 2], columns["z"]))

    def test_generic_source_windows_are_app_neutral(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def _point_matrix_for_fields")
        end = source.index("def pairwise_l2_distance_candidate_rows_numpy_columns")
        window = source[start:end].lower()
        self.assertIn("coordinate_matrix", window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, window)


if __name__ == "__main__":
    unittest.main()
