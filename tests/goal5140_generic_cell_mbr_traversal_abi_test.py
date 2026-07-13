from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _frontier_fixture():
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
    return rt.nearest_state_frontier_from_cell_candidates_numpy_columns(
        candidates["columns"],
        grid["cell_columns"],
        query_point_ids=demand_points["ids"],
        current_best_distances=[1.0, 4.5, float("inf")],
        current_best_item_ids=[10, 11, -1],
        max_inline_points=2,
    )


class Goal5140GenericCellMbrTraversalAbiTest(unittest.TestCase):
    def test_native_abi_contract_is_app_neutral_and_non_executable(self) -> None:
        import rtdsl as rt

        contract = rt.validate_cell_mbr_traversal_native_abi_contract()

        self.assertEqual(contract["contract"], "generic_cell_mbr_nearest_frontier_native_abi_v1")
        self.assertEqual(contract["python_reference_contract"], "generic_nearest_state_cell_frontier")
        self.assertFalse(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertEqual(tuple(contract["supported_dimensions"]), (2, 3))
        self.assertEqual(tuple(contract["output_row_schema"]), rt.CELL_MBR_TRAVERSAL_ROW_SCHEMA)
        self.assertEqual(contract["frontier_kind_codes"], rt.CELL_MBR_FRONTIER_KIND_CODES)
        self.assertEqual(contract["overflow_policy"], "fail_closed_no_partial_rows")

        contract_text = str(contract).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec"):
            self.assertNotIn(forbidden, contract_text)

    def test_frontier_row_table_matches_native_abi_schema(self) -> None:
        import rtdsl as rt

        frontier = _frontier_fixture()
        table = rt.cell_mbr_frontiers_to_row_table_numpy_columns(
            frontier,
            return_metadata=True,
        )
        columns = table["columns"]

        self.assertEqual(table["metadata"]["contract"], "generic_cell_mbr_nearest_frontier_row_table")
        self.assertEqual(table["metadata"]["native_abi_contract"], rt.CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT)
        self.assertEqual(tuple(table["metadata"]["row_schema"]), rt.CELL_MBR_TRAVERSAL_ROW_SCHEMA)
        self.assertEqual(columns["frontier_kind_codes"].tolist(), [1, 1, 1, 2, 3, 3])
        self.assertEqual(columns["query_point_ids"].tolist(), [100, 101, 102, 102, 100, 101])
        self.assertEqual(columns["cell_ids"].tolist(), [0, 0, 0, 1, 1, 1])
        self.assertEqual(columns["point_counts"].tolist(), [2, 2, 2, 3, 3, 3])

    def test_lowering_plan_separates_reference_from_future_native_targets(self) -> None:
        import rtdsl as rt

        reference = rt.plan_cell_mbr_traversal_lowering("numpy")
        self.assertTrue(reference["executable"])
        self.assertEqual(reference["status"], "implemented_numpy_reference_frontier_split")

        optix = rt.plan_cell_mbr_traversal_lowering("optix")
        self.assertFalse(optix["executable"])
        self.assertEqual(optix["status"], "specified_native_abi_no_backend_implementation")
        self.assertFalse(optix["native_engine_app_specific"])

        with self.assertRaisesRegex(ValueError, "cell-MBR traversal lowering target"):
            rt.plan_cell_mbr_traversal_lowering("xhd")

    def test_native_abi_surface_is_public_and_app_neutral(self) -> None:
        import rtdsl as rt

        for name in (
            "cell_mbr_traversal_native_abi_contract",
            "validate_cell_mbr_traversal_native_abi_contract",
            "plan_cell_mbr_traversal_lowering",
            "cell_mbr_frontiers_to_row_table_numpy_columns",
        ):
            self.assertIn(name, rt.__all__)

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def cell_mbr_frontiers_to_row_table_numpy_columns")
        end = source.index("def directed_hausdorff_2d_numpy_columns")
        generic_window = source[start:end].lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
