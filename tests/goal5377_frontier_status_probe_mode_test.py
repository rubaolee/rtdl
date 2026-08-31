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
        "ids": np.asarray([10, 11], dtype=np.int64),
        "x": np.asarray([0.0, 2.0], dtype=np.float64),
        "y": np.asarray([0.0, 0.0], dtype=np.float64),
        "z": np.asarray([0.0, 0.0], dtype=np.float64),
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


def _native_with_probe_metadata(row_capacity: int):
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
            "source_ids": np.asarray([10, 11], dtype=np.int64),
            "nearest_distances": np.asarray([0.0, 1.0], dtype=np.float64),
            "nearest_item_ids": np.asarray([200, 201], dtype=np.int64),
        },
        "valid_count": 0,
        "attempted_count": 5,
        "row_capacity": int(row_capacity),
        "sort_rows": False,
        "frontier_row_order": "native_unsorted",
        "inline_nearest": True,
        "native_generic_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6",
        "frontier_status_probe_mode": "heavy-before-inline-prune",
        "frontier_status_probe_mode_code": 1,
        "frontier_status_probe_contract": (
            "generic_heavy_cell_status_classification_before_inline_prune_probe"
        ),
        "native_memory_telemetry_collected": True,
        "native_memory_telemetry": {
            "schema": "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v3",
            "raw_frontier_kind2_rows": 5,
        },
    }


class Goal5377FrontierStatusProbeModeTest(unittest.TestCase):
    def test_native_v6_declares_generic_status_probe_mode(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(
            encoding="utf-8"
        )

        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6", api)
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6", prelude)
        self.assertIn("frontier_status_probe_mode", workloads)
        self.assertIn("params.frontier_status_probe_mode != 1u", workloads)
        self.assertIn(
            "params.frontier_status_probe_mode == 1u && cell.point_count > params.max_inline_points",
            workloads,
        )

        kernel_start = workloads.index("static const char* kCellMbrFrontier3DKernelSrc")
        kernel_end = workloads.index("static void ensure_cell_mbr_frontier_3d_pipeline")
        kernel = workloads[kernel_start:kernel_end].lower()
        for forbidden in ("xhd", "x-hd", "paper", "author"):
            self.assertNotIn(forbidden, kernel)

    def test_runtime_requires_v6_for_non_default_status_probe(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        fn_start = runtime.index("def collect_cell_mbr_nearest_frontier_3d_optix")
        fn_end = runtime.index("@dataclass(frozen=True)", fn_start)
        window = runtime[fn_start:fn_end]

        self.assertIn("frontier_status_probe_mode", window)
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6", window)
        self.assertIn("heavy-before-inline-prune", window)
        self.assertIn("generic_heavy_cell_status_classification_before_inline_prune_probe", window)
        self.assertIn("frontier_status_probe_mode requires inline_nearest=True", window)

    def test_partner_frontdoor_passes_status_probe_mode_and_metadata(self) -> None:
        import rtdsl as rt

        query_points, target_points, cell_columns = _fixture()
        calls: list[dict[str, object]] = []

        def fake_native(**kwargs):
            calls.append(kwargs)
            return _native_with_probe_metadata(kwargs["row_capacity"])

        with patch(
            "rtdsl.optix_runtime.collect_cell_mbr_nearest_frontier_3d_optix",
            side_effect=fake_native,
        ):
            result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
                query_points,
                cell_columns,
                target_point_columns=target_points,
                radius=2.0,
                current_best_distances=np.full(2, np.inf, dtype=np.float64),
                current_best_item_ids=np.full(2, -1, dtype=np.int64),
                max_inline_points=8,
                emit_pruned_rows=False,
                sort_rows=False,
                inline_nearest=True,
                frontier_status_probe_mode="heavy-before-inline-prune",
                return_split_frontiers=False,
                return_metadata=True,
            )

        self.assertEqual("heavy-before-inline-prune", calls[0]["frontier_status_probe_mode"])
        self.assertEqual(
            "heavy-before-inline-prune",
            result["metadata"]["frontier_status_probe_mode"],
        )
        self.assertEqual(
            "generic_heavy_cell_status_classification_before_inline_prune_probe",
            result["metadata"]["frontier_status_probe_contract"],
        )
        self.assertEqual(
            "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6",
            result["metadata"]["native_generic_symbol"],
        )

    def test_xhd_kind_count_probe_exposes_bounded_mode_without_owning_semantics(self) -> None:
        script = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "scripts"
            / "run_xhd_cell_mbr_frontier_kind_count_probe.py"
        ).read_text(encoding="utf-8")
        self.assertIn("--frontier-status-probe-mode", script)
        self.assertIn("frontier_status_probe_mode=args.frontier_status_probe_mode", script)
        self.assertIn('"frontier_status_probe_mode"', script)
        self.assertIn('"explicit_lb_support_claimed": False', script)
        self.assertIn('"row_count_parity_claimed": False', script)


if __name__ == "__main__":
    unittest.main()
