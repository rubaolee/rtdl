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
        "ids": [10, 11, 12],
        "x": [0.0, 1.0, 4.0],
        "y": [0.0, 0.0, 0.0],
        "z": [0.0, 0.0, 0.0],
    }
    query_points = {
        "ids": [100, 101],
        "x": [0.2, 3.8],
        "y": [0.0, 0.0],
        "z": [0.0, 0.0],
    }
    grid = rt.point_grid_cell_mbrs_numpy_columns(
        target_points,
        coordinate_fields=("x", "y", "z"),
        grid_shape=(2, 1, 1),
    )
    return query_points, grid["cell_columns"]


class Goal5201CellMbrFrontierPhaseTimingTest(unittest.TestCase):
    def test_native_phase_timing_flag_reaches_backend_and_metadata(self) -> None:
        import rtdsl as rt

        query_points, cell_columns = _fixture_3d()
        captured: dict[str, object] = {}

        def fake_native(**kwargs):
            captured.update(kwargs)
            oracle = rt.cell_mbr_nearest_frontier_numpy_columns(
                query_points,
                cell_columns,
                coordinate_fields=("x", "y", "z"),
                radius=10.0,
                current_best_distances=[float("inf"), float("inf")],
                current_best_item_ids=[-1, -1],
                max_inline_points=1,
                return_metadata=True,
            )
            return {
                "columns": {name: values.copy() for name, values in oracle["row_table"]["columns"].items()},
                "valid_count": int(oracle["row_table"]["columns"]["frontier_kind_codes"].size),
                "attempted_count": int(oracle["row_table"]["columns"]["frontier_kind_codes"].size),
                "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4",
                "native_phase_timings_collected": True,
                "native_phase_timings": {
                    "total_native_sec": 1.25,
                    "query_pack_sec": 0.01,
                    "cell_pack_aabb_sec": 0.02,
                    "accel_build_sec": 0.30,
                    "device_alloc_upload_sec": 0.04,
                    "optix_launch_sec": 0.80,
                    "nearest_download_sec": 0.03,
                    "stats_download_sec": 0.0,
                    "count_download_sec": 0.01,
                    "row_download_sec": 0.0,
                    "host_sort_pack_sec": 0.04,
                    "attempted_count": 0,
                    "emitted_count": 0,
                    "mode_bits": 1,
                },
            }

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                radius=10.0,
                current_best_distances=[float("inf"), float("inf")],
                current_best_item_ids=[-1, -1],
                max_inline_points=1,
                collect_native_phase_timings=True,
                return_metadata=True,
            )

        self.assertTrue(captured["collect_native_phase_timings"])
        self.assertTrue(result["metadata"]["native_phase_timings_collected"])
        self.assertEqual(result["metadata"]["native_phase_timings"]["optix_launch_sec"], 0.80)
        self.assertEqual(result["metadata"]["native_phase_timings"]["accel_build_sec"], 0.30)

    def test_phase_timing_surface_is_generic_and_app_neutral(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        optix_runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        route_gate = (
            ROOT / "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_phase_timings", workloads)
        self.assertIn("collect_native_phase_timings", optix_runtime)
        self.assertIn("native_phase_timings", optix_runtime)
        self.assertIn("--collect-frontier-native-phase-timings", route_gate)
        self.assertIn("frontier_native_phase_timings", route_gate)

        start = workloads.index("extern \"C\" int rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_phase_timings")
        end = workloads.index("static void reset_segment_pair_phase_timings")
        timing_window = workloads[start:end].lower()
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, timing_window)


if __name__ == "__main__":
    unittest.main()
