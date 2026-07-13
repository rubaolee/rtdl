from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _coverage_candidate_fixture():
    import rtdsl as rt

    facility_points = {
        "ids": [10, 11, 12, 13, 14],
        "x": [0.0, 1.0, 10.0, 12.0, 12.5],
        "y": [0.0, 1.0, 0.0, 0.0, 0.0],
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
        radius=20.0,
    )
    return demand_points, grid, candidates


class Goal5139GenericNearestStateFrontierApiTest(unittest.TestCase):
    def test_nearest_state_frontier_splits_inline_offload_and_pruned_cells(self) -> None:
        import rtdsl as rt

        demand_points, grid, candidates = _coverage_candidate_fixture()
        frontier = rt.nearest_state_frontier_from_cell_candidates_numpy_columns(
            candidates["columns"],
            grid["cell_columns"],
            query_point_ids=demand_points["ids"],
            current_best_distances=[1.0, 4.5, float("inf")],
            current_best_item_ids=[10, 11, -1],
            max_inline_points=2,
            return_metadata=True,
        )

        self.assertEqual(frontier["metadata"]["contract"], "generic_nearest_state_cell_frontier")
        self.assertEqual(frontier["metadata"]["app_semantics"], "none")
        self.assertEqual(frontier["metadata"]["inline_frontier_row_count"], 3)
        self.assertEqual(frontier["metadata"]["offload_frontier_row_count"], 1)
        self.assertEqual(frontier["metadata"]["pruned_frontier_row_count"], 2)
        self.assertEqual(frontier["nearest_state"]["query_point_ids"].tolist(), [100, 101, 102])
        self.assertEqual(frontier["nearest_state"]["current_best_item_ids"].tolist(), [10, 11, -1])

        inline = frontier["inline_frontier"]
        self.assertEqual(inline["query_point_ids"].tolist(), [100, 101, 102])
        self.assertEqual(inline["cell_ids"].tolist(), [0, 0, 0])
        self.assertEqual(inline["point_counts"].tolist(), [2, 2, 2])

        offload = frontier["offload_frontier"]
        self.assertEqual(offload["query_point_ids"].tolist(), [102])
        self.assertEqual(offload["cell_ids"].tolist(), [1])
        self.assertEqual(offload["point_counts"].tolist(), [3])
        self.assertEqual(offload["min_distances"].tolist(), [0.0])

        pruned = frontier["pruned_frontier"]
        self.assertEqual(pruned["query_point_ids"].tolist(), [100, 101])
        self.assertEqual(pruned["cell_ids"].tolist(), [1, 1])

    def test_nearest_state_frontier_surface_is_app_neutral_and_public(self) -> None:
        import rtdsl as rt

        self.assertIn("nearest_state_frontier_from_cell_candidates_numpy_columns", rt.__all__)

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def nearest_state_frontier_from_cell_candidates_numpy_columns")
        end = source.index("def directed_hausdorff_2d_numpy_columns")
        generic_window = source[start:end].lower()

        self.assertIn("generic_nearest_state_cell_frontier", generic_window)
        self.assertIn("offload_frontier", generic_window)
        self.assertNotIn("xhd", generic_window)
        self.assertNotIn("x-hd", generic_window)
        self.assertNotIn("hausdorff", generic_window)
        self.assertNotIn("paper", generic_window)
        self.assertNotIn("hd_exec", generic_window)

    def test_nearest_state_frontier_fails_closed_on_bad_contracts(self) -> None:
        import rtdsl as rt

        demand_points, grid, candidates = _coverage_candidate_fixture()
        with self.assertRaisesRegex(ValueError, "max_inline_points must be non-negative"):
            rt.nearest_state_frontier_from_cell_candidates_numpy_columns(
                candidates["columns"],
                grid["cell_columns"],
                query_point_ids=demand_points["ids"],
                max_inline_points=-1,
            )
        bad_columns = dict(candidates["columns"])
        bad_columns["query_point_ids"] = [999] * len(candidates["columns"]["query_row_ids"])
        with self.assertRaisesRegex(ValueError, "candidate query_point_ids must match"):
            rt.nearest_state_frontier_from_cell_candidates_numpy_columns(
                bad_columns,
                grid["cell_columns"],
                query_point_ids=demand_points["ids"],
                max_inline_points=2,
            )


if __name__ == "__main__":
    unittest.main()
