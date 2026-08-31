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


class Goal5190GridBranchBoundSeedTest(unittest.TestCase):
    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_branch_bound_seed_finds_exact_nearest_witness(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20, 30],
            "x": [0.0, 4.9, 10.0],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100],
            "x": [5.1],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(3, 1, 1),
        )

        seed = rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        self.assertEqual(seed["metadata"]["contract"], "generic_seed_nearest_witness_from_grid_branch_bound")
        self.assertEqual(seed["metadata"]["app_semantics"], "none")
        self.assertEqual(seed["metadata"]["seed_quality"], "exact_nearest_witness_under_grid_cell_branch_bound")
        self.assertEqual(seed["metadata"]["executor"], "numba_parallel")
        self.assertEqual(seed["columns"]["nearest_item_ids"].tolist(), [20])
        self.assertAlmostEqual(seed["columns"]["nearest_distances"][0], 0.2)
        self.assertGreaterEqual(seed["metadata"]["grid_cell_probes"], 1)
        self.assertGreaterEqual(seed["metadata"]["scanned_cell_count"], 1)
        self.assertIn("seed_nearest_witness_from_grid_branch_bound_numpy_columns", rt.__all__)

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_branch_bound_seed_is_no_looser_than_local_grid_seed(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20, 30, 40],
            "x": [0.0, 3.0, 6.0, 9.0],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101, 102],
            "x": [1.6, 4.6, 7.6],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(4, 1, 1),
        )

        local_seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )
        branch_seed = rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        for branch_distance, local_distance in zip(
            branch_seed["columns"]["nearest_distances"],
            local_seed["columns"]["nearest_distances"],
        ):
            self.assertLessEqual(float(branch_distance), float(local_distance) + 1.0e-12)

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_branch_bound_seed_refines_to_same_result_as_unseeded_frontier(self) -> None:
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

        seed = rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns(
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

    def test_branch_bound_seed_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def seed_nearest_witness_from_grid_branch_bound_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("generic_seed_nearest_witness_from_grid_branch_bound", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
