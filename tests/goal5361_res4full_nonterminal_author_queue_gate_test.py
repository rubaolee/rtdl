from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5361_res4full_nonterminal_author_queue_gate.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5361_res4full_nonterminal_author_queue_gate.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5361_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5361Res4FullNonterminalAuthorQueueGateTest(unittest.TestCase):
    def test_res4full_wrapper_matches_nonterminal_author_queue_trace(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual("res4full_nonterminal_author_like_queue_trace_matches", payload["status"])
        self.assertTrue(payload["comparison"]["matched"])
        self.assertLessEqual(payload["comparison"]["hd_abs_diff"], payload["comparison"]["tolerance"])
        self.assertEqual(["translate_each_input_to_min_bound"], payload["preprocessing_contract"]["required"])
        self.assertEqual(
            ["translate_each_input_to_min_bound"],
            payload["preprocessing_contract"]["wrapper_reference_preprocessing"],
        )

        rows = payload["comparison"]["wrapper_rows"]
        self.assertEqual(2, len(rows))
        self.assertEqual(5205, rows[0]["NumInputPoints"])
        self.assertEqual(4, rows[0]["NumOutputPoints"])
        self.assertEqual(4, rows[1]["NumInputPoints"])
        self.assertEqual(0, rows[1]["NumOutputPoints"])
        self.assertTrue(payload["route"]["uses_radius_growth_step"])
        self.assertTrue(payload["route"]["has_nonterminal_iteration"])
        self.assertFalse(payload["route"]["author_tune_radius_supported"])

    def test_saved_artifact_preserves_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertIn("explicit_tune_radius_still_unmapped", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)

    def test_frontier_nearest_allow_missing_is_explicit_and_app_neutral(self) -> None:
        sys.path.insert(0, str(ROOT / "src"))
        import rtdsl as rt

        target = {
            "ids": [10, 11],
            "x": [0.0, 5.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        query = {
            "ids": [100, 101],
            "x": [0.1, 4.9],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=10.0,
            max_inline_points=1,
        )
        table_columns = frontier["row_table"]["columns"]
        mask = np.asarray(table_columns["query_row_ids"], dtype=np.int64) == 0
        partial_table = {"columns": {key: np.asarray(value)[mask] for key, value in table_columns.items()}}

        with self.assertRaisesRegex(ValueError, "did not cover every query row"):
            rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
                query,
                target,
                grid["cell_columns"],
                partial_table,
                coordinate_fields=("x", "y", "z"),
            )

        partial = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query,
            target,
            grid["cell_columns"],
            partial_table,
            coordinate_fields=("x", "y", "z"),
            allow_missing=True,
            return_metadata=True,
        )
        self.assertFalse(partial["metadata"]["coverage_complete"])
        self.assertEqual(1, partial["metadata"]["missing_query_count"])
        self.assertTrue(partial["metadata"]["allow_missing"])
        self.assertEqual("none", partial["metadata"]["app_semantics"])
        self.assertEqual([10, -1], partial["columns"]["nearest_item_ids"].tolist())


if __name__ == "__main__":
    unittest.main()
