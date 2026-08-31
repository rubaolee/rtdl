from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5152NearestCellMbrSeedPruningTest(unittest.TestCase):
    def test_nearest_cell_seed_is_public_app_neutral_and_valid_upper_bound(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 11, 12, 13],
            "x": [0.0, 0.25, 10.0, 10.25],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101],
            "x": [0.1, 10.2],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        self.assertEqual(seed["metadata"]["contract"], "generic_seed_nearest_witness_from_nearest_cell_mbr")
        self.assertEqual(seed["metadata"]["app_semantics"], "none")
        self.assertEqual(seed["columns"]["nearest_item_ids"].tolist(), [10, 13])
        self.assertAlmostEqual(seed["columns"]["nearest_distances"][0], 0.1)
        self.assertAlmostEqual(seed["columns"]["nearest_distances"][1], 0.05)
        self.assertIn("seed_nearest_witness_from_nearest_cell_mbr_numpy_columns", rt.__all__)

    def test_seed_reduces_frontier_continuation_work_without_changing_distance(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 11, 12, 13],
            "x": [0.0, 0.25, 10.0, 10.25],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101],
            "x": [0.1, 10.2],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        unseeded_frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            max_inline_points=2,
        )
        unseeded = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            unseeded_frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )
        seeded_radius = float(seed["columns"]["nearest_distances"].max()) + 1.0e-12
        seeded_frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=seeded_radius,
            current_best_distances=seed["columns"]["nearest_distances"],
            current_best_item_ids=seed["columns"]["nearest_item_ids"],
            max_inline_points=2,
        )
        seeded = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            seeded_frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            current_best_distances=seed["columns"]["nearest_distances"],
            current_best_item_ids=seed["columns"]["nearest_item_ids"],
            return_metadata=True,
        )

        self.assertEqual(
            seeded["columns"]["nearest_distances"].tolist(),
            unseeded["columns"]["nearest_distances"].tolist(),
        )
        self.assertLess(
            seeded["metadata"]["candidate_distance_evaluations"],
            unseeded["metadata"]["candidate_distance_evaluations"],
        )

    def test_seed_helper_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def seed_nearest_witness_from_nearest_cell_mbr_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()
        self.assertIn("generic_seed_nearest_witness_from_nearest_cell_mbr", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
