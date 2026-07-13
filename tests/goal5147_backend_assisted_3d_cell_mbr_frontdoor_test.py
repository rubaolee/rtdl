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


class Goal5147BackendAssisted3DCellMbrFrontdoorTest(unittest.TestCase):
    def test_backend_assisted_3d_cpu_matches_dimension_generic_oracle(self) -> None:
        import rtdsl as rt

        query_points, grid = _fixture_3d()
        assisted = rt.cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns(
            query_points,
            grid["cell_columns"],
            radius=20.0,
            current_best_distances=[1.0, 4.5, float("inf")],
            current_best_item_ids=[10, 11, -1],
            max_inline_points=2,
            backend="cpu",
            return_metadata=True,
        )
        oracle = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            current_best_distances=[1.0, 4.5, float("inf")],
            current_best_item_ids=[10, 11, -1],
            max_inline_points=2,
        )

        for name, expected in oracle["row_table"]["columns"].items():
            self.assertEqual(assisted["row_table"]["columns"][name].tolist(), expected.tolist())
        self.assertEqual(assisted["metadata"]["contract"], "generic_cell_mbr_nearest_frontier_aabb_membership_3d")
        self.assertEqual(assisted["metadata"]["traversal_backend"], "cpu")
        self.assertEqual(assisted["metadata"]["broadphase_contract"], "generic_expanded_aabb_point_membership_rows_3d_v1")
        self.assertEqual(assisted["metadata"]["row_count"], 6)
        self.assertEqual(assisted["metadata"]["app_semantics"], "none")
        self.assertFalse(assisted["metadata"]["native_backend_complete"])

    def test_backend_assisted_3d_filters_expanded_aabb_corner_false_positive(self) -> None:
        import rtdsl as rt

        query_points = {"ids": [100], "x": [2.3], "y": [2.3], "z": [2.3]}
        cell_columns = {
            "cell_ids": [7],
            "point_begin_offsets": [0],
            "point_counts": [1],
            "min_x": [0.0],
            "min_y": [0.0],
            "min_z": [0.0],
            "max_x": [1.0],
            "max_y": [1.0],
            "max_z": [1.0],
        }
        assisted = rt.cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns(
            query_points,
            cell_columns,
            radius=1.5,
            max_inline_points=1,
            backend="cpu",
            return_metadata=True,
        )

        self.assertEqual(assisted["metadata"]["broadphase_row_count"], 1)
        self.assertEqual(assisted["metadata"]["exact_candidate_row_count"], 0)
        self.assertEqual(assisted["metadata"]["row_count"], 0)

    def test_backend_assisted_3d_fails_closed_on_output_capacity(self) -> None:
        import rtdsl as rt

        query_points, grid = _fixture_3d()
        with self.assertRaisesRegex(RuntimeError, "failure_mode=fail_closed_overflow"):
            rt.cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns(
                query_points,
                grid["cell_columns"],
                radius=20.0,
                current_best_distances=[1.0, 4.5, float("inf")],
                current_best_item_ids=[10, 11, -1],
                max_inline_points=2,
                row_capacity=5,
                backend="cpu",
            )

    def test_backend_assisted_3d_is_public_and_app_neutral(self) -> None:
        import rtdsl as rt

        self.assertIn("cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns", rt.__all__)
        plan = rt.plan_cell_mbr_traversal_lowering("aabb_membership_3d")
        self.assertTrue(plan["executable"])
        self.assertFalse(plan["native_backend_complete"])
        self.assertEqual(plan["status"], "implemented_backend_assisted_3d_frontdoor")
        self.assertIn("optix", plan["backend_options"])
        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns")
        end = source.index("def cell_mbr_nearest_frontier_numpy_columns")
        generic_window = source[start:end].lower()
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
