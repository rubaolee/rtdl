from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5157VectorizedFrontierNearestContinuationTest(unittest.TestCase):
    def test_vectorized_frontier_nearest_preserves_tie_break_and_metadata(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [20, 10, 30],
            "x": [-1.0, 1.0, 4.0],
            "y": [0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100],
            "x": [0.0],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(1, 1, 1),
        )
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=10.0,
            max_inline_points=8,
        )

        nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            executor="numpy",
            return_metadata=True,
        )

        self.assertEqual(nearest["metadata"]["reduction_strategy"], "vectorized_expand_lexsort")
        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [10])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [1.0])

    def test_vectorized_frontier_nearest_keeps_seed_when_frontier_is_pruned(self) -> None:
        import rtdsl as rt

        target_points = {
            "ids": [10, 11],
            "x": [0.0, 10.0],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
        }
        query_points = {
            "ids": [100],
            "x": [0.25],
            "y": [0.0],
            "z": [0.0],
        }
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_points,
            coordinate_fields=("x", "y", "z"),
            grid_shape=(2, 1, 1),
        )
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            query_points,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            radius=0.1,
            current_best_distances=[0.25],
            current_best_item_ids=[10],
            max_inline_points=2,
        )

        nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            current_best_distances=[0.25],
            current_best_item_ids=[10],
            return_metadata=True,
        )

        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [10])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [0.25])
        self.assertEqual(nearest["metadata"]["candidate_distance_evaluations"], 0)

    def test_vectorized_continuation_profile_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_vectorized_continuation_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5157 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        cases = {case["case"]: case for case in payload["cases"]}
        self.assertEqual(set(cases), {"sample256", "sample1024"})
        sample1024 = cases["sample1024"]
        self.assertTrue(sample1024["matched"])
        self.assertEqual(sample1024["rtdl"]["validation_mode"], "author-only")
        self.assertIsNone(sample1024["rtdl"]["rtdl_matches_exact_reference"])
        self.assertLess(
            sample1024["rtdl"]["directed_a_to_b"]["phase_timings_sec_median"]["nearest_continuation"],
            sample1024["rtdl"]["directed_a_to_b"]["phase_timings_sec_median"]["initial_state_seed"],
        )
        self.assertLess(
            sample1024["rtdl"]["directed_b_to_a"]["phase_timings_sec_median"]["nearest_continuation"],
            sample1024["rtdl"]["directed_b_to_a"]["phase_timings_sec_median"]["initial_state_seed"],
        )


if __name__ == "__main__":
    unittest.main()
