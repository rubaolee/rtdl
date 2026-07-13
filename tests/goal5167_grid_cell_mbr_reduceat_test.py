from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _slow_cell_mbr_reference(points, *, coordinate_fields, grid_shape):
    point_ids = np.asarray(points["ids"], dtype=np.int64)
    coordinates = [np.asarray(points[field], dtype=np.float64) for field in coordinate_fields]
    coord_matrix = np.column_stack(coordinates)
    lower_bounds = coord_matrix.min(axis=0)
    upper_bounds = coord_matrix.max(axis=0)
    extents = upper_bounds - lower_bounds

    positions = []
    for axis, axis_values in enumerate(coordinates):
        if extents[axis] == 0.0:
            position = np.zeros(point_ids.size, dtype=np.int64)
        else:
            normalized = (axis_values - lower_bounds[axis]) / extents[axis]
            position = np.floor(normalized * int(grid_shape[axis])).astype(np.int64)
            position = np.clip(position, 0, int(grid_shape[axis]) - 1)
        positions.append(position)

    encoded = positions[0].astype(np.int64, copy=True)
    for axis in range(1, len(positions)):
        encoded = encoded * int(grid_shape[axis]) + positions[axis]

    order = np.lexsort((point_ids, encoded))
    sorted_encoded = encoded[order]
    unique_encoded, begin_offsets, counts = np.unique(
        sorted_encoded,
        return_index=True,
        return_counts=True,
    )

    result = {
        "original_cell_ids": unique_encoded.astype(np.int64),
        "point_begin_offsets": begin_offsets.astype(np.int64),
        "point_counts": counts.astype(np.int64),
        "point_ids": point_ids[order].astype(np.int64),
        "point_row_indices": order.astype(np.int64),
    }
    for axis, field in enumerate(coordinate_fields):
        sorted_axis = coordinates[axis][order]
        mins = []
        maxs = []
        for begin, count in zip(begin_offsets, counts):
            values = sorted_axis[int(begin) : int(begin + count)]
            mins.append(float(values.min()))
            maxs.append(float(values.max()))
        result[f"min_{field}"] = np.asarray(mins, dtype=np.float64)
        result[f"max_{field}"] = np.asarray(maxs, dtype=np.float64)
    return result


class Goal5167GridCellMbrReduceatTest(unittest.TestCase):
    def test_reduceat_grid_cell_mbrs_match_slow_reference_for_sparse_3d_grid(self) -> None:
        import rtdsl as rt

        points = {
            "ids": [30, 10, 20, 40, 50, 60, 70],
            "x": [0.0, 0.1, 0.2, 2.5, 2.8, 5.0, 5.0],
            "y": [0.0, 0.3, 0.1, 1.0, 1.4, 2.0, 2.0],
            "z": [0.0, 0.2, 0.4, 3.0, 3.5, 6.0, 6.0],
        }
        grid_shape = (4, 3, 5)
        coordinate_fields = ("x", "y", "z")

        fast = rt.point_grid_cell_mbrs_numpy_columns(
            points,
            coordinate_fields=coordinate_fields,
            grid_shape=grid_shape,
            return_metadata=True,
        )
        cells = fast["cell_columns"]
        slow = _slow_cell_mbr_reference(
            points,
            coordinate_fields=coordinate_fields,
            grid_shape=grid_shape,
        )

        self.assertEqual(fast["metadata"]["cell_mbr_reduction"], "numpy_reduceat")
        for key in (
            "original_cell_ids",
            "point_begin_offsets",
            "point_counts",
            "point_ids",
            "point_row_indices",
        ):
            np.testing.assert_array_equal(cells[key], slow[key], err_msg=key)
        for field in coordinate_fields:
            np.testing.assert_allclose(cells[f"min_{field}"], slow[f"min_{field}"])
            np.testing.assert_allclose(cells[f"max_{field}"], slow[f"max_{field}"])

    def test_reduceat_grid_cell_mbr_surface_stays_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def point_grid_cell_mbrs_numpy_columns")
        end = source.index("def radius_cell_mbr_candidate_rows_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("numpy_reduceat", generic_window)
        self.assertNotIn("xhd", generic_window)
        self.assertNotIn("x-hd", generic_window)
        self.assertNotIn("hausdorff", generic_window)
        self.assertNotIn("paper", generic_window)
        self.assertNotIn("hd_exec", generic_window)


if __name__ == "__main__":
    unittest.main()
