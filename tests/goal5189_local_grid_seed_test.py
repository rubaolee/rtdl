from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _numba_available() -> bool:
    try:
        import numba  # noqa: F401
    except Exception:
        return False
    return True


class Goal5189LocalGridSeedTest(unittest.TestCase):
    def test_grid_descriptors_carry_app_neutral_grid_domain_metadata(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20],
            "x": [0.0, 10.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(3, 1, 1),
            return_metadata=True,
        )
        cells = grid["cell_columns"]

        self.assertEqual(cells["grid_shape"].tolist(), [3, 1, 1])
        self.assertEqual(cells["grid_lower_bounds"].tolist(), [0.0, 0.0, 0.0])
        self.assertEqual(cells["grid_upper_bounds"].tolist(), [10.0, 0.0, 0.0])
        self.assertEqual(grid["metadata"]["cell_mbr_contract"], "tight_mbr_over_points_in_cell")

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_local_grid_seed_is_valid_upper_bound_from_nearby_occupied_cell(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20],
            "x": [0.0, 10.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        query_points = {
            "ids": [100],
            "x": [5.0],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(3, 1, 1),
        )

        seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        self.assertEqual(seed["metadata"]["contract"], "generic_seed_nearest_witness_from_local_grid_cell")
        self.assertEqual(seed["metadata"]["app_semantics"], "none")
        self.assertEqual(seed["metadata"]["seed_quality"], "valid_upper_bound_not_nearest_cell_mbr")
        self.assertEqual(seed["metadata"]["executor"], "numba_parallel")
        self.assertIn(seed["columns"]["nearest_item_ids"].tolist()[0], [10, 20])
        self.assertAlmostEqual(seed["columns"]["nearest_distances"][0], 5.0)
        self.assertGreaterEqual(seed["metadata"]["grid_cell_probes"], 1)
        self.assertIn("seed_nearest_witness_from_local_grid_cell_numpy_columns", rt.__all__)

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_local_grid_seed_refines_to_same_result_as_unseeded_frontier(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20, 30, 40],
            "x": [0.0, 0.2, 10.0, 10.2],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101],
            "x": [0.1, 10.1],
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

        seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )
        seeded_frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=float(seed["columns"]["nearest_distances"].max()) + 1.0e-12,
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
            seeded["columns"]["nearest_item_ids"].tolist(),
            unseeded["columns"]["nearest_item_ids"].tolist(),
        )
        self.assertEqual(
            seeded["columns"]["nearest_distances"].tolist(),
            unseeded["columns"]["nearest_distances"].tolist(),
        )

    def test_local_grid_seed_fails_closed_without_grid_metadata(self) -> None:
        import rtdsl as rt

        points = {"ids": [1], "x": [0.0], "y": [0.0], "z": [0.0]}
        with self.assertRaisesRegex(KeyError, "grid_shape"):
            rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
                points,
                points,
                {
                    "cell_ids": [0],
                    "original_cell_ids": [0],
                    "point_begin_offsets": [0],
                    "point_counts": [1],
                    "point_row_indices": [0],
                },
                coordinate_fields=("x", "y", "z"),
            )

    def test_local_grid_seed_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def seed_nearest_witness_from_local_grid_cell_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("generic_seed_nearest_witness_from_local_grid_cell", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
