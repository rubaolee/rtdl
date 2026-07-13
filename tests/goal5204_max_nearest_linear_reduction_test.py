from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_xhd_route_module():
    route_path = (
        ROOT
        / "Paper-reproduction-apps"
        / "x-hd-paper"
        / "scripts"
        / "run_xhd_cell_mbr_frontier_route_gate.py"
    )
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate_goal5204", route_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5204MaxNearestLinearReductionTest(unittest.TestCase):
    def test_unique_finite_max_uses_single_candidate_path(self) -> None:
        import rtdsl as rt

        result = rt.max_nearest_distance_witness_numpy_columns(
            {
                "source_ids": np.asarray([10, 11, 12], dtype=np.int64),
                "nearest_item_ids": np.asarray([100, 101, 102], dtype=np.int64),
                "nearest_distances": np.asarray([1.0, 5.0, 3.0], dtype=np.float64),
            },
            return_metadata=True,
        )

        self.assertEqual(result["source_index"], 1)
        self.assertEqual(result["source_id"], 11)
        self.assertEqual(result["item_id"], 101)
        self.assertEqual(result["value"], 5.0)
        self.assertEqual(result["metadata"]["reduction_strategy"], "finite_max_then_tie_lexsort")
        self.assertEqual(result["metadata"]["tie_candidate_count"], 1)
        self.assertEqual(result["metadata"]["app_semantics"], "none")

    def test_tie_break_matches_full_lexsort_semantics(self) -> None:
        import rtdsl as rt

        result = rt.max_nearest_distance_witness_numpy_columns(
            {
                "source_ids": np.asarray([30, 31, 32, 33], dtype=np.int64),
                "nearest_item_ids": np.asarray([9, 3, 2, 1], dtype=np.int64),
                "nearest_distances": np.asarray([7.0, 7.0, 7.0, 4.0], dtype=np.float64),
            },
            group_ids=np.asarray([2, 1, 1, 0], dtype=np.int64),
            return_metadata=True,
        )

        # Old full lexsort key order was: maximum distance, then minimum
        # group id, then minimum item id.
        self.assertEqual(result["source_index"], 1)
        self.assertEqual(result["source_id"], 32)
        self.assertEqual(result["item_id"], 2)
        self.assertEqual(result["value"], 7.0)
        self.assertEqual(result["metadata"]["tie_candidate_count"], 3)

    def test_nonfinite_distances_keep_full_lexsort_fallback(self) -> None:
        import rtdsl as rt

        result = rt.max_nearest_distance_witness_numpy_columns(
            {
                "source_ids": np.asarray([10, 11], dtype=np.int64),
                "nearest_item_ids": np.asarray([100, 101], dtype=np.int64),
                "nearest_distances": np.asarray([np.nan, 5.0], dtype=np.float64),
            },
            return_metadata=True,
        )

        self.assertEqual(result["metadata"]["reduction_strategy"], "full_lexsort_nonfinite_fallback")
        self.assertEqual(result["metadata"]["tie_candidate_count"], 2)

    def test_generic_source_window_is_app_neutral(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def max_nearest_distance_witness_numpy_columns")
        end = source.index("def _normalize_grid_shape")
        window = source[start:end].lower()
        self.assertIn("finite_max_then_tie_lexsort", window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, window)

    def test_xhd_route_surfaces_generic_max_reduction_metadata(self) -> None:
        route = _load_xhd_route_module()
        result = route._directed_cell_mbr_route(
            np.asarray([(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)], dtype=np.float64),
            np.asarray([(0.0, 0.0, 0.0)], dtype=np.float64),
            label="small",
            backend="numpy",
            grid_shape=(2, 2, 2),
            radius=None,
            fallback_radius=3.0,
            max_inline_points=64,
            initial_state="nearest-cell-mbr",
            seed_cell_budget=4,
            local_grid_seed_executor="auto",
            frontier_nearest_executor="auto",
            frontier_row_order="sorted",
            frontier_inline_nearest=False,
        )

        self.assertEqual(result["max_reduction_strategy"], "finite_max_then_tie_lexsort")
        self.assertEqual(result["max_tie_candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
