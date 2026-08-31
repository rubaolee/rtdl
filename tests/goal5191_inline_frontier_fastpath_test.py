from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


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


class Goal5191InlineFrontierFastpathTest(unittest.TestCase):
    def test_complete_frontier_state_passthrough_produces_nearest_columns(self) -> None:
        runner = _load_runner()

        nearest = runner._nearest_from_complete_frontier_state(
            {"ids": [100, 101]},
            {
                "query_point_ids": [100, 101],
                "current_best_distances": [0.25, 1.5],
                "current_best_item_ids": [200, 201],
            },
            executor_requested="auto",
        )

        self.assertEqual(nearest["columns"]["source_ids"].tolist(), [100, 101])
        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [200, 201])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [0.25, 1.5])
        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_from_complete_frontier_state")
        self.assertEqual(nearest["metadata"]["app_semantics"], "none")
        self.assertEqual(nearest["metadata"]["frontier_row_count"], 0)
        self.assertEqual(nearest["metadata"]["candidate_distance_evaluations"], 0)
        self.assertEqual(nearest["metadata"]["executor"], "complete_frontier_state_passthrough")

    def test_complete_frontier_state_fails_closed_when_witness_missing(self) -> None:
        runner = _load_runner()

        with self.assertRaisesRegex(RuntimeError, "missing nearest witnesses"):
            runner._nearest_from_complete_frontier_state(
                {"ids": [100, 101]},
                {
                    "query_point_ids": [100, 101],
                    "current_best_distances": [0.25, float("inf")],
                    "current_best_item_ids": [200, -1],
                },
                executor_requested="numba_parallel",
            )

    def test_complete_frontier_state_fails_closed_on_source_id_mismatch(self) -> None:
        runner = _load_runner()

        with self.assertRaisesRegex(RuntimeError, "source ids do not match"):
            runner._nearest_from_complete_frontier_state(
                {"ids": [100, 101]},
                {
                    "query_point_ids": [100, 102],
                    "current_best_distances": [0.25, 1.5],
                    "current_best_item_ids": [200, 201],
                },
                executor_requested="auto",
            )

    def test_fastpath_helper_source_window_is_app_neutral(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        start = source.index("def _nearest_from_complete_frontier_state")
        end = source.index("def _directed_cell_mbr_route")
        generic_window = source[start:end].lower()

        self.assertIn("generic_nearest_witness_from_complete_frontier_state", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)


if __name__ == "__main__":
    unittest.main()
