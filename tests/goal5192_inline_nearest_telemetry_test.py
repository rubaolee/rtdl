from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_cell_mbr_frontier_route_gate.py"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5192InlineNearestTelemetryTest(unittest.TestCase):
    def test_collect_inline_stats_requires_inline_nearest(self) -> None:
        from rtdsl.optix_runtime import collect_cell_mbr_nearest_frontier_3d_optix

        with self.assertRaisesRegex(ValueError, "collect_inline_stats requires inline_nearest=True"):
            collect_cell_mbr_nearest_frontier_3d_optix(
                query_coords=np.asarray([[0.0, 0.0, 0.0]], dtype=np.float64),
                query_point_ids=np.asarray([1], dtype=np.int64),
                cell_ids=np.asarray([10], dtype=np.int64),
                point_begin_offsets=np.asarray([0], dtype=np.uint64),
                point_counts=np.asarray([1], dtype=np.uint64),
                cell_mbr_min=np.asarray([[0.0, 0.0, 0.0]], dtype=np.float64),
                cell_mbr_max=np.asarray([[0.0, 0.0, 0.0]], dtype=np.float64),
                radius=1.0,
                current_best_distances=np.asarray([1.0], dtype=np.float64),
                current_best_item_ids=np.asarray([100], dtype=np.int64),
                max_inline_points=1,
                row_capacity=0,
                inline_nearest=False,
                collect_inline_stats=True,
            )

    def test_runner_accepts_collect_inline_stats_route_argument(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("--collect-inline-stats", source)
        self.assertIn("collect_inline_stats=bool", source)
        self.assertIn("inline_point_evaluation_count", source)
        self.assertIn("inline_cell_hit_count", source)

    def test_complete_state_metadata_is_compatible_with_telemetry_fields(self) -> None:
        runner = _load_runner()

        nearest = runner._nearest_from_complete_frontier_state(
            {"ids": [1]},
            {
                "query_point_ids": [1],
                "current_best_distances": [0.0],
                "current_best_item_ids": [2],
            },
            executor_requested="auto",
        )

        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_from_complete_frontier_state")
        self.assertEqual(nearest["metadata"]["candidate_distance_evaluations"], 0)


if __name__ == "__main__":
    unittest.main()
