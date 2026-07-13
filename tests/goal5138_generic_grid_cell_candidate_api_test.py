from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5138GenericGridCellCandidateApiTest(unittest.TestCase):
    def test_point_grid_cell_mbrs_emit_generic_tight_cell_descriptors(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 11, 12, 13],
            "x": [0.0, 1.0, 10.0, 12.0],
            "y": [0.0, 1.0, 0.0, 0.0],
        }

        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y"),
            grid_shape=(2, 1),
            return_metadata=True,
        )
        cells = grid["cell_columns"]

        self.assertEqual(grid["metadata"]["contract"], "generic_point_grid_cell_mbr_columns")
        self.assertEqual(grid["metadata"]["app_semantics"], "none")
        self.assertEqual(cells["cell_ids"].tolist(), [0, 1])
        self.assertEqual(cells["original_cell_ids"].tolist(), [0, 1])
        self.assertEqual(cells["point_counts"].tolist(), [2, 2])
        self.assertEqual(cells["point_begin_offsets"].tolist(), [0, 2])
        self.assertEqual(cells["point_ids"].tolist(), [10, 11, 12, 13])
        self.assertEqual(cells["min_x"].tolist(), [0.0, 10.0])
        self.assertEqual(cells["max_x"].tolist(), [1.0, 12.0])
        self.assertEqual(cells["min_y"].tolist(), [0.0, 0.0])
        self.assertEqual(cells["max_y"].tolist(), [1.0, 0.0])

    def test_radius_cell_mbr_candidate_rows_support_non_xhd_coverage_queries(self) -> None:
        import rtdsl as rt

        facility_points = {
            "ids": [10, 11, 12, 13],
            "x": [0.0, 1.0, 10.0, 12.0],
            "y": [0.0, 1.0, 0.0, 0.0],
        }
        demand_points = {
            "ids": [100, 101, 102],
            "x": [0.5, 5.0, 11.0],
            "y": [0.0, 0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            facility_points,
            coordinate_fields=("x", "y"),
            grid_shape=(2, 1),
        )
        candidates = rt.radius_cell_mbr_candidate_rows_numpy_columns(
            demand_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y"),
            radius=1.5,
            return_metadata=True,
        )
        rows = candidates["candidate_rows"]
        columns = candidates["columns"]

        self.assertEqual(candidates["metadata"]["contract"], "generic_radius_cell_mbr_candidate_rows")
        self.assertEqual(candidates["metadata"]["app_semantics"], "none")
        self.assertEqual(rows.query_ids.tolist(), [0, 2])
        self.assertEqual(rows.primitive_ids.tolist(), [0, 1])
        self.assertEqual(rows.values.tolist(), [0.0, 0.0])
        self.assertEqual(columns["query_point_ids"].tolist(), [100, 102])
        self.assertEqual(columns["cell_ids"].tolist(), [0, 1])

    def test_grid_cell_candidate_surface_is_app_neutral_and_public(self) -> None:
        import rtdsl as rt

        self.assertIn("point_grid_cell_mbrs_numpy_columns", rt.__all__)
        self.assertIn("radius_cell_mbr_candidate_rows_numpy_columns", rt.__all__)

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def point_grid_cell_mbrs_numpy_columns")
        end = source.index("def directed_hausdorff_2d_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("generic_point_grid_cell_mbr_columns", generic_window)
        self.assertIn("generic_radius_cell_mbr_candidate_rows", generic_window)
        self.assertNotIn("xhd", generic_window)
        self.assertNotIn("x-hd", generic_window)
        self.assertNotIn("hausdorff", generic_window)
        self.assertNotIn("paper", generic_window)
        self.assertNotIn("hd_exec", generic_window)

    def test_grid_cell_candidate_api_fails_closed_on_bad_contracts(self) -> None:
        import rtdsl as rt

        points = {"ids": [1], "x": [0.0], "y": [0.0]}
        with self.assertRaisesRegex(ValueError, "grid_shape length must match"):
            rt.point_grid_cell_mbrs_numpy_columns(
                points,
                coordinate_fields=("x", "y"),
                grid_shape=(2,),
            )
        with self.assertRaisesRegex(ValueError, "radius must be non-negative"):
            rt.radius_cell_mbr_candidate_rows_numpy_columns(
                points,
                {
                    "cell_ids": [0],
                    "min_x": [0.0],
                    "max_x": [1.0],
                    "min_y": [0.0],
                    "max_y": [1.0],
                },
                coordinate_fields=("x", "y"),
                radius=-1.0,
            )


if __name__ == "__main__":
    unittest.main()
