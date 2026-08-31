from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5244GridCellInputStableOrderTest(unittest.TestCase):
    def test_input_stable_order_preserves_cell_mbrs(self) -> None:
        import rtdsl as rt

        points = {
            "ids": [30, 10, 20, 40],
            "x": [0.0, 1.0, 0.5, 10.0],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        default = rt.point_grid_cell_mbrs_numpy_columns(
            points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
            return_metadata=True,
        )
        stable = rt.point_grid_cell_mbrs_numpy_columns(
            points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
            cell_point_order="input-stable",
            return_metadata=True,
        )

        self.assertEqual(default["metadata"]["cell_point_order"], "point-id")
        self.assertEqual(stable["metadata"]["cell_point_order"], "input-stable")
        self.assertEqual(stable["metadata"]["cell_point_order_contract"], "cell_id_then_input_order")

        for name in (
            "cell_ids",
            "original_cell_ids",
            "point_begin_offsets",
            "point_counts",
            "min_x",
            "max_x",
            "min_y",
            "max_y",
            "min_z",
            "max_z",
        ):
            self.assertEqual(
                default["cell_columns"][name].tolist(),
                stable["cell_columns"][name].tolist(),
            )

        self.assertEqual(default["cell_columns"]["point_ids"].tolist(), [10, 20, 30, 40])
        self.assertEqual(stable["cell_columns"]["point_ids"].tolist(), [30, 10, 20, 40])

    def test_input_stable_order_fails_closed_on_bad_mode(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "cell_point_order"):
            rt.point_grid_cell_mbrs_numpy_columns(
                {"ids": [1], "x": [0.0], "y": [0.0], "z": [0.0]},
                coordinate_fields=("x", "y", "z"),
                grid_shape=(1, 1, 1),
                cell_point_order="xhd-special",
            )


if __name__ == "__main__":
    unittest.main()
