from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))


class Goal5246NativeGridCellMbrBuilderTest(unittest.TestCase):
    def test_native_grid_builder_wrapper_preserves_generic_contract(self) -> None:
        import rtdsl as rt

        points = {
            "ids": [20, 10, 30],
            "x": [1.0, 0.0, 3.0],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }

        def fake_native(**kwargs):
            self.assertEqual(kwargs["coords"].shape, (3, 3))
            self.assertEqual(kwargs["point_ids"].tolist(), [20, 10, 30])
            self.assertEqual(tuple(kwargs["grid_shape"].tolist()), (2, 1, 1))
            self.assertEqual(kwargs["cell_point_order"], "point-id")
            return {
                "cell_columns": {
                    "cell_ids": np.asarray([0, 1], dtype=np.int64),
                    "original_cell_ids": np.asarray([0, 1], dtype=np.int64),
                    "point_begin_offsets": np.asarray([0, 2], dtype=np.int64),
                    "point_counts": np.asarray([2, 1], dtype=np.int64),
                    "point_ids": np.asarray([10, 20, 30], dtype=np.int64),
                    "point_row_indices": np.asarray([1, 0, 2], dtype=np.int64),
                    "grid_shape": np.asarray([2, 1, 1], dtype=np.int64),
                    "grid_lower_bounds": np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
                    "grid_upper_bounds": np.asarray([3.0, 0.0, 0.0], dtype=np.float64),
                    "min_x": np.asarray([0.0, 3.0], dtype=np.float64),
                    "min_y": np.asarray([0.0, 0.0], dtype=np.float64),
                    "min_z": np.asarray([0.0, 0.0], dtype=np.float64),
                    "max_x": np.asarray([1.0, 3.0], dtype=np.float64),
                    "max_y": np.asarray([0.0, 0.0], dtype=np.float64),
                    "max_z": np.asarray([0.0, 0.0], dtype=np.float64),
                },
                "metadata": {
                    "adapter": "point_grid_cell_mbrs_3d_cuda",
                    "partner": "native_cuda_thrust",
                    "contract": "generic_point_grid_cell_mbr_columns",
                    "coordinate_fields": ("x", "y", "z"),
                    "grid_shape": (2, 1, 1),
                    "point_count": 3,
                    "cell_count": 2,
                    "cell_id_contract": "compact_zero_based_with_original_cell_ids",
                    "cell_mbr_contract": "tight_mbr_over_points_in_cell",
                    "cell_mbr_reduction": "native_cuda_thrust_reduce_by_key",
                    "cell_point_order": "point-id",
                    "cell_point_order_contract": "cell_id_then_point_id",
                    "native_generic_symbol": "rtdl_cuda_point_grid_cell_mbrs_3d",
                    "app_semantics": "none",
                    "native_engine_row_contract": "native_cuda_generic_point_grid_cell_mbrs_3d",
                    "rt_core_speedup_claim_authorized": False,
                    "whole_app_speedup_claim_authorized": False,
                },
            }

        with patch("rtdsl.optix_runtime.point_grid_cell_mbrs_3d_cuda", fake_native):
            grid = rt.point_grid_cell_mbrs_native_3d_cuda_columns(
                points,
                coordinate_fields=("x", "y", "z"),
                grid_shape=(2, 1, 1),
                return_metadata=True,
            )

        self.assertEqual(grid["cell_columns"]["point_ids"].tolist(), [10, 20, 30])
        self.assertEqual(grid["metadata"]["contract"], "generic_point_grid_cell_mbr_columns")
        self.assertEqual(grid["metadata"]["adapter"], "point_grid_cell_mbrs_native_3d_cuda_columns")
        self.assertEqual(grid["metadata"]["app_semantics"], "none")
        self.assertFalse(grid["metadata"]["rt_core_speedup_claim_authorized"])

    def test_route_accepts_native_grid_cell_builder_option(self) -> None:
        from run_xhd_cell_mbr_frontier_route_gate import build_summary

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input1 = tmp_path / "a.wkt"
            input2 = tmp_path / "b.wkt"
            input1.write_text("POINT (0 0 0)\nPOINT (1 0 0)\n", encoding="utf-8")
            input2.write_text("POINT (0.1 0 0)\nPOINT (1.5 0 0)\n", encoding="utf-8")

            class Args:
                n_dims = 3
                input_type = "wkt"
                normalize_each_input_to_author_unit_box = False
                author_float32_normalization = False
                translate_each_input_to_min_bound = False
                backend = "numpy"
                grid_shape = "2,1,1"
                radius = None
                max_inline_points = 64
                initial_state = "none"
                seed_cell_budget = 4
                frontier_nearest_executor = "auto"
                local_grid_seed_executor = "auto"
                grid_branch_bound_seed_executor = "auto"
                frontier_row_order = "native"
                cell_order = "native"
                grid_cell_point_order = "point-id"
                grid_cell_builder = "native_cuda"
                skip_frontier_if_exact_seed = False
                frontier_inline_nearest = False
                global_bound_early_break = False
                collect_inline_stats = False
                collect_frontier_native_phase_timings = False
                frontier_row_capacity = None
                direction_mode = "directed-a-to-b"
                validation_mode = "none"
                author_json = None
                tolerance = 1e-6

            Args.input1 = str(input1)
            Args.input2 = str(input2)

            def fake_grid(*args, **kwargs):
                import rtdsl as rt

                self.assertEqual(kwargs["grid_shape"], (2, 1, 1))
                return rt.point_grid_cell_mbrs_numpy_columns(*args, **kwargs)

            with patch("rtdsl.point_grid_cell_mbrs_native_3d_cuda_columns", fake_grid):
                summary = build_summary(Args())

        route = summary["rtdl_route"]["directed_a_to_b"]
        self.assertEqual(summary["grid_cell_builder"], "native_cuda")
        self.assertEqual(route["grid_cell_builder_adapter"], "point_grid_cell_mbrs_numpy_columns")

    def test_native_grid_builder_symbol_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        native_source = (root.parent / "src" / "native" / "optix" / "rtdl_optix_cuda_helpers.cu").read_text(
            encoding="utf-8"
        )
        self.assertIn("rtdl_cuda_point_grid_cell_mbrs_3d", native_source)
        window_start = native_source.index("rtdl_cuda_point_grid_cell_mbrs_3d")
        window = native_source[window_start : window_start + 5000].lower()
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, window)


if __name__ == "__main__":
    unittest.main()
