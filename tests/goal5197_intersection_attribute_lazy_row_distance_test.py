from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5197IntersectionAttributeLazyRowDistanceTest(unittest.TestCase):
    def test_intersection_reports_min_sq_as_attributes_for_anyhit(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        start = workloads.index("extern \"C\" __global__ void __intersection__cell_mbr_frontier3d_exact")
        end = workloads.index("extern \"C\" __global__ void __anyhit__cell_mbr_frontier3d_emit")
        intersection = workloads[start:end]

        self.assertIn("const double min_sq = min_distance_sq(query, cell);", intersection)
        self.assertIn("const u64 min_bits = (u64)__double_as_longlong(min_sq);", intersection)
        self.assertIn("optixReportIntersection(", intersection)
        self.assertIn("(unsigned int)(min_bits & 0xffffffffULL)", intersection)
        self.assertIn("(unsigned int)((min_bits >> 32) & 0xffffffffULL)", intersection)

    def test_anyhit_reuses_min_sq_attribute_and_computes_row_distances_lazily(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        start = workloads.index("extern \"C\" __global__ void __anyhit__cell_mbr_frontier3d_emit")
        end = workloads.index("static void ensure_cell_mbr_frontier_3d_pipeline")
        anyhit = workloads[start:end]

        self.assertIn("optixGetAttribute_0", anyhit)
        self.assertIn("optixGetAttribute_1", anyhit)
        self.assertIn("__longlong_as_double((long long)min_bits_attr)", anyhit)
        self.assertNotIn("const double min_sq = min_distance_sq(query, cell);", anyhit)

        max_distance_index = anyhit.index("const double max_sq = max_distance_sq(query, cell);")
        row_output_index = anyhit.index("const u64 row_index = atomicAdd(params.hit_count, 1ULL);")
        inline_scan_index = anyhit.index("if (kind == 1 && params.inline_nearest != 0u)")
        self.assertGreater(max_distance_index, inline_scan_index)
        self.assertLess(max_distance_index, row_output_index)
        self.assertIn("const double row_min_dist = sqrt(min_sq);", anyhit)

    def test_adapter_exposes_attribute_and_lazy_row_distance_metadata(self) -> None:
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
                "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4",
                "inline_stats_collected": False,
                "inline_cell_hit_count": None,
                "inline_point_evaluation_count": None,
                "intersection_pruning": "payload_current_best_before_report_intersection",
                "intersection_attribute_min_distance_sq": "reported_by_intersection_reused_by_anyhit",
                "anyhit_row_distance_computation": "lazy_row_output_only",
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
            result["metadata"]["intersection_attribute_min_distance_sq"],
            "reported_by_intersection_reused_by_anyhit",
        )
        self.assertEqual(result["metadata"]["anyhit_row_distance_computation"], "lazy_row_output_only")
        self.assertEqual(result["metadata"]["app_semantics"], "none")


if __name__ == "__main__":
    unittest.main()
