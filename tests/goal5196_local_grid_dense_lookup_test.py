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


class Goal5196LocalGridDenseLookupTest(unittest.TestCase):
    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_local_grid_seed_uses_dense_lookup_by_default(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20, 30],
            "x": [0.0, 5.0, 10.0],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101],
            "x": [0.1, 9.9],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(8, 2, 2),
        )

        seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )

        self.assertEqual(seed["metadata"]["contract"], "generic_seed_nearest_witness_from_local_grid_cell")
        self.assertEqual(seed["metadata"]["cell_lookup_strategy"], "dense_grid_cell_position_table")
        self.assertEqual(seed["metadata"]["dense_lookup_cell_capacity"], 32)
        self.assertEqual(seed["metadata"]["app_semantics"], "none")
        self.assertEqual(seed["columns"]["nearest_item_ids"].tolist(), [10, 30])

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_dense_lookup_matches_binary_search_fallback(self) -> None:
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
            grid_shape=(16, 2, 2),
        )

        dense = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )
        fallback = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            dense_lookup_max_cells=0,
            return_metadata=True,
        )

        self.assertEqual(dense["metadata"]["cell_lookup_strategy"], "dense_grid_cell_position_table")
        self.assertEqual(fallback["metadata"]["cell_lookup_strategy"], "binary_search_original_cell_ids")
        self.assertEqual(dense["columns"]["nearest_item_ids"].tolist(), fallback["columns"]["nearest_item_ids"].tolist())
        self.assertEqual(
            dense["columns"]["nearest_distances"].tolist(),
            fallback["columns"]["nearest_distances"].tolist(),
        )
        self.assertEqual(dense["columns"]["seed_cell_ids"].tolist(), fallback["columns"]["seed_cell_ids"].tolist())

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_dense_lookup_matches_fallback_for_budget_and_branch_bound_seeds(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20, 30, 40, 50],
            "x": [0.0, 0.2, 5.0, 10.0, 10.2],
            "y": [0.0, 0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101, 102],
            "x": [0.1, 5.1, 10.1],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(16, 2, 2),
        )

        for helper, kwargs in (
            (rt.seed_nearest_witness_from_grid_cell_budget_numpy_columns, {"max_scanned_cells_per_query": 2}),
            (rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns, {}),
        ):
            dense = helper(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                return_metadata=True,
                **kwargs,
            )
            fallback = helper(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                dense_lookup_max_cells=0,
                return_metadata=True,
                **kwargs,
            )

            self.assertEqual(dense["metadata"]["cell_lookup_strategy"], "dense_grid_cell_position_table")
            self.assertEqual(fallback["metadata"]["cell_lookup_strategy"], "binary_search_original_cell_ids")
            self.assertEqual(
                dense["columns"]["nearest_item_ids"].tolist(),
                fallback["columns"]["nearest_item_ids"].tolist(),
            )
            self.assertEqual(
                dense["columns"]["nearest_distances"].tolist(),
                fallback["columns"]["nearest_distances"].tolist(),
            )
            self.assertEqual(dense["columns"]["seed_cell_ids"].tolist(), fallback["columns"]["seed_cell_ids"].tolist())

    def test_local_grid_dense_lookup_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def seed_nearest_witness_from_local_grid_cell_numpy_columns")
        end = source.index("def seed_nearest_witness_from_grid_branch_bound_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("dense_grid_cell_position_table", generic_window)
        self.assertIn("binary_search_original_cell_ids", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
