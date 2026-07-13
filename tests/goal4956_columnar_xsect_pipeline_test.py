from __future__ import annotations

import importlib.util
from pathlib import Path
import types
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


def _load_app_module():
    spec = importlib.util.spec_from_file_location("rayjoin_section57_columnar_binary_test_module", APP)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal4956ColumnarXsectPipelineTest(unittest.TestCase):
    def test_columnar_sort_uses_non_overflowing_distance_and_stable_tie(self) -> None:
        module = _load_app_module()
        edge_id = 7
        columns = {
            "eid0": np.asarray([edge_id, edge_id, edge_id], dtype=np.int64),
            "eid1": np.asarray([95930, 95927, 95898], dtype=np.int64),
            "scaled_x": np.asarray(
                [-36584167492323, -36804867847227, -36919864748650],
                dtype=np.int64,
            ),
            "scaled_y": np.asarray(
                [13210982077858, 13211217488978, 13211340150989],
                dtype=np.int64,
            ),
        }
        dataset = types.SimpleNamespace(
            edge_count=8,
            x0=np.zeros(8, dtype=np.float64),
            y0=np.zeros(8, dtype=np.float64),
        )
        scale_bounds = (-1.0, 1.0, -1.0, 1.0)
        module.base._FMA_LOOKED_UP = True
        module.base._FMA = None
        rx_scale, ry_scale, deltax, deltay, *_ = module.base._rayjoin_scaling_constants(scale_bounds)
        start_sx = int(module.base._scale_array([dataset.x0[edge_id]], rx_scale, deltax)[0])
        start_sy = int(module.base._scale_array([dataset.y0[edge_id]], ry_scale, deltay)[0])

        expected = sorted(
            range(3),
            key=lambda index: (
                (int(columns["scaled_x"][index]) - start_sx) ** 2
                + (int(columns["scaled_y"][index]) - start_sy) ** 2,
                int(columns["eid1"][index]),
                index,
            ),
        )
        result = module.sort_xsect_indices_for_map(columns, dataset, 0, scale_bounds)

        self.assertEqual(expected, result["order"].tolist())
        self.assertEqual([0, 1, 2], expected)

    def test_public_app_file_has_no_internal_goal_or_history_dependency(self) -> None:
        source = APP.read_text(encoding="utf-8").lower()
        self.assertNotIn("history/internal_docs", source)
        self.assertNotIn("goal4956", source)
        self.assertNotIn("goal4955", source)

    def test_prepared_lsi_replay_is_explicit_hot_path_mode(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("def run_lsi_prepared_replay", source)
        self.assertIn("--prepared-lsi-replay", source)
        self.assertIn("lsi_prepare_workspace_sec", source)
        self.assertIn("query.prepare_workspace", source)
        self.assertIn("lsi_prepared_replay_rows_sec", source)
        self.assertIn("lsi_public_rows_sec", source)

    def test_compiled_group_builder_matches_python_reference_without_xsects(self) -> None:
        module = _load_app_module()
        if not module.NUMBA_AVAILABLE:
            self.skipTest("Numba is not available in this local Python environment")
        dataset = types.SimpleNamespace(
            chain_count=1,
            edge_count=2,
            chain_offsets=np.asarray([0], dtype=np.int64),
            chain_point_counts=np.asarray([3], dtype=np.int64),
            chain_left_faces=np.asarray([11], dtype=np.uint32),
            chain_right_faces=np.asarray([13], dtype=np.uint32),
            point_x=np.asarray([0.0, 1.0, 2.0], dtype=np.float64),
            point_y=np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
        )
        sorted_view = {
            "order": np.asarray([], dtype=np.int64),
            "run_start": np.asarray([-1, -1], dtype=np.int64),
            "run_end": np.asarray([-1, -1], dtype=np.int64),
            "edge_ids": np.asarray([], dtype=np.int64),
        }
        columns = {
            "display_x": np.asarray([], dtype=np.float64),
            "display_y": np.asarray([], dtype=np.float64),
        }
        point_faces = [np.asarray([5, 5, 7], dtype=np.uint32), np.asarray([5, 5, 7], dtype=np.uint32)]
        midpoint_faces = [np.asarray([], dtype=np.uint32), np.asarray([], dtype=np.uint32)]

        reference, reference_stats = module.build_projected_descriptor_carrier_columnar(
            (dataset, dataset),
            columns,
            (sorted_view, sorted_view),
            point_faces,
            midpoint_faces,
        )
        compiled, compiled_stats = module.build_projected_descriptor_carrier_columnar_compiled(
            (dataset, dataset),
            columns,
            (sorted_view, sorted_view),
            point_faces,
            midpoint_faces,
        )

        for field in ("group_length", "label_a", "label_b"):
            np.testing.assert_array_equal(reference[field], compiled[field])
        self.assertEqual(reference_stats["group_count"], compiled_stats["group_count"])
        self.assertEqual(reference_stats["point_row_count"], compiled_stats["point_row_count"])
        self.assertEqual(reference_stats["skipped_group_count"], compiled_stats["skipped_group_count"])


if __name__ == "__main__":
    unittest.main()
