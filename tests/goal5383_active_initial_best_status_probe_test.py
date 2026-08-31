from __future__ import annotations

import pathlib
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _fixture():
    query_points = {
        "ids": np.asarray([10], dtype=np.int64),
        "x": np.asarray([0.0], dtype=np.float64),
        "y": np.asarray([0.0], dtype=np.float64),
        "z": np.asarray([0.0], dtype=np.float64),
    }
    target_points = {
        "ids": np.asarray([200, 201, 202], dtype=np.int64),
        "x": np.asarray([0.0, 1.0, 3.0], dtype=np.float64),
        "y": np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
        "z": np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
    }
    cell_columns = {
        "cell_ids": np.asarray([7], dtype=np.int64),
        "min_x": np.asarray([0.0], dtype=np.float64),
        "min_y": np.asarray([0.0], dtype=np.float64),
        "min_z": np.asarray([0.0], dtype=np.float64),
        "max_x": np.asarray([3.0], dtype=np.float64),
        "max_y": np.asarray([0.0], dtype=np.float64),
        "max_z": np.asarray([0.0], dtype=np.float64),
        "point_begin_offsets": np.asarray([0], dtype=np.int64),
        "point_counts": np.asarray([3], dtype=np.int64),
        "point_row_indices": np.asarray([0, 1, 2], dtype=np.int64),
    }
    return query_points, target_points, cell_columns


def _native_with_initial_best_probe_metadata(row_capacity: int):
    return {
        "columns": {
            "frontier_kind_codes": np.asarray([], dtype=np.int64),
            "query_row_ids": np.asarray([], dtype=np.int64),
            "query_point_ids": np.asarray([], dtype=np.int64),
            "cell_ids": np.asarray([], dtype=np.int64),
            "point_begin_offsets": np.asarray([], dtype=np.uint64),
            "point_counts": np.asarray([], dtype=np.uint64),
            "min_distances": np.asarray([], dtype=np.float64),
            "max_distances": np.asarray([], dtype=np.float64),
        },
        "nearest_columns": {
            "source_ids": np.asarray([10], dtype=np.int64),
            "nearest_distances": np.asarray([0.0], dtype=np.float64),
            "nearest_item_ids": np.asarray([200], dtype=np.int64),
        },
        "valid_count": 0,
        "attempted_count": 3,
        "row_capacity": int(row_capacity),
        "sort_rows": False,
        "frontier_row_order": "native_unsorted",
        "inline_nearest": True,
        "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6",
        "frontier_status_probe_mode": "active-initial-best-prune",
        "frontier_status_probe_mode_code": 2,
        "frontier_status_probe_contract": "generic_active_query_initial_best_status_probe",
        "native_memory_telemetry_collected": True,
        "native_memory_telemetry": {
            "schema": "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v3",
            "raw_frontier_kind2_rows": 3,
        },
    }


class Goal5383ActiveInitialBestStatusProbeTest(unittest.TestCase):
    def test_native_kernel_has_initial_best_probe_branch_without_app_identity(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("params.frontier_status_probe_mode == 2u", workloads)
        self.assertIn("use_initial_best_status", workloads)
        self.assertIn("query.current_best_distance", workloads)
        self.assertIn("cell-MBR frontier_status_probe_mode must be 0, 1, or 2", workloads)

        kernel_start = workloads.index("static const char* kCellMbrFrontier3DKernelSrc")
        kernel_end = workloads.index("static void ensure_cell_mbr_frontier_3d_pipeline")
        kernel = workloads[kernel_start:kernel_end].lower()
        for forbidden in ("xhd", "x-hd", "paper", "author", "hd_exec"):
            self.assertNotIn(forbidden, kernel)

    def test_runtime_maps_active_initial_best_probe_to_v6_and_metadata(self) -> None:
        import rtdsl as rt

        query_points, target_points, cell_columns = _fixture()
        calls: list[dict[str, object]] = []

        def fake_native(**kwargs):
            calls.append(kwargs)
            return _native_with_initial_best_probe_metadata(kwargs["row_capacity"])

        with patch(
            "rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix",
            side_effect=fake_native,
        ):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                target_point_columns=target_points,
                radius=4.0,
                current_best_distances=np.asarray([2.0], dtype=np.float64),
                current_best_item_ids=np.asarray([200], dtype=np.int64),
                max_inline_points=2,
                emit_pruned_rows=False,
                sort_rows=False,
                inline_nearest=True,
                frontier_status_probe_mode="active-initial-best-prune",
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual("active-initial-best-prune", calls[0]["frontier_status_probe_mode"])
        metadata = result["metadata"]
        self.assertEqual("active-initial-best-prune", metadata["frontier_status_probe_mode"])
        self.assertEqual(2, metadata["frontier_status_probe_mode_code"])
        self.assertEqual(
            "generic_active_query_initial_best_status_probe",
            metadata["frontier_status_probe_contract"],
        )
        self.assertEqual(
            "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6",
            metadata["native_generic_symbol"],
        )

    def test_xhd_probe_runners_accept_new_mode_without_claiming_lb_support(self) -> None:
        bridge_script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_active_query_frontier_bridge_probe.py"
        ).read_text(encoding="utf-8")
        kind_script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_kind_count_probe.py"
        ).read_text(encoding="utf-8")
        for script in (bridge_script, kind_script):
            self.assertIn("active-initial-best-prune", script)
        self.assertIn("--initial-state", bridge_script)
        self.assertIn("seed_nearest_witness_from_local_grid_cell_numpy_columns", bridge_script)
        self.assertIn("current_best_distances=current_best_distances", bridge_script)
        self.assertIn('"explicit_lb_support_claimed": False', bridge_script)
        self.assertIn('"row_count_parity_claimed": False', bridge_script)


if __name__ == "__main__":
    unittest.main()
