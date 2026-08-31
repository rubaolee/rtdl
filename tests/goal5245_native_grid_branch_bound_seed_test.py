from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))


class Goal5245NativeGridBranchBoundSeedTest(unittest.TestCase):
    def test_branch_bound_seed_can_select_native_cuda_executor(self) -> None:
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

        def fake_native(**kwargs):
            self.assertEqual(kwargs["query_coords"].shape, (1, 3))
            self.assertEqual(kwargs["target_coords"].shape, (3, 3))
            self.assertEqual(kwargs["grid_shape"].tolist(), [3, 1, 1])
            self.assertEqual(kwargs["dense_cell_positions"].shape, (3,))
            return {
                "columns": {
                    "nearest_item_ids": np.asarray([20], dtype=np.int64),
                    "nearest_distances": np.asarray([0.2], dtype=np.float64),
                    "seed_cell_ids": np.asarray([1], dtype=np.int64),
                },
                "metadata": {
                    "contract": "generic_seed_nearest_witness_from_grid_branch_bound",
                    "executor": "native_cuda",
                    "native_generic_symbol": "rtdl_optix_seed_nearest_witness_grid_branch_bound_3d",
                    "grid_cell_probes": 3,
                    "max_grid_cell_probes_per_query": 3,
                    "scanned_cell_count": 1,
                    "max_scanned_cells_per_query": 1,
                    "candidate_distance_evaluations": 1,
                    "max_shells_per_query": 1,
                    "max_seed_cell_point_count": 1,
                    "seed_quality": "exact_nearest_witness_under_grid_cell_branch_bound",
                    "app_semantics": "none",
                    "native_phase_timings_collected": True,
                    "native_phase_timings": {"kernel_sec": 0.001},
                },
            }

        with patch("rtdsl.optix_runtime.seed_nearest_witness_grid_branch_bound_3d_cuda", fake_native):
            seed = rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                executor="native_cuda",
                return_metadata=True,
            )

        self.assertEqual(seed["columns"]["nearest_item_ids"].tolist(), [20])
        self.assertAlmostEqual(float(seed["columns"]["nearest_distances"][0]), 0.2)
        self.assertEqual(seed["metadata"]["executor"], "native_cuda")
        self.assertEqual(seed["metadata"]["executor_requested"], "native_cuda")
        self.assertEqual(
            seed["metadata"]["native_generic_symbol"],
            "rtdl_optix_seed_nearest_witness_grid_branch_bound_3d",
        )
        self.assertEqual(seed["metadata"]["app_semantics"], "none")

    def test_branch_bound_seed_rejects_unknown_executor(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10],
            "x": [0.0],
            "y": [0.0],
            "z": [0.0],
        }
        query_points = {
            "ids": [100],
            "x": [0.0],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(1, 1, 1),
        )

        with self.assertRaisesRegex(ValueError, "executor"):
            rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                coordinate_fields=("x", "y", "z"),
                executor="xhd",
            )

    def test_branch_bound_seed_native_symbol_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        native_source = (root.parent / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("rtdl_optix_seed_nearest_witness_grid_branch_bound_3d", native_source)
        window_start = native_source.index("rtdl_optix_seed_nearest_witness_grid_branch_bound_3d")
        window = native_source[window_start : window_start + 2500].lower()
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, window)

    def test_exact_branch_bound_seed_can_skip_frontier(self) -> None:
        from run_xhd_cell_mbr_frontier_route_gate import _directed_cell_mbr_route

        result = _directed_cell_mbr_route(
            np.asarray([[0.1, 0.0, 0.0], [3.8, 0.0, 0.0]], dtype=np.float64),
            np.asarray([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0]], dtype=np.float64),
            label="unit",
            backend="numpy",
            grid_shape=(2, 1, 1),
            radius=None,
            fallback_radius=10.0,
            max_inline_points=8,
            initial_state="grid-branch-bound",
            seed_cell_budget=4,
            local_grid_seed_executor="auto",
            grid_branch_bound_seed_executor="auto",
            frontier_nearest_executor="auto",
            frontier_row_order="native",
            frontier_inline_nearest=False,
            skip_frontier_if_exact_seed=True,
        )

        self.assertTrue(result["exact_seed_frontier_skipped"])
        self.assertEqual(result["frontier_row_count"], 0)
        self.assertTrue(result["complete_frontier_state_passthrough"])
        self.assertEqual(result["frontier_contract"], "generic_exact_seed_frontier_skip")
        self.assertAlmostEqual(float(result["distance"]), 0.2, places=12)


if __name__ == "__main__":
    unittest.main()
