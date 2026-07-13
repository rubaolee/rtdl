from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5194PayloadCurrentBestPruningTest(unittest.TestCase):
    def test_native_anyhit_classifies_cells_against_payload_current_best(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        start = workloads.index("extern \"C\" __global__ void __anyhit__cell_mbr_frontier3d_emit")
        end = workloads.index("static void ensure_cell_mbr_frontier_3d_pipeline")
        anyhit = workloads[start:end]

        self.assertIn("inline_state_available", anyhit)
        self.assertIn("optixGetPayload_1", anyhit)
        self.assertIn("optixGetPayload_2", anyhit)
        self.assertIn("inline_state_available ? (min_sq > best) : (min_dist >= query.current_best_distance)", anyhit)

    def test_python_metadata_exposes_payload_current_best_pruning_strategy(self) -> None:
        import rtdsl as rt

        query_points = {
            "ids": [100],
            "x": [0.0],
            "y": [0.0],
            "z": [0.0],
        }
        target_points = {
            "ids": [200],
            "x": [0.25],
            "y": [0.0],
            "z": [0.0],
        }
        cell_columns = {
            "cell_ids": np.asarray([10], dtype=np.int64),
            "point_begin_offsets": np.asarray([0], dtype=np.uint64),
            "point_counts": np.asarray([1], dtype=np.uint64),
            "point_row_indices": np.asarray([0], dtype=np.uint64),
            "min_x": np.asarray([0.25], dtype=np.float64),
            "min_y": np.asarray([0.0], dtype=np.float64),
            "min_z": np.asarray([0.0], dtype=np.float64),
            "max_x": np.asarray([0.25], dtype=np.float64),
            "max_y": np.asarray([0.0], dtype=np.float64),
            "max_z": np.asarray([0.0], dtype=np.float64),
        }

        def fake_native(**kwargs):
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
                    "source_ids": np.asarray([100], dtype=np.int64),
                    "nearest_distances": np.asarray([0.25], dtype=np.float64),
                    "nearest_item_ids": np.asarray([200], dtype=np.int64),
                },
                "valid_count": 0,
                "attempted_count": 0,
                "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3",
                "inline_stats_collected": False,
                "inline_cell_hit_count": None,
                "inline_point_evaluation_count": None,
            }

        with patch("rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix", side_effect=fake_native):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                target_point_columns=target_points,
                radius=1.0,
                current_best_distances=[1.0],
                current_best_item_ids=[200],
                max_inline_points=1,
                emit_pruned_rows=False,
                inline_nearest=True,
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual(
            result["metadata"]["inline_nearest_pruning"],
            "payload_current_best_min_cell_distance_gt_best",
        )
        self.assertEqual(
            result["metadata"]["inline_nearest_contract"],
            "native_exact_inline_cell_point_nearest_for_inline_frontier_rows",
        )
        self.assertEqual(result["metadata"]["app_semantics"], "none")


if __name__ == "__main__":
    unittest.main()
