from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


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
    return query_points, grid["cell_columns"]


class Goal5148Native3DCellMbrFrontierTest(unittest.TestCase):
    def test_native_symbol_declared_and_app_neutral(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d", prelude)
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d", api)
        self.assertIn("collect_cell_mbr_nearest_frontier_3d_optix", workloads)
        self.assertIn("g_cell_mbr_frontier3d", core)
        start = workloads.index("static const char* kCellMbrFrontier3DKernelSrc")
        end = workloads.index("static void ensure_pack_triangle2d_device_columns_kernel")
        native_window = workloads[start:end].lower()
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, native_window)

    def test_public_plan_and_exports_are_bounded_native_3d(self) -> None:
        import rtdsl as rt

        self.assertIn("collect_cell_mbr_nearest_frontier_3d_optix", rt.__all__)
        self.assertIn("cell_mbr_nearest_frontier_native_3d_optix_columns", rt.__all__)
        plan = rt.plan_cell_mbr_traversal_lowering("optix_3d")
        self.assertTrue(plan["executable"])
        self.assertEqual(plan["status"], "implemented_bounded_native_3d_optix_backend")
        self.assertFalse(plan["native_backend_complete"])
        self.assertFalse(plan["native_engine_app_specific"])
        self.assertEqual(plan["native_symbol"], "rtdl_optix_collect_cell_mbr_nearest_frontier_3d")

    def test_python_adapter_wires_generic_arrays_to_native_rows(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture_3d()
        current_best_distances = [1.0, 4.5, float("inf")]
        current_best_item_ids = [10, 11, -1]
        oracle = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            cell_columns,
            coordinate_fields=("x", "y", "z"),
            radius=20.0,
            current_best_distances=current_best_distances,
            current_best_item_ids=current_best_item_ids,
            max_inline_points=2,
        )
        captured: dict[str, object] = {}

        def fake_native(**kwargs):
            captured.update(kwargs)
            return {
                "columns": {name: values.copy() for name, values in oracle["row_table"]["columns"].items()},
                "valid_count": int(oracle["row_table"]["columns"]["frontier_kind_codes"].size),
                "attempted_count": int(oracle["row_table"]["columns"]["frontier_kind_codes"].size),
                "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d",
            }

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            native = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=20.0,
                current_best_distances=current_best_distances,
                current_best_item_ids=current_best_item_ids,
                max_inline_points=2,
                return_metadata=True,
            )

        self.assertEqual(captured["query_coords"].shape, (3, 3))
        self.assertEqual(captured["cell_mbr_min"].shape[1], 3)
        self.assertEqual(captured["cell_mbr_max"].shape[1], 3)
        self.assertEqual(captured["max_inline_points"], 2)
        self.assertTrue(captured["emit_pruned_rows"])
        self.assertEqual(captured["row_capacity"], 6)
        for name, expected in oracle["row_table"]["columns"].items():
            actual = native["row_table"]["columns"][name]
            if actual.dtype.kind == "f":
                np.testing.assert_allclose(actual, expected)
            else:
                self.assertEqual(actual.tolist(), expected.tolist())
        self.assertEqual(native["metadata"]["contract"], "generic_cell_mbr_nearest_frontier_native_3d_optix")
        self.assertFalse(native["metadata"]["native_backend_complete"])
        self.assertEqual(native["metadata"]["app_semantics"], "none")
        self.assertTrue(native["metadata"]["emit_pruned_rows"])
        self.assertTrue(native["metadata"]["split_frontiers_returned"])

    def test_python_adapter_can_return_row_table_only_for_streaming_consumers(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture_3d()

        def fake_native(**kwargs):
            oracle = rt.cell_mbr_nearest_frontier_numpy_columns(
                query_points,
                cell_columns,
                coordinate_fields=("x", "y", "z"),
                radius=20.0,
                current_best_distances=[1.0, 4.5, float("inf")],
                current_best_item_ids=[10, 11, -1],
                max_inline_points=2,
                return_metadata=True,
            )
            return {
                "columns": {name: values.copy() for name, values in oracle["row_table"]["columns"].items()},
                "valid_count": int(oracle["row_table"]["columns"]["frontier_kind_codes"].size),
                "attempted_count": int(oracle["row_table"]["columns"]["frontier_kind_codes"].size),
                "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d",
            }

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            native = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=20.0,
                current_best_distances=[1.0, 4.5, float("inf")],
                current_best_item_ids=[10, 11, -1],
                max_inline_points=2,
                emit_pruned_rows=False,
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertIn("row_table", native)
        self.assertNotIn("inline_frontier", native)
        self.assertNotIn("offload_frontier", native)
        self.assertNotIn("pruned_frontier", native)
        self.assertFalse(native["metadata"]["emit_pruned_rows"])
        self.assertFalse(native["metadata"]["split_frontiers_returned"])
        self.assertEqual(native["metadata"]["row_table_contract"], "generic_cell_mbr_nearest_frontier_row_table")


if __name__ == "__main__":
    unittest.main()
