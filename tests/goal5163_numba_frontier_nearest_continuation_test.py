from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _numba_available() -> bool:
    try:
        import numba  # noqa: F401
    except Exception:
        return False
    return True


class Goal5163NumbaFrontierNearestContinuationTest(unittest.TestCase):
    def _fixture(self):
        import rtdsl as rt

        target_points = {
            "ids": [20, 10, 30, 40],
            "x": [-1.0, 1.0, 4.0, 4.5],
            "y": [0.0, 0.0, 0.0, 0.0],
            "z": [0.0, 0.0, 0.0, 0.0],
        }
        query_points = {
            "ids": [100, 101],
            "x": [0.0, 4.25],
            "y": [0.0, 0.0],
            "z": [0.0, 0.0],
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
            radius=10.0,
            max_inline_points=8,
        )
        return rt, query_points, target_points, grid, frontier

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_numba_frontier_nearest_matches_numpy_and_preserves_tie_breaks(self) -> None:
        rt, query_points, target_points, grid, frontier = self._fixture()

        numpy_nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            executor="numpy",
            return_metadata=True,
        )
        numba_nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            executor="numba",
            return_metadata=True,
        )

        self.assertEqual(numba_nearest["metadata"]["executor"], "numba")
        self.assertEqual(numba_nearest["metadata"]["reduction_strategy"], "numba_loop_min_distance_then_item_id")
        self.assertEqual(
            numba_nearest["columns"]["nearest_item_ids"].tolist(),
            numpy_nearest["columns"]["nearest_item_ids"].tolist(),
        )
        self.assertEqual(
            numba_nearest["columns"]["nearest_distances"].tolist(),
            numpy_nearest["columns"]["nearest_distances"].tolist(),
        )
        self.assertEqual(numba_nearest["columns"]["nearest_item_ids"].tolist(), [10, 30])

    @unittest.skipUnless(_numba_available(), "Numba is not available")
    def test_numba_frontier_nearest_keeps_seed_when_frontier_is_pruned(self) -> None:
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
            executor="numba",
            return_metadata=True,
        )

        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [10])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [0.25])
        self.assertEqual(nearest["metadata"]["candidate_distance_evaluations"], 0)

    def test_auto_executor_keeps_public_contract(self) -> None:
        rt, query_points, target_points, grid, frontier = self._fixture()

        nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            query_points,
            target_points,
            grid["cell_columns"],
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            executor="auto",
            return_metadata=True,
        )

        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_from_cell_mbr_frontier")
        self.assertEqual(nearest["metadata"]["app_semantics"], "none")
        self.assertIn(nearest["metadata"]["executor"], ("numpy", "numba", "numba_parallel"))
        self.assertFalse(nearest["metadata"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(nearest["metadata"]["whole_app_speedup_claim_authorized"])

    def test_invalid_executor_fails_closed(self) -> None:
        rt, query_points, target_points, grid, frontier = self._fixture()

        with self.assertRaises(ValueError):
            rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
                query_points,
                target_points,
                grid["cell_columns"],
                frontier["row_table"],
                coordinate_fields=("x", "y", "z"),
                executor="xhd",
            )

    def test_frontier_nearest_source_window_is_app_neutral(self) -> None:
        import rtdsl as rt

        root = Path(rt.__file__).resolve().parents[1]
        source = (root / "rtdsl" / "partner_continuations.py").read_text(encoding="utf-8")
        start = source.index("def nearest_witness_from_cell_mbr_frontier_numpy_columns")
        end = source.index("def seed_nearest_witness_from_nearest_cell_mbr_numpy_columns")
        generic_window = source[start:end].lower()
        self.assertIn("executor", generic_window)
        self.assertIn("numba_loop_min_distance_then_item_id", generic_window)
        for forbidden in ("x" + "hd", "x-" + "hd", "haus" + "dorff", "pa" + "per", "hd_" + "exec"):
            self.assertNotIn(forbidden, generic_window)

    def test_numba_frontier_artifact_preserves_boundaries_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample2048_numba_continuation_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5163 POD artifact not generated yet")

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(payload["phase_policy"]["ratios_authorized"])
        self.assertFalse(payload["performance_claim_authorized"])
        sample2048 = {case["case"]: case for case in payload["cases"]}["sample2048"]
        self.assertTrue(sample2048["matched"])
        self.assertEqual(sample2048["rtdl"]["validation_mode"], "author-only")
        for direction in ("directed_a_to_b", "directed_b_to_a"):
            self.assertLess(
                sample2048["rtdl"][direction]["phase_timings_sec_median"]["nearest_continuation"],
                0.005,
            )


if __name__ == "__main__":
    unittest.main()
