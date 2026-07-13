from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5200NativeLocalGridSeedTest(unittest.TestCase):
    def test_local_grid_seed_can_select_native_cuda_executor(self) -> None:
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
        native_result = {
            "columns": {
                "nearest_item_ids": np.asarray([10, 30], dtype=np.int64),
                "nearest_distances": np.asarray([0.1, 0.1], dtype=np.float64),
                "seed_cell_ids": np.asarray([0, 28], dtype=np.int64),
            },
            "metadata": {
                "adapter": "seed_nearest_witness_local_grid_cell_3d_cuda",
                "partner": "optix_cuda",
                "contract": "generic_seed_nearest_witness_from_local_grid_cell",
                "native_generic_symbol": "rtdl_optix_seed_nearest_witness_local_grid_3d",
                "query_count": 2,
                "target_count": 3,
                "cell_count": 3,
                "grid_shape": (8, 2, 2),
                "grid_cell_probes": 2,
                "max_grid_cell_probes_per_query": 1,
                "cell_lookup_strategy": "dense_grid_cell_position_table",
                "dense_lookup_cell_capacity": 32,
                "executor": "native_cuda",
                "cell_selection": "local_grid_first_occupied_shell_min_grid_cell_distance_then_cell_id",
                "seed_point_reduction_strategy": "native_cuda_loop_min_distance_then_item_id",
                "candidate_distance_evaluations": 2,
                "max_seed_cell_point_count": 1,
                "seed_quality": "valid_upper_bound_not_nearest_cell_mbr",
                "app_semantics": "none",
                "native_engine_row_contract": "generic_local_grid_nearest_seed_native_cuda",
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }
        with patch(
            "rtdsl.optix_runtime.seed_nearest_witness_local_grid_cell_3d_cuda",
            return_value=native_result,
        ) as native_seed:
            seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                executor="native_cuda",
                return_metadata=True,
            )

        native_seed.assert_called_once()
        self.assertEqual(seed["columns"]["nearest_item_ids"].tolist(), [10, 30])
        self.assertEqual(seed["metadata"]["executor"], "native_cuda")
        self.assertEqual(seed["metadata"]["executor_requested"], "native_cuda")
        self.assertEqual(seed["metadata"]["native_engine_row_contract"], "generic_local_grid_nearest_seed_native_cuda")
        self.assertEqual(seed["metadata"]["app_semantics"], "none")

    def test_native_cuda_requires_dense_lookup(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 20],
            "x": [0.0, 10.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        query_points = {
            "ids": [100],
            "x": [0.1],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(16, 2, 2),
        )

        with self.assertRaisesRegex(ValueError, "requires dense lookup"):
            rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                dense_lookup_max_cells=0,
                executor="native_cuda",
            )

    def test_native_seed_source_windows_are_app_neutral(self) -> None:
        root = ROOT / "src"
        partner_source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        partner_start = partner_source.index("def seed_nearest_witness_from_local_grid_cell_numpy_columns")
        partner_end = partner_source.index("def seed_nearest_witness_from_grid_branch_bound_numpy_columns")
        partner_window = partner_source[partner_start:partner_end].lower()

        runtime_source = (root / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        runtime_start = runtime_source.index("def seed_nearest_witness_local_grid_cell_3d_cuda")
        runtime_end = runtime_source.index("def _coerce_list")
        runtime_window = runtime_source[runtime_start:runtime_end].lower()

        native_source = (root / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_seed_nearest_witness_local_grid_3d", native_source)
        for window in (partner_window, runtime_window):
            self.assertIn("generic_seed_nearest_witness_from_local_grid_cell", window)
            for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
                self.assertNotIn(forbidden, window)


if __name__ == "__main__":
    unittest.main()
