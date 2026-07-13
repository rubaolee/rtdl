from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5149CellMbrFrontierNearestContinuationTest(unittest.TestCase):
    def test_frontier_nearest_witness_supports_non_hausdorff_facility_route(self) -> None:
        import rtdsl as rt

        facilities = {
            "ids": [200, 201, 202, 203],
            "x": [0.0, 2.0, 8.0, 10.0],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        demand = {
            "ids": [100, 101, 102],
            "x": [0.25, 9.0, 11.0],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            facilities,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            demand,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            max_inline_points=2,
        )
        nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            demand,
            facilities,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_from_cell_mbr_frontier")
        self.assertEqual(nearest["metadata"]["app_semantics"], "none")
        self.assertEqual(nearest["columns"]["source_ids"].tolist(), [100, 101, 102])
        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [200, 202, 203])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [0.25, 1.0, 1.0])

    def test_frontier_nearest_witness_matches_pairwise_nearest_on_goal5148_fixture(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 11, 12, 13, 14],
            "x": [0.0, 1.0, 10.0, 12.0, 12.5],
            "y": [0.0, 1.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 2.0, 2.0],
        }
        query_points = {
            "ids": [100, 101, 102],
            "x": [0.5, 5.0, 11.0],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 1.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            max_inline_points=2,
        )
        frontier_nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
        )
        pairwise = rt.pairwise_l2_distance_candidate_rows_numpy_columns(
            query_points,
            target_points,
            coordinate_fields=("x", "y", "z"),
        )
        pairwise_nearest = rt.nearest_witness_numpy_columns(
            pairwise["candidate_rows"],
            pairwise["source_ids"],
        )

        self.assertEqual(
            frontier_nearest["columns"]["nearest_item_ids"].tolist(),
            pairwise_nearest["columns"]["nearest_item_ids"].tolist(),
        )
        self.assertEqual(
            frontier_nearest["columns"]["nearest_distances"].tolist(),
            pairwise_nearest["columns"]["nearest_distances"].tolist(),
        )

    def test_frontier_nearest_witness_surface_is_public_and_app_neutral(self) -> None:
        import rtdsl as rt

        self.assertIn("nearest_witness_from_cell_mbr_frontier_numpy_columns", rt.__all__)
        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def nearest_witness_from_cell_mbr_frontier_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()
        self.assertIn("generic_nearest_witness_from_cell_mbr_frontier", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
