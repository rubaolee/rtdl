from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _fixture_3d():
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
    return query_points, grid


class Goal5145DimensionGenericCellMbrFrontdoorTest(unittest.TestCase):
    def test_dimension_generic_frontdoor_matches_manual_3d_composition(self) -> None:
        import rtdsl as rt

        query_points, grid = _fixture_3d()
        composed = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            current_best_distances=[1.0, 4.5, float("inf")],
            current_best_item_ids=[10, 11, -1],
            max_inline_points=2,
            return_metadata=True,
        )
        candidates = rt.radius_cell_mbr_candidate_rows_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
        )
        frontier = rt.nearest_state_frontier_from_cell_candidates_numpy_columns(
            candidates["columns"],
            grid["cell_columns"],
            query_point_ids=query_points["ids"],
            current_best_distances=[1.0, 4.5, float("inf")],
            current_best_item_ids=[10, 11, -1],
            max_inline_points=2,
        )
        reference = rt.cell_mbr_frontiers_to_row_table_numpy_columns(frontier)

        for name, expected in reference["columns"].items():
            self.assertEqual(composed["row_table"]["columns"][name].tolist(), expected.tolist())
        self.assertEqual(composed["metadata"]["contract"], "generic_cell_mbr_nearest_frontier_reference")
        self.assertEqual(composed["metadata"]["coordinate_fields"], ("x", "y", "z"))
        self.assertEqual(composed["metadata"]["candidate_row_count"], 6)
        self.assertEqual(composed["metadata"]["row_count"], 6)
        self.assertEqual(composed["metadata"]["native_abi_contract"], rt.CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT)
        self.assertEqual(composed["metadata"]["app_semantics"], "none")
        self.assertFalse(composed["metadata"]["native_backend_complete"])

    def test_dimension_generic_frontdoor_outputs_expected_3d_kinds(self) -> None:
        import rtdsl as rt

        query_points, grid = _fixture_3d()
        result = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            current_best_distances=[1.0, 4.5, float("inf")],
            current_best_item_ids=[10, 11, -1],
            max_inline_points=2,
        )
        columns = result["row_table"]["columns"]

        self.assertEqual(columns["query_point_ids"].tolist(), [100, 101, 102, 102, 100, 101])
        self.assertEqual(columns["cell_ids"].tolist(), [0, 0, 0, 1, 1, 1])
        self.assertEqual(columns["frontier_kind_codes"].tolist(), [1, 1, 1, 2, 3, 3])
        self.assertEqual(columns["point_counts"].tolist(), [2, 2, 2, 3, 3, 3])

    def test_dimension_generic_frontdoor_fails_closed_on_output_capacity(self) -> None:
        import rtdsl as rt

        query_points, grid = _fixture_3d()
        with self.assertRaisesRegex(RuntimeError, "failure_mode=fail_closed_overflow"):
            rt.cell_mbr_nearest_frontier_numpy_columns(
                query_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                radius=20.0,
                current_best_distances=[1.0, 4.5, float("inf")],
                current_best_item_ids=[10, 11, -1],
                max_inline_points=2,
                row_capacity=5,
            )

    def test_dimension_generic_frontdoor_is_public_and_app_neutral(self) -> None:
        import rtdsl as rt

        self.assertIn("cell_mbr_nearest_frontier_numpy_columns", rt.__all__)
        plan = rt.plan_cell_mbr_traversal_lowering("dimension_generic")
        self.assertTrue(plan["executable"])
        self.assertFalse(plan["native_backend_complete"])
        self.assertEqual(plan["status"], "implemented_dimension_generic_reference_row_table")

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        end = source.index("def _frontier_table_piece")
        generic_window = source[start:end].lower()
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
